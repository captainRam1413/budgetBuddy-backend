import datetime
from sqlalchemy import inspect, text
from extensions import db

def init_db(app):
    with app.app_context():
        try:
            db.create_all()
            
            # Check if users table is missing isAdmin column and add it dynamically
            inspector = inspect(db.engine)
            if 'users' in inspector.get_table_names():
                columns = [c['name'] for c in inspector.get_columns('users')]
                if 'isAdmin' not in columns:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE users ADD COLUMN isAdmin BOOLEAN DEFAULT 0;"))
                        conn.commit()
                    print("🔄 Migration: Added missing 'isAdmin' column to users table.")

            # Auto-seed default admin account if no admin exists
            try:
                from models import User
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()
                
                admin = User.query.filter_by(isAdmin=True).first()
                if not admin:
                    now_iso = datetime.datetime.utcnow().isoformat()
                    hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
                    default_admin = User(
                        name='Admin User',
                        email='admin@budgetbuddy.com',
                        password=hashed,
                        isAdmin=True,
                        totalBudget=0.0,
                        hasCompletedOnboarding=True,
                        budgetPeriod='monthly',
                        periodStartDate=now_iso,
                        createdAt=now_iso,
                        updatedAt=now_iso
                    )
                    db.session.add(default_admin)
                    db.session.commit()
                    print("🔑 Default admin user (admin@budgetbuddy.com) seeded.")
            except Exception as se:
                print(f"⚠️ Admin seed note: {se}")

            print("✅ Database tables created via SQLAlchemy ORM.")
        except Exception as e:
            print(f"⚠️ Warning during db initialization: {e}")


