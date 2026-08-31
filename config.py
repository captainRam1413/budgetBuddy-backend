import os
from dotenv import load_dotenv
from urllib.parse import quote, unquote

load_dotenv()

raw_db_url = (
    os.getenv('DATABASE_URL') or 
    os.getenv('POSTGRES_URL') or 
    os.getenv('SUPABASE_DATABASE_URL') or 
    os.getenv('DATABASE_PATH')
)

if not raw_db_url:
    raise ValueError("❌ Error: DATABASE_URL environment variable is missing! Please configure PostgreSQL / Supabase connection string.")

if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

# Automatically encode special characters (like '@') in database passwords
try:
    if '://' in raw_db_url and '@' in raw_db_url:
        scheme, rest = raw_db_url.split('://', 1)
        last_at_index = rest.rfind('@')
        if last_at_index != -1:
            user_pass = rest[:last_at_index]
            host_db = rest[last_at_index+1:]
            if ':' in user_pass:
                user, pwd = user_pass.split(':', 1)
                encoded_pwd = quote(unquote(pwd))
                raw_db_url = f"{scheme}://{user}:{encoded_pwd}@{host_db}"
except Exception:
    pass

# Automatically append sslmode=require if connecting to cloud PostgreSQL
if raw_db_url.startswith("postgresql://") and 'sslmode=' not in raw_db_url:
    delim = '&' if '?' in raw_db_url else '?'
    raw_db_url = f"{raw_db_url}{delim}sslmode=require"

class Config:
    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-budgetbuddy-secret-key-change-me')
    
    # Database Configuration (PostgreSQL / Supabase SQLAlchemy ORM)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DAYS = 7
