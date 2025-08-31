# src/config/settings.py
import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Try to load .env file
load_dotenv()

class Settings(BaseSettings):
    # LLM Configuration
    litellm_provider: str = Field(default="openai", alias="LITELLM_PROVIDER")
    litellm_api_key: str = Field(default="fake-api-key-for-demo", alias="LITELLM_API_KEY")
    litellm_model: str = Field(default="gpt-4", alias="LITELLM_MODEL")
    
    # Browser Configuration
    headless_browser: bool = Field(default=True, alias="HEADLESS_BROWSER")
    browser_timeout: int = Field(default=30000, alias="BROWSER_TIMEOUT")
    
    # Data Configuration
    output_dir: str = Field(default="./data/output", alias="OUTPUT_DIR")
    input_dir: str = Field(default="./data/input", alias="INPUT_DIR")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables
    )

settings = Settings()