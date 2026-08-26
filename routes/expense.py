from flask import Blueprint, request, jsonify
import datetime
from urllib.parse import unquote
from sqlalchemy import func
from extensions import db
from models import Expense, Category, User
from auth import token_required

expense_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

def is_income_type(category, exp_type):
    if exp_type == 'credit':
        return True
    if exp_type == 'debit':
        return False
    cat = (category or '').lower()
    return cat in ['income', 'salary', 'deposit', 'credit']

@expense_bp.route('/', methods=['GET'])
@token_required
def get_expenses(current_user_id):
    try:
        expenses = Expense.query.filter_by(user_id=int(current_user_id)).order_by(Expense.date.desc()).all()
        return jsonify({'success': True, 'expenses': [exp.to_dict() for exp in expenses]}), 200

    except Exception as e:
        print(f"Get Expenses Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@expense_bp.route('/', methods=['POST'])
@token_required
def create_expense(current_user_id):
    try:
        data = request.get_json() or {}
        title = str(data.get('title', '')).strip()
        amount = data.get('amount')
        category = str(data.get('category', 'Uncategorized')).strip()
        icon = data.get('icon', '💸')
        color = data.get('color', '#FFB347')
        date = data.get('date', datetime.datetime.utcnow().isoformat())
        exp_type = data.get('type', 'debit')

        if not title or amount is None:
            return jsonify({'success': False, 'message': 'Title and amount are required'}), 400

        try:
            amount_val = float(amount)
            if amount_val <= 0:
                return jsonify({'success': False, 'message': 'Amount must be positive'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid amount value'}), 400

        user_id_int = int(current_user_id)

        # Financial validation: category budget check for non-income transactions
        if not is_income_type(category, exp_type):
            cat_obj = Category.query.filter_by(user_id=user_id_int, name=category).first()
            if cat_obj and cat_obj.budget and float(cat_obj.budget) > 0:
                cat_budget = float(cat_obj.budget)
                
                spent_total = db.session.query(func.sum(Expense.amount)).filter(
                    Expense.user_id == user_id_int,
                    Expense.category == category,
                    Expense.type != 'credit'
                ).scalar() or 0.0

                current_spent = float(spent_total)

                if current_spent + amount_val > cat_budget:
                    remaining = cat_budget - current_spent
                    return jsonify({
                        'success': False,
                        'message': f'Expense exceeds category budget. Category Budget: {cat_budget}, Spent: {current_spent}, Remaining: {remaining}'
                    }), 400

        now_iso = datetime.datetime.utcnow().isoformat()
        expense = Expense(
            user_id=user_id_int,
            title=title,
            amount=amount_val,
            category=category,
            icon=icon,
            color=color,
            date=date,
            type=exp_type,
            createdAt=now_iso,
            updatedAt=now_iso
        )
        db.session.add(expense)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Expense created successfully',
            'expenseId': str(expense.id)
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Create Expense Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@expense_bp.route('/<expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user_id, expense_id):
    try:
        data = request.get_json() or {}
        user_id_int = int(current_user_id)
        expense = Expense.query.filter_by(id=int(expense_id), user_id=user_id_int).first()

        if not expense:
            return jsonify({'success': False, 'message': 'Expense not found'}), 404

        title = str(data.get('title', expense.title)).strip()
        amount = data.get('amount', expense.amount)
        category = str(data.get('category', expense.category)).strip()
        icon = data.get('icon', expense.icon)
        color = data.get('color', expense.color)
        date = data.get('date', expense.date)
        exp_type = data.get('type', expense.type)

        try:
            amount_val = float(amount)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid amount value'}), 400

        expense.title = title
        expense.amount = amount_val
        expense.category = category
        expense.icon = icon
        expense.color = color
        expense.date = date
        expense.type = exp_type
        expense.updatedAt = datetime.datetime.utcnow().isoformat()

        db.session.commit()
        return jsonify({'success': True, 'message': 'Expense updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update Expense Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@expense_bp.route('/<expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user_id, expense_id):
    try:
        user_id_int = int(current_user_id)
        expense = Expense.query.filter_by(id=int(expense_id), user_id=user_id_int).first()

        if not expense:
            return jsonify({'success': False, 'message': 'Expense not found'}), 404

        db.session.delete(expense)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Expense deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete Expense Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@expense_bp.route('/category/<category_name>', methods=['GET'])
@token_required
def get_expenses_by_category(current_user_id, category_name):
    try:
        decoded_name = unquote(category_name).strip()
        user_id_int = int(current_user_id)

        expenses = Expense.query.filter_by(user_id=user_id_int, category=decoded_name).order_by(Expense.date.desc()).all()
        return jsonify({'success': True, 'expenses': [exp.to_dict() for exp in expenses]}), 200

    except Exception as e:
        print(f"Get Category Expenses Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@expense_bp.route('/category/<category_name>/total', methods=['GET'])
@token_required
def get_category_total(current_user_id, category_name):
    try:
        decoded_name = unquote(category_name).strip()
        user_id_int = int(current_user_id)

        total_spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id_int,
            Expense.category == decoded_name,
            Expense.type != 'credit'
        ).scalar() or 0.0

        return jsonify({'success': True, 'category': decoded_name, 'total': float(total_spent)}), 200

    except Exception as e:
        print(f"Get Category Total Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@expense_bp.route('/summary', methods=['GET'])
@token_required
def get_expense_summary(current_user_id):
    try:
        user_id_int = int(current_user_id)
        user = User.query.get(user_id_int)
        total_budget = float(user.totalBudget or 0.0) if user else 0.0

        # Calculate Total Expenses
        total_spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id_int,
            Expense.type != 'credit'
        ).scalar() or 0.0

        # Calculate Total Income
        total_income = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id_int,
            Expense.type == 'credit'
        ).scalar() or 0.0

        total_spent_val = float(total_spent)
        total_income_val = float(total_income)

        effective_budget = total_budget + total_income_val
        remaining_budget = effective_budget - total_spent_val

        return jsonify({
            'success': True,
            'summary': {
                'baseBudget': total_budget,
                'totalIncome': total_income_val,
                'effectiveBudget': effective_budget,
                'totalSpent': total_spent_val,
                'remainingBudget': remaining_budget
            }
        }), 200

    except Exception as e:
        print(f"Get Summary Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
