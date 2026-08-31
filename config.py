import os
from dotenv import load_dotenv

import tempfile

load_dotenv()

db_url = os.getenv('DATABASE_URL')

if not db_url:
    # Vercel serverless filesystem is read-only except /tmp
    if os.getenv('VERCEL'):
        tmp_db = os.path.join(tempfile.gettempdir(), 'budgetbuddy.db')
        db_url = f'sqlite:///{tmp_db}'
    else:
        db_url = 'sqlite:///budgetbuddy.db'
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

class Config:
    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-budgetbuddy-secret-key-change-me')
    
    # Database Configuration (SQLAlchemy ORM)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DAYS = 7


