from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinalProject Backend"
    DATABASE_URL: str = "sqlite:///./finalproject.db"


settings = Settings()