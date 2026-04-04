import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", 30))
    OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", 2))


settings = Settings()
