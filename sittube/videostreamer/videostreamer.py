"""
Ideally what we want here is a video/buffer like interface:
VideoStreamer.read() -> returns a frame
VideoStreamer.seek() -> seeks to a frame
We should probably use a context manager for opening and closing the video file

Let's start with reading a file from disk.
Now, let's store the frames in a buffer and implement the read method.
"""

import cv2


class VideoBuffer:
    # TODO add class docstring and type hints for buffer
    def __init__(
        self,
        filename: str,
        buffer_size: int = 1000,
        buffer_step: int = 10,
    ):
        self.cap = cv2.VideoCapture(filename)
        self.buffer = []  # stores the frames of the video
        self.frame_index = []  # stores the frame indexes of the frames in the original video (useful for debugging)
        self.buffer_size = buffer_size  # number of frames to store in the buffer
        self.buffer_step = buffer_step  # number of frames to skip between frames
        self._fill_buffer()

    def _fill_buffer(self):
        step = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            if len(self.buffer) > self.buffer_size:
                self.buffer.pop(0)
                self.frame_index.pop(0)

            if step % self.buffer_step == 0:
                self.buffer.append(frame)
                self.frame_index.append(step)
                self._show_frame(frame)

            # print(self)
            # time.sleep(0.1)
            step += 1

    def __repr__(self):
        return (
            f"VideoBuffer: "
            f"Total number of frames: {int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))}, "
            f"Buffer step: {self.buffer_step}, "
            f"Frames in Buffer: {len(self.buffer)}, "
            f"Current Frame: {self.frame_index[-1]}, "
            f"Original FPS: {self.cap.get(cv2.CAP_PROP_FPS)})"
        )

    def read(self):
        if not self.buffer:
            return None
        return self.buffer.pop(0)

    def seek(self, frame):
        # TODO implement this correctly later, should index the ring buffer
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self.buffer = []
        self._fill_buffer()

    def __del__(self):
        self.cap.release()

    def show(self):
        for frame in self.buffer:
            self._show_frame(frame)

            # interrupt the display if q is pressed
            if cv2.waitKey(100) & 0xFF == ord("q"):
                break

            # print(self)

    def _show_frame(self, frame):
        cv2.imshow("frame", frame)


def main():
    VideoBuffer("/home/alvaro/repos/mine/sittube/resources/countdown.mp4")
    # VideoBuffer("/home/alvaro/repos/mine/sittube/resources/countdown.mp4").show()


if __name__ == "__main__":
    main()
