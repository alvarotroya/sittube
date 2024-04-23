"""
Ideally what we want here is a video/buffer like interface:
VideoStreamer.read() -> returns a frame
VideoStreamer.seek() -> seeks to a frame
We should probably use a context manager for opening and closing the video file

Let's start with reading a file from disk.
Now, let's store the frames in a buffer and implement the read method.
"""

import datetime
import functools
import time

import cv2


class VideoBuffer:
    # TODO add class docstring and type hints for buffer
    def __init__(
        self,
        filename: str,
        buffer_size: int = 50,
        buffer_step: int = 30,
    ):
        self.cap = None
        self.buffer = []  # stores the frames of the video
        self.frame_index = []  # stores the frame indexes of the frames in the original video (useful for debugging)
        self.filename = filename
        self.buffer_size = buffer_size  # number of frames to store in the buffer
        self.buffer_step = buffer_step  # number of frames to skip between frames
        self.start_ts = datetime.datetime.utcnow()

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.filename)
        self._fill_buffer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cap.release()

    def _fill_buffer(self):
        step = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            if len(self.buffer) > self.buffer_size:
                self._pop()

            if step % self.buffer_step == 0:
                self.buffer.append(frame)
                self.frame_index.append(step)

            # print(self)
            # time.sleep(0.1)
            step += 1

    def __repr__(self):
        return (
            f"VideoBuffer: "
            f"Total number of frames: {int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))}, "
            f"Buffer step: {self.buffer_step}, "
            f"Frames in buffer: {len(self.buffer)}, "
            f"Current frame: {self.frame_index[-1] if self.frame_index else -1}, "
            f"Original FPS: {self.cap.get(cv2.CAP_PROP_FPS)}, "
            f"Buffered FPS: {self.fps:.2f})"
        )

    def __len__(self):
        return len(self.buffer)

    def __getitem__(self, index):
        return self.buffer[index]

    @functools.cached_property
    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS) / self.buffer_step

    def _get_closest_buffer_frame_at_timestamp(self, timestamp: datetime.datetime):
        delta_ts = timestamp - self.start_ts
        frame_index = int(delta_ts.total_seconds() * self.fps) % self.buffer_size
        return frame_index

    def read(self):
        if self.buffer:
            _, frame = self._pop()
            return True, frame
        else:
            return False, None

    def _pop(self):
        return self.frame_index.pop(0), self.buffer.pop(0)

    def show(self):
        for frame in self.buffer:
            cv2.imshow("frame", frame)

            # interrupt the display if q is pressed
            if cv2.waitKey(100) & 0xFF == ord("q"):
                break

            # print(self)

    def slice_at_timestamp(
        self,
        timestamp: datetime.datetime,
        *,  # disallow positional arguments
        num_frames: int | None = None,
        num_frames_left: int = 0,
        num_frames_right: int = 0,
    ):
        if not any([num_frames, num_frames_right, num_frames_left]):
            raise ValueError(
                "At least one of num_frames, num_frames_right or num_frames_left must be provided."
            )

        if num_frames is not None:
            num_frames_right = num_frames_left = num_frames

        curr_frame = self._get_closest_buffer_frame_at_timestamp(timestamp)

        # TODO: we might want to guarantee that we don't return less than num_frames frames or at least log a warning
        left_index = max(0, curr_frame - num_frames_left)
        right_index = min(len(self), curr_frame + num_frames_right)

        # TODO: this method should actually return a new VideoBuffer instance, skipping now for simplicity
        return self.buffer[left_index:right_index]


def main():
    start = datetime.datetime.utcnow()
    VIDEO_PATH = "/home/alvaro/repos/mine/sittube/resources/countdown.mp4"
    with VideoBuffer(VIDEO_PATH) as video:
        # video.show()
        # while True:
        #     ret, frame = video.read()
        #
        #     if not ret:
        #         print("End of video. Exiting...")
        #         break
        #
        #     # print(video)
        #     cv2.imshow("frame", frame)
        #     if cv2.waitKey(100) & 0xFF == ord("q"):
        #         break
        # for i in range(len(video)):
        #     # print(i)
        #     cv2.imshow("frame", video[i])
        #     if cv2.waitKey(100) & 0xFF == ord("q"):
        #         break

        time.sleep(5)
        now = datetime.datetime.utcnow()
        for frame in video.slice_at_timestamp(now, num_frames_right=200):
            # print(i)
            cv2.imshow("frame", frame)
            if cv2.waitKey(100) & 0xFF == ord("q"):
                break

        # print(video)
        # print(len(video))
        # print(video.frame_index)
        # for _ in range(10):
        #     time.sleep(1)
        #     now_again = datetime.datetime.utcnow()
        #     print((now_again - start).total_seconds())
        #     index = video.get_closest_frame_index(now_again)
        #     print(index)
        #     cv2.imshow("frame", video[index])
        #     if cv2.waitKey(100) & 0xFF == ord("q"):
        #         break


if __name__ == "__main__":
    main()
