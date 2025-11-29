"""
Configuration management for the fraud detection API
"""
from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    workers: int = 4
    
    # Auth Service
    auth_server_url: str = "http://localhost:3000"
    auth_token_verify_endpoint: str = "/api/auth/verify"
    
    # CORS - use string in env, parse to list
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080,chrome-extension://*"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins_str.split(',')]
    
    # Logging
    log_level: str = "INFO"
    
    # API Info
    api_title: str = "Fraud Detection API"
    api_version: str = "1.0.0"
    api_description: str = "API for detecting fraudulent URLs, SMS messages, and UPI transactions"
    
    # Google Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_enabled: bool = False
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_parse_none_str": "null"
    }


# Global settings instance
settings = Settings()
