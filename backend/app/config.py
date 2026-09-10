import os
from pathlib import Path
from pydantic import BaseModel

# Explicitly load backend/.env
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file, override=True)
    except Exception:
        pass

    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k:
                        os.environ[k] = v
    except Exception:
        pass

class Settings(BaseModel):
    app_name: str = "ReSkillAI Career Intelligence API"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    gemini_mock_mode: bool = os.getenv("GEMINI_MOCK_MODE", "false").lower() in ["true", "1", "yes"]
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]

    @property
    def APP_NAME(self) -> str:
        return self.app_name

    @property
    def GEMINI_API_KEY(self) -> str:
        return self.gemini_api_key

    @property
    def GEMINI_MODEL(self) -> str:
        return self.gemini_model

    @property
    def GEMINI_MOCK_MODE(self) -> bool:
        return self.gemini_mock_mode

settings = Settings()
