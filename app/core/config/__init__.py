from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
import os
from typing import Optional
import urllib.parse



class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env.test" if os.getenv("TESTING", "").lower() == "true" else ".env",
        env_nested_delimiter="__",
        extra="allow",
    )

    SERVICE_NAME: Optional[str] = "cat-chatter-backend"

    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_NAME_TEST: Optional[str] = None
    ENABLE_DB_CONNECTION_POOLING: bool = True

    TESTING: bool = False

    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str

    @field_validator("DB_PASSWORD")
    @classmethod
    def db_password_escape_special_characters(cls, db_password: str) -> str:
        return urllib.parse.quote_plus(db_password)
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.TESTING:
            db_name = f"{self.DB_NAME_TEST}"
        else:
            db_name = f"{self.DB_NAME}"

        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{db_name}?application_name={self.SERVICE_NAME}&sslmode=allow"

settings = Settings()