"""
Configuration management for the fraud detection API
"""
from pydantic_settings import BaseSettings
from typing import List


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
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "chrome-extension://*"
    ]
    
    # Logging
    log_level: str = "INFO"
    
    # API Info
    api_title: str = "Fraud Detection API"
    api_version: str = "1.0.0"
    api_description: str = "API for detecting fraudulent URLs, SMS messages, and UPI transactions"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
