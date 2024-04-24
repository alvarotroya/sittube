from pydantic import BaseSettings, validator

from pathlib import Path


class Settings(BaseSettings):
    video_source: Path
    frame_buffer_size: int = 10
    target_location: Path

    class Config:
        env_file = ".env"

    @validator("target_location")
    def validate_target_location(cls, value):
        if not value.exists():
            raise FileNotFoundError("Target location does not exist.")
        return value

    @validator("video_source")
    def validate_video_source(cls, value):
        if not value.exists():
            raise FileNotFoundError("Video source does not exist.")
        return value
