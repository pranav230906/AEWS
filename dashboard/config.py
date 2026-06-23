import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Field representation of DATABASE_URL
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")

    # Pydantic configuration to load from .env automatically
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @classmethod
    def load_config(cls) -> "Settings":
        """
        Custom loader to check Streamlit Secrets first,
        then fall back to system environment / .env file.
        """
        # 1. Check Streamlit secrets
        try:
            import streamlit as st
            if "DATABASE_URL" in st.secrets:
                return cls(DATABASE_URL=st.secrets["DATABASE_URL"])
        except Exception:
            pass

        # 2. Fallback to Pydantic loading from env/dotenv
        return cls()

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL cannot be empty.")
        if not (v.startswith("postgresql://") or v.startswith("postgresql+psycopg2://") or v.startswith("sqlite://")):
            raise ValueError("DATABASE_URL must be a valid connection string (e.g., starting with postgresql:// or sqlite://)")
        return v

# Instantiate settings once at startup to trigger validation immediately
settings = Settings.load_config()
