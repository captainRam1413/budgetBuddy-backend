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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({'message': 'BudgetBuddy API Server (SQLAlchemy ORM) is running', 'version': '1.0.0'}), 200

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
