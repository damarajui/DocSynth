from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    chroma_db_path: str
    redis_url: str

    class Config:
        env_file = ".env"

settings = Settings()