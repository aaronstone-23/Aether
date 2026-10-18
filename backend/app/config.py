# Readin the env variables
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  #this will reject bodies over 1MB

    # comma seperated lists okay?
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://localhost:5173")
    ADMIN_KEY = os.getenv("ADMIN_KEY", "")

    SUPABASE_URL = os.getenv("SUPERBASE_URL", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
    OPENROUTER_FALLBACK_MODEL = os.getenv("OPENROUTER_FALLBACK_MODEL", "deepseek/deepseek-chat")
    OPENROUTER_URL= "https://openrouter.ai/api/v1/chat/completions"

    SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY", "")

    SMIP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Aether")

    RATELIMIT_DEFAULT = "60 per minute"
    RATELIMIT_STORAGE_URL = "memory://"

    @staticmethod
    def check(logger):
        # WARNING (does not crash) about missing settings okay?
        for key in ("SUPABASE_URL",  "SUPABASE_SERVICE_KEY", "OPENROUTER_API_KEY", "ADMIN_KEY"):
            if not getattr(Config, key):
                logger.warning("Env var %s is not set;" 
                " related features are disabled", 
                key)


