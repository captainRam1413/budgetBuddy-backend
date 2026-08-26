
import datetime
import json
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), default='')
    password = db.Column(db.String(255), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)
    totalBudget = db.Column(db.Float, default=0.0)
    hasCompletedOnboarding = db.Column(db.Boolean, default=False)
    budgetPeriod = db.Column(db.String(20), default='monthly')
    periodStartDate = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat())
    createdAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat())
    updatedAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat(), onupdate=lambda: datetime.datetime.utcnow().isoformat())

    # Relationships
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade='all, delete-orphan')
    screen_access = db.relationship('UserScreenAccess', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        user_id_str = str(self.id)
        return {
            'id': user_id_str,
            '$id': user_id_str,
            'name': self.name,
            'email': self.email,
            'phone': self.phone or '',
            'isAdmin': bool(self.isAdmin),
            'totalBudget': float(self.totalBudget or 0.0),
            'hasCompletedOnboarding': bool(self.hasCompletedOnboarding),
            'budgetPeriod': self.budgetPeriod or 'monthly',
            'periodStartDate': self.periodStartDate or datetime.datetime.utcnow().isoformat(),
            '$createdAt': self.createdAt or '',
            '$updatedAt': self.updatedAt or ''
        }


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), default='🎯')
    color = db.Column(db.String(50), default='#FFB347')
    budget = db.Column(db.Float, default=0.0)
    createdAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat())
    updatedAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat(), onupdate=lambda: datetime.datetime.utcnow().isoformat())

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='_user_category_uc'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'icon': self.icon or '🎯',
            'color': self.color or '#FFB347',
            'budget': float(self.budget or 0.0)
        }


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    icon = db.Column(db.String(50), default='💸')
    color = db.Column(db.String(50), default='#FFB347')
    date = db.Column(db.String(50), nullable=False, index=True)
    type = db.Column(db.String(20), default='debit')
    createdAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat())
    updatedAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat(), onupdate=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'amount': float(self.amount or 0.0),
            'category': self.category or 'Uncategorized',
            'icon': self.icon or '💸',
            'color': self.color or '#FFB347',
            'date': self.date or datetime.datetime.utcnow().isoformat(),
            'type': self.type or 'debit'
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default='')
    timestamp = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp
        }


class DynamicScreen(db.Model):
    """
    Admin-defined screen. fields_config is a JSON array of component definitions:
    [
      {"key": "service_name", "label": "Service Name", "type": "text", "required": true},
      {"key": "amount",       "label": "Amount",       "type": "number", "required": true},
      {"key": "due_date",     "label": "Due Date",     "type": "date"},
      {"key": "auto_renew",   "label": "Auto Renew",   "type": "checkbox"},
      {"key": "notes",        "label": "Notes",        "type": "textarea"}
    ]
    Supported types: text, number, date, checkbox, textarea, select
    For select, add "options": ["opt1", "opt2"]
    """
    __tablename__ = 'dynamic_screens'

    id = db.Column(db.Integer, primary_key=True)
    screen_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    icon = db.Column(db.String(50), default='📱')
    description = db.Column(db.String(255), default='')
    fields_config = db.Column(db.Text, nullable=False, default='[]')
    createdAt = db.Column(db.String(50), default=lambda: datetime.datetime.utcnow().isoformat())

    access_entries = db.relationship('UserScreenAccess', backref='screen', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        try:
            fields = json.loads(self.fields_config) if self.fields_config else []
        except Exception:
            fields = []
        return {
            'id': str(self.id),
            'screen_key': self.screen_key,
            'title': self.title,
            'icon': self.icon or '📱',
            'description': self.description or '',
            'fields_config': fields
        }


class UserScreenAccess(db.Model):
    """Simple link: which user can see which screen."""
    __tablename__ = 'user_screen_access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    screen_id = db.Column(db.Integer, db.ForeignKey('dynamic_screens.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'screen_id', name='_user_screen_access_uc'),
    )

