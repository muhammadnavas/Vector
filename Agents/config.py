from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_title: str = "Vector API"
    api_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
