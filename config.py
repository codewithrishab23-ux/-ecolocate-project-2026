import os
from datetime import timedelta
from dotenv import load_dotenv

# Robust .env loading (current directory and module directory)
basedir = os.path.abspath(os.path.dirname(__file__))
env_file = os.path.join(basedir, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ecolocate-dev-secret-key-phase2-98471928374')
    
    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.environ.get('DB_PORT', 3307))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'ewaste_db')
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 25))
    DB_SSL_CA = os.environ.get('DB_SSL_CA', None)
    
    # Session Security
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
    
    # Security & Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload limit
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Valid for session duration
