from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "InvoiceIQ"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://root:root@localhost:5432/invoiceiq_db"
    
    # Grok / OpenAI API
    XAI_API_KEY: str = ""
    XAI_BASE_URL: str = "https://api.groq.com/openai/v1"
    XAI_MODEL: str = "openai/gpt-oss-120b"
    
    # Upload storage
    UPLOAD_DIR: str = "uploads/invoices"
    MAX_UPLOAD_SIZE_MB: int = 15
    
    # OCR
    TESSERACT_CMD: str = ""
    
    # Security / CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @property
    def upload_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        if not p.is_absolute():
            p = BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
