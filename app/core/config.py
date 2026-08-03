from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SEO & Digital Visibility Audit Engine"
    API_V1_STR: str = "/api/v1"
    PAGESPEED_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()