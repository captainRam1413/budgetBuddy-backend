import sys
import os

# Add project root directory to sys.path so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

def handler(environ, start_response):
    # Restore original path if Vercel rewritten PATH_INFO to /api/index
    path_info = environ.get('PATH_INFO', '')
    if path_info in ['/api/index', '/api/index.py', '/api', '/api/']:
        forwarded_path = (
            environ.get('HTTP_X_FORWARDED_URI') or 
            environ.get('HTTP_X_MATCHED_PATH') or 
            environ.get('RAW_URI') or 
            '/'
        )
        environ['PATH_INFO'] = forwarded_path.split('?')[0]

    return flask_app(environ, start_response)

app = handler
