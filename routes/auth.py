from flask import Blueprint, request, jsonify
import datetime
from flask_bcrypt import Bcrypt
from extensions import db
from models import User
from auth import generate_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        name = str(data.get('name', '')).strip()
        email = str(data.get('email', '')).strip().lower()
        phone = str(data.get('phone', '')).strip()
        password = str(data.get('password', ''))

        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400

        # Check existing user
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered.'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        now_iso = datetime.datetime.utcnow().isoformat()

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password,
            totalBudget=0.0,
            hasCompletedOnboarding=False,
            budgetPeriod='monthly',
            periodStartDate=now_iso,
            createdAt=now_iso,
            updatedAt=now_iso
        )

        db.session.add(user)
        db.session.commit()

        user_id_str = str(user.id)
        token = generate_token(user_id_str)

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': token,
            'userId': user_id_str,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Register Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = str(data.get('email', '')).strip().lower()
        password = str(data.get('password', ''))

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

        user_id_str = str(user.id)
        token = generate_token(user_id_str)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f"Login Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
