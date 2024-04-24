import datetime
import json

from fastapi import FastAPI, WebSocket
import cv2
import asyncio

from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from sittube.frame_buffer import FrameBuffer
from sittube.settings import Settings

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app_settings = Settings()

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

frame_buffer = FrameBuffer(app_settings.frame_buffer_size)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.websocket("/video")
async def video_endpoint(websocket: WebSocket):
    global frame_buffer
    await websocket.accept()
    cap = cv2.VideoCapture(str(app_settings.video_source))
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_buffer.add_frame(frame)
            _, buffer = cv2.imencode(".jpg", frame)
            try:
                await websocket.send_bytes(buffer.tobytes())
            except WebSocketDisconnect:
                logging.info("Client disconnected.")
                break
            except RuntimeError:
                logging.exception("Error sending frame")
                break

            await asyncio.sleep(0.033)
    finally:
        cap.release()
        try:
            await websocket.close()
        except RuntimeError:
            # swallow errors about closed connections
            logging.debug("Websocket already closed")
            pass


class Data(BaseModel):
    num_frames: int = Field(default=10, ge=1, le=app_settings.frame_buffer_size)
    metadata: dict | None = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


@app.post("/submit", response_model=Data)
async def handle_data(data: Data):
    global frame_buffer

    logging.info("Num frames:", data.num_frames)
    logging.info("Metadata:", data.metadata)
    logging.info("Timestamp message:", data.timestamp)

    out_dir = app_settings.target_location / f"{data.timestamp.isoformat()}"
    out_dir.mkdir()

    _dump_frame_buffer(frame_buffer, data.num_frames, out_dir)
    _dump_buffer_metadata(data, out_dir)

    return data


def _dump_frame_buffer(frame_buffer, num_frames, out_dir):
    for i, frame in enumerate(frame_buffer.get_all_frames()[:num_frames]):
        cv2.imwrite(str(out_dir / f"{i}.jpg"), frame)
        logging.info(f"Saved frame to {out_dir / f'{i}.jpg'}")


def _dump_buffer_metadata(data, out_dir):
    with open(out_dir / "metadata.json", "w") as f:
        data_dict = data.dict()
        data_dict["timestamp"] = data_dict["timestamp"].isoformat()
        json.dump(data_dict, f, indent=4)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, workers=1)
