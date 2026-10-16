# Shared extension objects!! CORS, rate limiter, supabase client
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from supabase import create_client, Client

cors = CORS()
limiter = Limiter(key_func=get_remote_address)

_supabase: Client | None = None

def get_supabase() -> Client | None:
    # ALWAYS CALL THIS instead of yk importing a variable and all
    return _supabase

def init_extensions(app):
    global _supabase

    origins = [o.strip() for o in app.config["FRONTEND_URL"].split(",") if o.strip()] 
    cors.init_app(app, resources={r"/api/*": {"origins": origins}})

    limiter.init_app(app)

    url, key = app.config["SUPABASE_URL"], app.config["SUPABASE_SERVICE_KEY"]
    if url and key:
        try:
            _supabase = create_client(url, key)
        except Exception as e:
            app.logger.error("Supabase init failed: %s", e)
            
