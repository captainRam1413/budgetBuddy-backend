import os
from dotenv import load_dotenv

import tempfile

from urllib.parse import quote, unquote

load_dotenv()

db_url = os.getenv('DATABASE_URL')

if not db_url:
    # Vercel serverless filesystem is read-only except /tmp
    if os.getenv('VERCEL'):
        tmp_db = os.path.join(tempfile.gettempdir(), 'budgetbuddy.db')
        db_url = f'sqlite:///{tmp_db}'
    else:
        db_url = 'sqlite:///budgetbuddy.db'
else:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # Automatically encode special characters (like '@') in database passwords
    try:
        if '://' in db_url and '@' in db_url:
            scheme, rest = db_url.split('://', 1)
            last_at_index = rest.rfind('@')
            if last_at_index != -1:
                user_pass = rest[:last_at_index]
                host_db = rest[last_at_index+1:]
                if ':' in user_pass:
                    user, pwd = user_pass.split(':', 1)
                    encoded_pwd = quote(unquote(pwd))
                    db_url = f"{scheme}://{user}:{encoded_pwd}@{host_db}"
    except Exception:
        pass


class Config:
    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-budgetbuddy-secret-key-change-me')
    
    # Database Configuration (SQLAlchemy ORM)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DAYS = 7


