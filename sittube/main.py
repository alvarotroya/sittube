import datetime

from fastapi import FastAPI, WebSocket
import cv2
import asyncio

from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.websocket("/video")
async def video_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture("/home/alvaro/repos/mine/sittube/resources/countdown.mp4")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

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
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


@app.post("/submit")
async def handle_data(data: Data):
    print("Num frames:", data.num_frames)
    print("Timestamp message:", data.timestamp)
    return JSONResponse(
        content={"message": "Data received", "yourMessage": data.message}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
