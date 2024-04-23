"""
Ideally what we want here is a video/buffer like interface:
VideoStreamer.read() -> returns a frame
VideoStreamer.seek() -> seeks to a frame
We should probably use a context manager for opening and closing the video file

Let's start with reading a file from disk
"""
import cv2


def main():
    cap = cv2.VideoCapture('/home/alvaro/repos/mine/sittube/resources/countdown.mp4')
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('frame', frame)


if __name__ == '__main__':
    main()
