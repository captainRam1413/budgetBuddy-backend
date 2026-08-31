import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from extensions import db
from db import init_db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.category import category_bp
from routes.expense import expense_bp
from routes.admin import admin_bp

class VercelPathFixMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        
        # Check all headers Vercel/proxies send with the original request path
        matched_path = (
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('HTTP_X_REWRITE_URL') or
            environ.get('HTTP_X_ORIGINAL_URL') or
            environ.get('HTTP_X_VERCEL_FORWARDED_PATH') or
            environ.get('RAW_URI') or
            environ.get('REQUEST_URI')
        )
        
        if matched_path and matched_path not in ['/api/index', '/api/index.py']:
            environ['PATH_INFO'] = matched_path.split('?')[0]
        elif path_info in ['/api/index', '/api/index.py']:
            environ['PATH_INFO'] = '/'

        return self.app(environ, start_response)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

    # Enable CORS for frontend integration
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/admin/*": {"origins": "*"}})

    # Initialize SQLAlchemy Extension
    db.init_app(app)

    # Initialize Database Tables
    init_db(app)


    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'orm': 'SQLAlchemy', 'database': 'SQLite', 'service': 'budgetBuddy-backend'}), 200

    @app.route('/debug-env', methods=['GET'])
    def debug_env():
        from flask import request
        headers = {k: v for k, v in request.headers.items()}
        environ_keys = {k: str(v) for k, v in request.environ.items() if isinstance(v, (str, int, float, bool))}
        return jsonify({'headers': headers, 'environ': environ_keys, 'path': request.path}), 200


    @app.route('/', methods=['GET'])
    def root():
        # Return JSON if explicitly requested by API client
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'online',
                'service': 'BudgetBuddy API Server',
                'version': '1.0.0',
                'admin_studio': '/admin/',
                'health_check': '/health'
            }), 200

        # Beautiful Landing & API Dashboard Page
        landing_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BudgetBuddy API Server</title>
            <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
            <style>
                :root {
                    --bg-dark: #090d16;
                    --bg-card: #111726;
                    --border: rgba(255, 255, 255, 0.08);
                    --accent: #6366f1;
                    --accent-hover: #4f46e5;
                    --success: #10b981;
                    --text-main: #f8fafc;
                    --text-muted: #94a3b8;
                }
                * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
                body {
                    background: var(--bg-dark);
                    color: var(--text-main);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .container {
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 24px;
                    padding: 40px;
                    max-width: 640px;
                    width: 100%;
                    box-shadow: 0 25px 60px rgba(0,0,0,0.6);
                }
                .status-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(16, 185, 129, 0.15);
                    color: #34d399;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 700;
                    margin-bottom: 20px;
                }
                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: #10b981;
                    border-radius: 50%;
                    box-shadow: 0 0 10px #10b981;
                }
                h1 {
                    font-size: 32px;
                    font-weight: 800;
                    margin-bottom: 12px;
                    background: linear-gradient(135deg, #6366f1, #10b981);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                p.desc {
                    color: var(--text-muted);
                    font-size: 15px;
                    line-height: 1.6;
                    margin-bottom: 28px;
                }
                .grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                    margin-bottom: 28px;
                }
                .card {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    padding: 20px;
                    text-decoration: none;
                    color: var(--text-main);
                    transition: all 0.2s;
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                .card:hover {
                    border-color: var(--accent);
                    background: rgba(99, 102, 241, 0.1);
                    transform: translateY(-2px);
                }
                .card h3 { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
                .card p { font-size: 13px; color: var(--text-muted); }
                .footer {
                    border-top: 1px solid var(--border);
                    padding-top: 20px;
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    color: var(--text-muted);
                    font-family: 'JetBrains Mono', monospace;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="status-badge">
                    <span class="status-dot"></span> API Server Active & Healthy
                </div>
                <h1>⚡ BudgetBuddy Backend</h1>
                <p class="desc">High-performance Flask API engine powered by SQLAlchemy ORM on Vercel Serverless.</p>
                
                <div class="grid">
                    <a href="/admin/" class="card">
                        <h3>🗄️ Admin Studio</h3>
                        <p>Database explorer, SQL query runner & screen configurator</p>
                    </a>
                    <a href="/health" class="card">
                        <h3>🟢 Health Status</h3>
                        <p>Real-time system diagnostics & ORM metrics</p>
                    </a>
                </div>

                <div class="footer">
                    <span>ORM: SQLAlchemy</span>
                    <span>Deployment: Vercel Serverless</span>
                    <span>Version: 1.0.0</span>
                </div>
            </div>
        </body>
        </html>
        """
        return landing_html, 200


    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(admin_bp)

    return app

app = create_app()

if __name__ == '__main__':
    print(f"🚀 Starting BudgetBuddy Backend Server (SQLAlchemy ORM) on port {Config.PORT}...")
    app.run(host='0.0.0.0', port=Config.PORT, debug=(Config.FLASK_ENV == 'development'))
