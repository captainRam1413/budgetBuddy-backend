from flask import Blueprint, request, jsonify
import datetime
from urllib.parse import unquote
from extensions import db
from models import Category
from auth import token_required

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@category_bp.route('/', methods=['GET'])
@token_required
def get_categories(current_user_id):
    try:
        categories = Category.query.filter_by(user_id=int(current_user_id)).all()
        return jsonify({'success': True, 'categories': [cat.to_dict() for cat in categories]}), 200

    except Exception as e:
        print(f"Get Categories Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@category_bp.route('/', methods=['POST'])
@token_required
def create_category(current_user_id):
    try:
        data = request.get_json() or {}
        name = str(data.get('name', '')).strip()
        icon = data.get('icon', '🎯')
        color = data.get('color', '#FFB347')
        budget = data.get('budget', 0.0)

        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'}), 400

        try:
            budget_val = float(budget) if budget else 0.0
        except ValueError:
            budget_val = 0.0

        user_id_int = int(current_user_id)
        existing = Category.query.filter_by(user_id=user_id_int, name=name).first()
        now_iso = datetime.datetime.utcnow().isoformat()

        if existing:
            existing.icon = icon
            existing.color = color
            existing.budget = budget_val
            existing.updatedAt = now_iso
            db.session.commit()
            return jsonify({'success': True, 'message': 'Category updated successfully', 'categoryId': str(existing.id)}), 200

        category = Category(
            user_id=user_id_int,
            name=name,
            icon=icon,
            color=color,
            budget=budget_val,
            createdAt=now_iso,
            updatedAt=now_iso
        )
        db.session.add(category)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Category created successfully', 'categoryId': str(category.id)}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Create Category Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@category_bp.route('/bulk', methods=['POST'])
@token_required
def create_multiple_categories(current_user_id):
    try:
        data = request.get_json() or {}
        categories = data.get('categories', [])

        if not isinstance(categories, list):
            return jsonify({'success': False, 'message': 'Categories must be a list'}), 400

        user_id_int = int(current_user_id)
        now_iso = datetime.datetime.utcnow().isoformat()
        created_count = 0

        for cat in categories:
            name = str(cat.get('name', '')).strip()
            if not name:
                continue

            icon = cat.get('icon', '🎯')
            color = cat.get('color', '#FFB347')
            budget = cat.get('budget', 0.0)
            try:
                budget_val = float(budget) if budget else 0.0
            except ValueError:
                budget_val = 0.0

            existing = Category.query.filter_by(user_id=user_id_int, name=name).first()
            if existing:
                existing.icon = icon
                existing.color = color
                existing.budget = budget_val
                existing.updatedAt = now_iso
            else:
                new_cat = Category(
                    user_id=user_id_int,
                    name=name,
                    icon=icon,
                    color=color,
                    budget=budget_val,
                    createdAt=now_iso,
                    updatedAt=now_iso
                )
                db.session.add(new_cat)
            created_count += 1

        db.session.commit()
        return jsonify({'success': True, 'message': f'{created_count} categories processed successfully', 'count': created_count}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Bulk Category Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@category_bp.route('/<category_name>/budget', methods=['PUT'])
@token_required
def update_category_budget(current_user_id, category_name):
    try:
        decoded_name = unquote(category_name).strip()
        data = request.get_json() or {}
        budget = data.get('budget')

        if budget is None:
            return jsonify({'success': False, 'message': 'Budget value is required'}), 400

        try:
            budget_val = float(budget)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid budget value'}), 400

        user_id_int = int(current_user_id)
        existing = Category.query.filter_by(user_id=user_id_int, name=decoded_name).first()
        now_iso = datetime.datetime.utcnow().isoformat()

        if existing:
            existing.budget = budget_val
            existing.updatedAt = now_iso
        else:
            new_cat = Category(
                user_id=user_id_int,
                name=decoded_name,
                icon='🎯',
                color='#FFB347',
                budget=budget_val,
                createdAt=now_iso,
                updatedAt=now_iso
            )
            db.session.add(new_cat)

        db.session.commit()
        return jsonify({'success': True, 'message': f'Budget updated for {decoded_name}'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update Category Budget Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@category_bp.route('/budgets/bulk', methods=['PUT'])
@token_required
def update_multiple_budgets(current_user_id):
    try:
        data = request.get_json() or {}
        budgets = data.get('budgets', {})

        if not isinstance(budgets, dict):
            return jsonify({'success': False, 'message': 'Budgets must be a map of category_name -> budget'}), 400

        user_id_int = int(current_user_id)
        now_iso = datetime.datetime.utcnow().isoformat()
        updated_count = 0

        for cat_name, budget_val in budgets.items():
            try:
                b_val = float(budget_val)
            except ValueError:
                continue

            name_clean = str(cat_name).strip()
            existing = Category.query.filter_by(user_id=user_id_int, name=name_clean).first()
            if existing:
                existing.budget = b_val
                existing.updatedAt = now_iso
            else:
                new_cat = Category(
                    user_id=user_id_int,
                    name=name_clean,
                    icon='🎯',
                    color='#FFB347',
                    budget=b_val,
                    createdAt=now_iso,
                    updatedAt=now_iso
                )
                db.session.add(new_cat)

            updated_count += 1

        db.session.commit()
        return jsonify({'success': True, 'message': f'Updated {updated_count} category budgets'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Bulk Update Budgets Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@category_bp.route('/<category_name>', methods=['DELETE'])
@token_required
def delete_category(current_user_id, category_name):
    try:
        decoded_name = unquote(category_name).strip()
        user_id_int = int(current_user_id)

        category = Category.query.filter_by(user_id=user_id_int, name=decoded_name).first()
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'}), 404

        db.session.delete(category)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Category {decoded_name} deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete Category Exception: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
