from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Desafio Toro"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000"
    ]
    DESCRIPTION: str = ""
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_DEFAULT_REGION: str
    DYNAMODB_TABLE: str = "questions"
    SNS_TOPIC_PROCESS_NAME: str = "process-question"
    SNS_TOPIC_NOTIFY_NAME: str = "notify-response"
    SNS_TOPIC_PROCESS: str = f"arn:aws:sns:{os.getenv('AWS_REGION')}:{os.getenv('AWS_ACCOUNT_ID')}:process-question"
    SNS_TOPIC_NOTIFY: str = f"arn:aws:sns:{os.getenv('AWS_REGION')}:{os.getenv('AWS_ACCOUNT_ID')}:notify-response"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: str = "8000"
    
    
    model_config = SettingsConfigDict(
        env_file="backend/.env"
    )

@lru_cache
def get_settings():
    """
    This function will cache the settings object to avoid reading the configuration file multiple times.
    https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru_cache
    """
    return Settings()


settings = get_settings()