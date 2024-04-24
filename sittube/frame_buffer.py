class FrameBuffer:
    def __init__(self, size: int):
        self.size = size
        self.buffer = [None] * size
        self.cursor = 0

    def add_frame(self, frame):
        self.buffer[self.cursor % self.size] = frame
        self.cursor = (self.cursor + 1) % self.size

    def get_all_frames(self):
        # Return all non-None frames, starting from the oldest to the newest
        if any(frame is None for frame in self.buffer):
            # Buffer is not yet full, return only the filled part
            return self.buffer[: self.cursor]
        else:
            # Buffer is full, return in correct order
            return self.buffer[self.cursor :] + self.buffer[: self.cursor]
