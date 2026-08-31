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

            print("✅ Database tables created via SQLAlchemy ORM.")
        except Exception as e:
            print(f"⚠️ Warning during db initialization: {e}")

