from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""

    # Application Settings
    APP_NAME: str = "Country Currency API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Database Settings (MySQL)
    DATABASE_URL: str = Field(
        default="mysql+aiomysql://root:password@localhost:3306/country_currency_db"
    )
    CACHE_DIR: str = "cache"

    # External API Settings
    RESTCOUNTRIES_API_URL: str = (
        "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    )
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6/latest/USD"
    API_TIMEOUT: int = 30

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
