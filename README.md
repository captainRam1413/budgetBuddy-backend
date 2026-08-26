# BudgetBuddy Backend API (Fully Dynamic Web Studio & Screen Builder)

High-performance, maintainable Flask backend API for **BudgetBuddy** equipped with a full **Web Database Studio**, **Analytics Dashboard**, and **Dynamic Screen & Field Builder**.

---

## 🏗️ Architecture & Structure

```
budgetBuddy-backend/
├── app.py                # Flask App Entry Point & Blueprint Registration
├── config.py             # SQLAlchemy Database URI & App Configurations
├── extensions.py         # SQLAlchemy Instance Singleton
├── models.py             # Declarative ORM Models (User, Category, Expense, AuditLog, DynamicScreenDefinition, UserUIConfig)
├── db.py                 # Table Creation, Schema Auto-Migrations & Default Screen Seeding
├── auth.py               # JWT Middleware & @admin_required Protection
├── create_admin.py       # CLI Script to Create / Promote Admin Users
├── routes/
│   ├── admin.py          # /admin Web Studio, Overview Dashboard, Dynamic Screen Builder & UI Configurator
│   ├── auth.py           # /api/auth (Register, Login)
│   ├── user.py           # /api/user (Profile, Budget, UI Configs & Dynamic Screen Definitions)
│   ├── category.py       # /api/categories (Single/Bulk Categories & Budgets)
│   └── expense.py        # /api/expenses (CRUD, Summary, Budget Validation)
├── requirements.txt      # Python Dependencies (Flask, Flask-SQLAlchemy, PyJWT, etc.)
├── instance/
│   └── budgetbuddy.db    # SQLite Database File
├── .env                  # Environment Configuration
└── README.md             # Setup Guide
```

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create Admin Account
```bash
python create_admin.py "Admin Name" "admin@budgetbuddy.com" "admin123"
```

### 3. Run Backend Server
```bash
python app.py
```
App runs at `http://localhost:5000`.

---

## 🗄️ Web Database Studio & Screen Builder (`/admin/`)

Access your web-based Database Studio & Configurator at:
`http://localhost:5000/admin/`

### Features:
1. **📊 Overview Dashboard**: Real-time metrics (users, categories, expenses logged, database tables) and registered user directory.
2. **🗄️ Web Database Studio**:
   - **Database Explorer**: Sidebar listing all dynamic SQLite tables (`users`, `categories`, `expenses`, `audit_logs`, `dynamic_screen_definitions`, `user_ui_configs`).
   - **Dual-Axis Scrollbars**: Full support for wide horizontal rows and long vertical query results without layout clipping.
3. **⚙️ Dynamic UI Configurator & Screen Builder**:
   - **Define New Screens**: Register completely new custom screens (e.g. `SubscriptionTracker`, `InvestmentPortfolio`) with custom field key definitions.
   - **Configure User Layouts**: Customize which screens and UI fields are enabled per user.
