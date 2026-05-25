from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/heat_accounting"
    app_title: str = "HeatAccounting API"
    app_version: str = "1.0.0"


settings = Settings()
