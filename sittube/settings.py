from pydantic import BaseSettings, validator

from pathlib import Path


class Settings(BaseSettings):
    video_source: Path
    frame_buffer_size: int = 50
    target_location: Path

    class Config:
        env_file = "../.env"

    @validator("video_source")
    def validate_video_source(cls, value):
        if not value.exists():
            raise FileNotFoundError("Video source does not exist.")
        return value

    @validator("target_location")
    def validate_target_location(cls, value):
        if not value.exists():
            try:
                value.mkdir(parents=True)
            except Exception as e:
                print("Error creating target location")
                print(f"Consider creating the directory manually: {value}")
                print(f"Error: {e}")
        return value
