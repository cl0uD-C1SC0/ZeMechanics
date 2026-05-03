from  pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

BASE_DIR = os.getcwd()

dotenv = os.path.join(BASE_DIR, "../../env")

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = str(os.getenv('DATABASE_URL'))
    SECRET_KEY: str = str(os.getenv('SECRET_KEY'))
    SECRET_KEY_JWT: str = str(os.getenv('SECRET_KEY_JWT'))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
