import datetime

from fastapi import FastAPI, WebSocket
import cv2
import asyncio

from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from sittube.frame_buffer import FrameBuffer

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

frame_buffer = FrameBuffer(10)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.websocket("/video")
async def video_endpoint(websocket: WebSocket):
    global frame_buffer
    await websocket.accept()
    cap = cv2.VideoCapture("/home/alvaro/repos/mine/sittube/resources/countdown.mp4")
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
                print("Client disconnected.")
                break
            except RuntimeError as e:
                print(f"Error sending frame: {e}")
                break

            await asyncio.sleep(0.033)
    finally:
        cap.release()
        try:
            await websocket.close()
        except RuntimeError:
            # swallow errors about closed connections
            pass


class Data(BaseModel):
    num_frames: int = Field(default=10, ge=1, le=100)
    metadata: dict | None = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


@app.post("/submit", response_model=Data)
async def handle_data(data: Data):
    print("Num frames:", data.num_frames)
    print("Metadata:", data.metadata)
    print("Timestamp message:", data.timestamp)
    global frame_buffer
    for i, frame in enumerate(frame_buffer.get_all_frames()):
        # Save the frame to a file
        filename = f"frame_{i}_{data.timestamp.isoformat()}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved frame to {filename}")

    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, workers=1)
