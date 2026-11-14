from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str = str(os.getenv('DATABASE_URL'))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
