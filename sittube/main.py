from fastapi import FastAPI, WebSocket
import cv2
import asyncio

from starlette.responses import RedirectResponse
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
