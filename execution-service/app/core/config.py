from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    MONGO_URL: str = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    MONGO_DB: str = os.getenv('MONGO_DB', 'execution_db')

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
