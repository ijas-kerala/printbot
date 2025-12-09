import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PrintBot"
    ENV: str = "development"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./printbot.db"
    
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_CURRENCY: str = "INR"
    
    PRINTER_NAME: str = "Canon_LBP122dw"
    PRICE_PER_PAGE: float = 5.0

    class Config:
        env_file = ".env"

settings = Settings()
