from functools import lru_cache
from typing import List
from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Desafio Toro"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = ""
    ALLOWED_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_DEFAULT_REGION: str
    AWS_ACCOUNT_ID: str
    DYNAMODB_TABLE_QUESTIONS: str = "questions"
    DYNAMODB_TABLE_SESSIONS: str = "sessions"
    SNS_TOPIC_PROCESS_NAME: str = "process-question"
    SNS_TOPIC_NOTIFY_NAME: str = "notify-response"

    # OpenAI
    OPENAI_API_KEY: str

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: str = "8000"

    class Config:
        env_file = ".env"

    @property
    def sns_topic_process(self) -> str:
        return (
            f"arn:aws:sns:{self.AWS_REGION}:"
            f"{self.AWS_ACCOUNT_ID}:{self.SNS_TOPIC_PROCESS_NAME}"
        )

    @property
    def sns_topic_notify(self) -> str:
        return (
            f"arn:aws:sns:{self.AWS_REGION}:"
            f"{self.AWS_ACCOUNT_ID}:{self.SNS_TOPIC_NOTIFY_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
