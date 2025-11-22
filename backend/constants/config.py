import os
from typing import Optional

YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
DB_HOST: Optional[str] = os.getenv("DB_HOST")
DB_USER: Optional[str] = os.getenv("DB_USER")
DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
DB_NAME: Optional[str] = os.getenv("DB_NAME")
MIN_FETCH_INTERVAL: int = int(os.getenv("MIN_FETCH_INTERVAL", "600"))
DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "channel_update_cache")


