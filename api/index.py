import sys
import os

# Add project root directory to sys.path so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel serverless WSGI handler
