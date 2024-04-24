# NOTE
# Please ignore this file for now, it is work in progress that has not been integrated in the main codebase yet.
# It's here for future reference and to keep track of the progress made so far.

"""
Ideally what we want here is a video/buffer like interface:
VideoStreamer.read() -> returns a frame
VideoStreamer.seek() -> seeks to a frame
We should probably use a context manager for opening and closing the video stream

Let's start with reading a file from disk.
Now, let's store the frames in a ring buffer and implement the read method.
"""

import copy
import datetime
import functools
import threading
import time  # noqa: F401

import cv2

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VideoBuffer:
    # TODO add class docstring and type hints for buffer
    def __init__(
        self,
        filename: str,
        buffer_size: int = 50,
        buffer_step: int = 1,
    ):
        self.cap = None
        self.buffer = []  # stores the frames of the video
        self.frame_index = []  # stores the frame indexes of the frames in the original video (useful for debugging)
        self.filename = filename
        self.buffer_size = buffer_size  # number of frames to store in the buffer
        self.buffer_step = buffer_step  # number of frames to skip between frames
        self.lock = threading.Lock()  # lock the buffer for thread safety
        self.running = False
        self.start_ts = datetime.datetime.utcnow()

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.filename)
        self.running = True
        # consume the video stream in a separate thread
        thread = threading.Thread(target=self._fill_buffer, daemon=True)
        thread.start()
        time.sleep(0.1)  # allow the buffer to fill up
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.cap.release()

    def _fill_buffer(self):
        step = 0
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.running = False
                break

            with self.lock:
                if step % self.buffer_step == 0:
                    logging.info("writing frame to buffer")
                    self.buffer.append(frame)
                    self.frame_index.append(step)

                    if len(self.buffer) > self.buffer_size:
                        self._pop()

            # print(self)
            # time.sleep(0.1)
            step += 1

    def __repr__(self):
        with self.lock:
            return (
                f"VideoBuffer: "
                f"Total number of frames: {int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))}, "
                f"Buffer step: {self.buffer_step}, "
                f"Frames in buffer: {len(self.buffer)}, "
                f"Current frame: {self.frame_index[-1] if self.frame_index else 'N/A'}, "
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
        with self.lock:
            if self.buffer:
                _, frame = self._pop()
                return True, frame
            else:
                return False, None

    def _pop(self):
        return self.frame_index.pop(0), self.buffer.pop(0)

    def show(self):
        while self.running:
            if not self.buffer:
                continue

            with self.lock:
                current_frame = self.buffer[-1]

            cv2.imshow("frame", current_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
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
        with self.lock:
            return copy.deepcopy(self.buffer[left_index:right_index])


def main():
    start = datetime.datetime.utcnow()
    VIDEO_PATH = "/home/alvaro/repos/mine/sittube/resources/countdown.mp4"
    with VideoBuffer(VIDEO_PATH) as video:
        # for i in range(len(video)):
        #     cv2.imshow("frame", video[i])
        #     if cv2.waitKey(100) & 0xFF == ord("q"):
        #         break

        # time.sleep(1)
        now = datetime.datetime.utcnow()
        print(video)
        for i, frame in enumerate(video.slice_at_timestamp(now, num_frames_right=10)):
            logging.info(f"showing frame {i} in first for loop")
            cv2.imshow("foo", frame)
            if cv2.waitKey(100) & 0xFF == ord("q"):
                break

        time.sleep(2)
        now = datetime.datetime.utcnow()
        print(video)
        for i, frame in enumerate(video.slice_at_timestamp(now, num_frames_right=10)):
            logging.info(f"showing frame {i} in second for loop")
            cv2.imshow("foo", frame)
            if cv2.waitKey(100) & 0xFF == ord("q"):
                break

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
