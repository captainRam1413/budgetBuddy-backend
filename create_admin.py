import sys
import datetime
from app import create_app
from extensions import db
from models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_admin(name, email, password, phone=''):
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(email=email.lower().strip()).first()
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        now_iso = datetime.datetime.utcnow().isoformat()

        if existing:
            existing.name = name
            existing.password = hashed
            existing.isAdmin = True
            existing.updatedAt = now_iso
            db.session.commit()
            print(f"✅ User '{email}' was updated to Admin successfully!")
        else:
            admin_user = User(
                name=name,
                email=email.lower().strip(),
                phone=phone,
                password=hashed,
                isAdmin=True,
                totalBudget=0.0,
                hasCompletedOnboarding=True,
                budgetPeriod='monthly',
                periodStartDate=now_iso,
                createdAt=now_iso,
                updatedAt=now_iso
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"🎉 Admin user '{email}' created successfully!")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <name> <email> <password> [phone]")
        sys.exit(1)

    name_arg = sys.argv[1]
    email_arg = sys.argv[2]
    pass_arg = sys.argv[3]
    phone_arg = sys.argv[4] if len(sys.argv) > 4 else ''

    create_admin(name_arg, email_arg, pass_arg, phone_arg)
