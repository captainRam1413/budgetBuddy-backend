import os
from dotenv import load_dotenv
from urllib.parse import quote, unquote
from sqlalchemy.engine import make_url

load_dotenv()

# Filter environment variables to find a valid PostgreSQL database URL
candidates = [
    os.getenv('DATABASE_URL'),
    os.getenv('POSTGRES_URL'),
    os.getenv('SUPABASE_DATABASE_URL'),
    os.getenv('DATABASE_PATH')
]

raw_db_url = None
for c in candidates:
    if c and (c.strip().startswith('postgresql://') or c.strip().startswith('postgres://')):
        raw_db_url = c.strip()
        break

if not raw_db_url:
    # Fallback to any string with ://
    for c in candidates:
        if c and '://' in c:
            raw_db_url = c.strip()
            break

if not raw_db_url:
    raise ValueError("❌ Error: Valid PostgreSQL DATABASE_URL is required. Please set DATABASE_URL in Vercel environment variables.")

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

# Sanity check validation with SQLAlchemy make_url
try:
    make_url(raw_db_url)
except Exception as parse_error:
    print(f"[Warning] Invalid SQLAlchemy URL format: {parse_error}")

class Config:
    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-budgetbuddy-secret-key-change-me')
    
    # Database Configuration (PostgreSQL / Supabase ORM)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DAYS = 7
