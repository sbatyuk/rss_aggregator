from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]
FEEDS_PATH = BASE_DIR / "feeds.yaml"


class Settings(BaseSettings):
    env: str = "dev"
    database_url: str = None
    fetch_max_retries: int = 3
    fetch_retry_delay_seconds: int = 2

    class Config:
        env_file = BASE_DIR / ".env"


settings = Settings()
