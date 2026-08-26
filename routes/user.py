from flask import Blueprint, request, jsonify
import datetime
import json
from extensions import db
from models import User
from auth import token_required

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    try:
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f"Get Profile Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    try:
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        data = request.get_json() or {}
        name = data.get('name')
        phone = data.get('phone')

        if name is not None:
            user.name = str(name).strip()
        if phone is not None:
            user.phone = str(phone).strip()

        user.updatedAt = datetime.datetime.utcnow().isoformat()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update Profile Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@user_bp.route('/budget', methods=['PUT'])
@token_required
def update_budget(current_user_id):
    try:
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        data = request.get_json() or {}
        total_budget = data.get('totalBudget')

        if total_budget is None:
            return jsonify({'success': False, 'message': 'totalBudget is required'}), 400

        try:
            budget_val = float(total_budget)
            if budget_val < 0:
                return jsonify({'success': False, 'message': 'Budget cannot be negative'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid budget amount'}), 400

        user.totalBudget = budget_val
        user.updatedAt = datetime.datetime.utcnow().isoformat()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Total budget updated successfully', 'totalBudget': budget_val}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update Budget Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@user_bp.route('/period', methods=['PUT'])
@token_required
def update_budget_period(current_user_id):
    try:
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        data = request.get_json() or {}
        period = data.get('budgetPeriod', 'monthly')
        start_date = data.get('periodStartDate', datetime.datetime.utcnow().isoformat())

        if period not in ['weekly', 'monthly']:
            return jsonify({'success': False, 'message': 'Invalid budget period. Must be weekly or monthly.'}), 400

        user.budgetPeriod = period
        user.periodStartDate = start_date
        user.updatedAt = datetime.datetime.utcnow().isoformat()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Budget period updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update Period Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@user_bp.route('/onboarding/complete', methods=['POST'])
@token_required
def complete_onboarding(current_user_id):
    try:
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        user.hasCompletedOnboarding = True
        user.updatedAt = datetime.datetime.utcnow().isoformat()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Onboarding marked as completed'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Complete Onboarding Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

# ============ DYNAMIC SCREENS (User-Facing) ============

@user_bp.route('/my-screens', methods=['GET'])
@token_required
def get_my_screens(current_user_id):
    """Returns list of screens this user has access to (with full field configs)."""
    try:
        from models import DynamicScreen, UserScreenAccess
        access = UserScreenAccess.query.filter_by(user_id=int(current_user_id)).all()
        screen_ids = [a.screen_id for a in access]

        if not screen_ids:
            return jsonify({'success': True, 'screens': []}), 200

        screens = DynamicScreen.query.filter(DynamicScreen.id.in_(screen_ids)).all()
        return jsonify({
            'success': True,
            'screens': [s.to_dict() for s in screens]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


