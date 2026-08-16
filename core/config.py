import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", os.getenv("SUPABASE_PUBLISHABLE_KEY", ""))
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_SECRET_KEY", ""))
    
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "mutual-fund-lancedb")
    R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "02019eb1a90f552b5ac7df800d970748")
    R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "00d831f038b646bb0d7c75ff21a59353")
    R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "940b5ddf8bb62db02d22f869c1dab4ba2296fb1e142ec930cdec95366ae40f49")
    R2_ENDPOINT: str = os.getenv("R2_ENDPOINT", "https://02019eb1a90f552b5ac7df800d970748.r2.cloudflarestorage.com")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Initialize global settings
settings = Settings()
