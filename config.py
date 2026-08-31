import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL', 'sqlite:///budgetbuddy.db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

class Config:
    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-budgetbuddy-secret-key-change-me')
    
    # Database Configuration (SQLAlchemy ORM)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DAYS = 7

