import os

class Settings:
    app_name: str = os.getenv("APP_NAME", "FlowForge AI")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./flowforge.db")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "15"))
    ai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    ai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    ai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

settings = Settings()
