from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(min_length=1)
    jwt_secret: str = Field(min_length=1)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    default_timezone: str = "Asia/Kolkata"
    cors_origins: str = "http://localhost:5173"
    environment: Literal["development", "testing", "production"] = "development"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        normalized = str(value).strip()
        if normalized.startswith("postgres://"):
            normalized = "postgresql+psycopg://" + normalized.removeprefix("postgres://")
        elif normalized.startswith("postgresql://"):
            normalized = "postgresql+psycopg://" + normalized.removeprefix("postgresql://")
        if normalized.startswith("sqlite"):
            raise ValueError("DATABASE_URL must use PostgreSQL; SQLite is not supported")
        return normalized

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.environment == "production":
            if len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must be at least 32 characters in production")
            if "*" in self.cors_origin_list:
                raise ValueError("CORS_ORIGINS must not use a wildcard in production")
            if any(origin.startswith(("http://localhost", "http://127.0.0.1")) for origin in self.cors_origin_list):
                raise ValueError("CORS_ORIGINS must not contain local origins in production")
        if not self.cors_origin_list:
            raise ValueError("CORS_ORIGINS must contain at least one origin")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
