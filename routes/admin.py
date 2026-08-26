import datetime
from flask import Blueprint, request, jsonify, render_template_string
from sqlalchemy import text, inspect, func
from extensions import db
from models import User, Category, Expense, AuditLog
from auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

FULL_DATABASE_STUDIO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BudgetBuddy Admin & Database Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #090d16;
            --bg-panel: #111726;
            --bg-editor: #161e31;
            --border: rgba(255, 255, 255, 0.08);
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* CUSTOM MODERN SCROLLBARS FOR ALL PANELS AND TABLES */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.6);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.4);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.7);
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* LOGIN OVERLAY */
        #loginOverlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(9, 13, 22, 0.96);
            backdrop-filter: blur(24px);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .login-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.7);
        }

        .login-card h2 {
            font-size: 24px;
            font-weight: 800;
            text-align: center;
            background: linear-gradient(135deg, #6366f1, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .input-group label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
        }

        .input-field {
            background: var(--bg-dark);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 16px;
            color: #fff;
            font-size: 14px;
            outline: none;
        }

        .input-field:focus {
            border-color: var(--accent);
        }

        /* TOPBAR NAVIGATION & TABS */
        .topbar {
            height: 58px;
            background: var(--bg-panel);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
        }

        .brand-container {
            display: flex;
            align-items: center;
            gap: 24px;
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 800;
            font-size: 18px;
        }

        .brand-logo span {
            background: linear-gradient(135deg, #6366f1, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-tabs {
            display: flex;
            gap: 8px;
        }

        .tab-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .tab-btn:hover {
            color: #fff;
            background: rgba(255, 255, 255, 0.04);
        }

        .tab-btn.active {
            background: rgba(99, 102, 241, 0.15);
            color: #fff;
            border-color: rgba(99, 102, 241, 0.3);
        }

        .db-badge {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .btn-action {
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-action:hover {
            background: var(--accent-hover);
        }
        .btn-secondary {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
        }

        /* MAIN VIEWPORT */
        .viewport {
            flex: 1;
            position: relative;
            overflow: hidden;
        }

        .page-view {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: none;
            flex-direction: column;
            overflow-y: auto;
            padding: 24px 32px;
        }

        .page-view.active {
            display: flex;
        }

        /* VIEW 1: DASHBOARD ANALYTICS */
        .dash-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }

        .dash-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .dash-card .title {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 600;
        }

        .dash-card .val {
            font-size: 32px;
            font-weight: 800;
            color: #fff;
        }

        .card-container {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 28px;
        }

        .card-header-flex {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .card-header-flex h3 {
            font-size: 18px;
            font-weight: 700;
        }

        /* VIEW 2: DATABASE STUDIO WORKSPACE */
        #viewStudio {
            padding: 0;
            flex-direction: row;
            overflow: hidden;
        }

        .explorer-sidebar {
            width: 280px;
            background: var(--bg-panel);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }

        .explorer-title {
            padding: 14px 18px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .tables-list {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .table-item {
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s;
        }

        .table-item:hover {
            background: rgba(99, 102, 241, 0.15);
            color: #fff;
        }

        .table-item .count {
            background: var(--bg-dark);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            color: var(--text-muted);
        }

        .studio-workspace {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-dark);
            overflow: hidden;
        }

        .sql-editor-panel {
            height: 40%;
            background: var(--bg-editor);
            border-bottom: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }

        .sql-toolbar {
            height: 44px;
            background: var(--bg-panel);
            border-bottom: 1px solid var(--border);
            padding: 0 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .sql-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            padding: 16px;
            color: #a5b4fc;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: none;
        }

        .grid-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .grid-bar {
            height: 38px;
            background: var(--bg-panel);
            border-bottom: 1px solid var(--border);
            padding: 0 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
        }

        /* AG-GRID STYLE DATABASE TABLES WITH BOTH VERTICAL AND HORIZONTAL SCROLLBARS */
        .table-scroll-wrapper {
            flex: 1;
            overflow: auto; /* ENABLE BOTH HORIZONTAL AND VERTICAL SCROLLBARS */
            max-width: 100%;
            max-height: 100%;
        }

        table.studio-table {
            width: max-content; /* ALLOW TABLE TO EXPAND FOR LONG ROWS */
            min-width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            font-family: 'JetBrains Mono', monospace;
        }

        table.studio-table th {
            position: sticky;
            top: 0;
            background: #192235;
            padding: 12px 18px;
            color: var(--text-muted);
            font-weight: 700;
            border-bottom: 1px solid var(--border);
            border-right: 1px solid var(--border);
            text-align: left;
            white-space: nowrap;
            z-index: 10;
        }

        table.studio-table td {
            padding: 10px 18px;
            border-bottom: 1px solid var(--border);
            border-right: 1px solid var(--border);
            color: var(--text-main);
            white-space: nowrap; /* PRESERVE LONG ROWS WITH HORIZONTAL SCROLLING */
            max-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        table.studio-table tr:hover td {
            background: rgba(99, 102, 241, 0.12);
        }

        .badge-role {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }
        .badge-admin {
            background: rgba(99, 102, 241, 0.2);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.4);
        }
        .badge-user {
            background: rgba(148, 163, 184, 0.15);
            color: #cbd5e1;
        }

        .output-message {
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #34d399;
        }

        .output-message.error {
            color: #f87171;
        }
    </style>
</head>
<body>

    <!-- LOGIN MODAL OVERLAY -->
    <div id="loginOverlay">
        <form class="login-card" onsubmit="handleLogin(event)">
            <h2>🔑 Database Studio Login</h2>
            <div class="input-group">
                <label>Admin Email</label>
                <input type="email" id="email" class="input-field" value="admin@budgetbuddy.com" required />
            </div>
            <div class="input-group">
                <label>Admin Password</label>
                <input type="password" id="password" class="input-field" value="admin123" required />
            </div>
            <button type="submit" class="btn-action" style="justify-content: center; padding: 14px;">Connect to Studio</button>
            <div id="loginErr" style="color: #f87171; font-size: 12px; text-align: center; display: none;"></div>
        </form>
    </div>

    <!-- TOPBAR -->
    <div class="topbar">
        <div class="brand-container">
            <div class="brand-logo">
                ⚡ <span>BudgetBuddy Studio</span>
            </div>
            <div class="nav-tabs">
                <button class="tab-btn active" id="tabDash" onclick="switchPage('dash')">📊 Overview Dashboard</button>
                <button class="tab-btn" id="tabStudio" onclick="switchPage('studio')">🗄️ Web Database Studio</button>
                <button class="tab-btn" id="tabConfig" onclick="switchPage('config')">⚙️ Dynamic UI Configurator</button>
            </div>
        </div>

        <div style="display: flex; align-items: center; gap: 16px;">
            <span class="db-badge">SQLite Database (SQLAlchemy ORM)</span>
            <button class="btn-action btn-secondary" onclick="logout()">Logout</button>
        </div>
    </div>

    <!-- VIEWPORT PAGE VIEWS -->
    <div class="viewport">

        <!-- PAGE 1: OVERVIEW DASHBOARD -->
        <div class="page-view active" id="viewDash">
            <div class="dash-grid">
                <div class="dash-card">
                    <span class="title">Total Active Users</span>
                    <span class="val" id="dashUsers">-</span>
                </div>
                <div class="dash-card">
                    <span class="title">Budget Categories</span>
                    <span class="val" id="dashCategories">-</span>
                </div>
                <div class="dash-card">
                    <span class="title">Expenses Logged</span>
                    <span class="val" id="dashExpenses">-</span>
                </div>
                <div class="dash-card">
                    <span class="title">Database Tables</span>
                    <span class="val" id="dashTables">-</span>
                </div>
            </div>

            <!-- USERS TABLE -->
            <div class="card-container">
                <div class="card-header-flex">
                    <h3>👥 Registered Users</h3>
                </div>
                <div class="table-scroll-wrapper" style="max-height: 320px;">
                    <table class="studio-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Total Budget</th>
                                <th>Period</th>
                                <th>Created At</th>
                            </tr>
                        </thead>
                        <tbody id="dashUsersBody">
                            <tr><td colspan="7" style="text-align: center;">Loading user records...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- PAGE 2: WEB DATABASE STUDIO -->
        <div class="page-view" id="viewStudio">
            <!-- LEFT EXPLORER -->
            <div class="explorer-sidebar">
                <div class="explorer-title">
                    <span>Database Explorer</span>
                    <span onclick="loadTablesSchema()" style="cursor: pointer;" title="Refresh Schema">🔄</span>
                </div>
                <div class="tables-list" id="explorerTables">
                    <div style="color: var(--text-muted); font-size: 12px;">Loading tables...</div>
                </div>
            </div>

            <!-- RIGHT STUDIO WORKSPACE -->
            <div class="studio-workspace">
                <!-- SQL EDITOR -->
                <div class="sql-editor-panel">
                    <div class="sql-toolbar">
                        <button class="btn-action" onclick="runQuery()">▶ Run SQL Query (Ctrl+Enter)</button>
                        <button class="btn-action btn-secondary" onclick="setQuery('SELECT * FROM users;')">Users</button>
                        <button class="btn-action btn-secondary" onclick="setQuery('SELECT * FROM categories;')">Categories</button>
                        <button class="btn-action btn-secondary" onclick="setQuery('SELECT * FROM expenses;')">Expenses</button>
                        <button class="btn-action btn-secondary" onclick="setQuery('SELECT * FROM audit_logs;')">Audit Logs</button>
                        <button class="btn-action btn-secondary" onclick="clearEditor()">Clear</button>
                    </div>
                    <textarea class="sql-input" id="sqlEditor" placeholder="-- Write SQL query here&#10;SELECT * FROM users LIMIT 50;"></textarea>
                </div>

                <!-- GRID WITH BOTH HORIZONTAL & VERTICAL SCROLLBARS FOR LONG ROWS -->
                <div class="grid-panel">
                    <div class="grid-bar">
                        <span id="gridTitle">Data Grid View</span>
                        <span id="gridCount">0 rows</span>
                    </div>
                    <div class="table-scroll-wrapper" id="gridWrapper">
                        <div class="output-message">Select a table from the sidebar or type a query above to view records.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- PAGE 3: DYNAMIC SCREEN CONFIGURATOR -->
        <div class="page-view" id="viewConfig">

            <!-- CARD 1: CREATE / EDIT SCREEN -->
            <div class="card-container">
                <div class="card-header-flex">
                    <h3>✨ Create Dynamic Screen</h3>
                </div>
                <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 16px;">
                    Define a screen with its UI components as JSON. The frontend renders whatever you define here — no code changes needed.
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px;">
                    <div class="input-group">
                        <label>Screen Key</label>
                        <input type="text" id="scrKey" class="input-field" placeholder="e.g. SubscriptionTracker" />
                    </div>
                    <div class="input-group">
                        <label>Title</label>
                        <input type="text" id="scrTitle" class="input-field" placeholder="e.g. My Subscriptions" />
                    </div>
                    <div class="input-group">
                        <label>Icon</label>
                        <input type="text" id="scrIcon" class="input-field" value="📱" style="width: 80px;" />
                    </div>
                </div>
                <div class="input-group" style="margin-bottom: 16px;">
                    <label>Description</label>
                    <input type="text" id="scrDesc" class="input-field" placeholder="Short description of the screen" />
                </div>
                <div class="input-group" style="margin-bottom: 8px;">
                    <label>Fields Config (JSON) — supported types: <code style="color: #a5b4fc;">text, number, date, checkbox, textarea, select</code></label>
                    <textarea id="scrFields" class="sql-input" style="height: 140px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-dark);" placeholder='[
  {"key": "name", "label": "Service Name", "type": "text", "required": true},
  {"key": "amount", "label": "Amount", "type": "number"},
  {"key": "due_date", "label": "Due Date", "type": "date"},
  {"key": "category", "label": "Category", "type": "select", "options": ["Entertainment","Utility","SaaS"]},
  {"key": "auto_renew", "label": "Auto Renew?", "type": "checkbox"}
]'></textarea>
                </div>
                <button class="btn-action" onclick="saveScreen()">💾 Save Screen</button>
                <span id="scrMsg" style="margin-left: 12px; font-size: 13px; color: #34d399;"></span>
            </div>

            <!-- CARD 2: ASSIGN SCREENS TO USERS -->
            <div class="card-container">
                <div class="card-header-flex">
                    <h3>👥 Assign Screens to Users</h3>
                </div>
                <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                    <div class="input-group" style="flex: 1;">
                        <label>Select Screen</label>
                        <select id="assignScreen" class="input-field" onchange="loadScreenAccess()"></select>
                    </div>
                </div>
                <div id="userCheckboxes" style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;"></div>
                <button class="btn-action" onclick="saveAccess()">Save Access</button>
                <span id="accessMsg" style="margin-left: 12px; font-size: 13px; color: #34d399;"></span>
            </div>

            <!-- CARD 3: EXISTING SCREENS LIST -->
            <div class="card-container">
                <div class="card-header-flex">
                    <h3>📋 Registered Screens</h3>
                    <button class="btn-action btn-secondary" onclick="loadScreensList()">🔄 Refresh</button>
                </div>
                <div id="screensList"></div>
            </div>
        </div>

    </div>

    <script>
        let token = localStorage.getItem('studioToken') || '';

        if (token) {
            document.getElementById('loginOverlay').style.display = 'none';
            fetchDashboardMetrics();
            loadTablesSchema();
        }

        async function handleLogin(e) {
            e.preventDefault();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const errBox = document.getElementById('loginErr');

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success && data.user && data.user.isAdmin) {
                    token = data.token;
                    localStorage.setItem('studioToken', token);
                    document.getElementById('loginOverlay').style.display = 'none';
                    fetchDashboardMetrics();
                    loadTablesSchema();
                } else {
                    errBox.innerText = data.message || 'Access Denied: Admin rights required!';
                    errBox.style.display = 'block';
                }
            } catch (err) {
                errBox.innerText = 'Connection Error: ' + err.message;
                errBox.style.display = 'block';
            }
        }

        function logout() {
            localStorage.removeItem('studioToken');
            token = '';
            document.getElementById('loginOverlay').style.display = 'flex';
        }

        function switchPage(page) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.page-view').forEach(v => v.classList.remove('active'));

            if (page === 'dash') {
                document.getElementById('tabDash').classList.add('active');
                document.getElementById('viewDash').classList.add('active');
                fetchDashboardMetrics();
            } else if (page === 'studio') {
                document.getElementById('tabStudio').classList.add('active');
                document.getElementById('viewStudio').classList.add('active');
                loadTablesSchema();
            } else if (page === 'config') {
                document.getElementById('tabConfig').classList.add('active');
                document.getElementById('viewConfig').classList.add('active');
                loadScreensList();
                loadAssignDropdowns();
            }
        }

        // ===== DYNAMIC SCREEN CONFIGURATOR JS =====
        let allScreens = [];
        let allUsers = [];

        async function loadAssignDropdowns() {
            // load screens
            try {
                const r1 = await fetch('/admin/api/screens', { headers: { 'Authorization': 'Bearer ' + token } });
                const d1 = await r1.json();
                if (d1.success) { allScreens = d1.screens; }
            } catch(e){}
            const sel = document.getElementById('assignScreen');
            sel.innerHTML = allScreens.map(s => `<option value="${s.id}">${s.icon} ${s.title} (${s.screen_key})</option>`).join('');

            // load users
            try {
                const r2 = await fetch('/admin/api/overview', { headers: { 'Authorization': 'Bearer ' + token } });
                const d2 = await r2.json();
                if (d2.success) { allUsers = d2.users; }
            } catch(e){}

            loadScreenAccess();
        }

        async function loadScreenAccess() {
            const screenId = document.getElementById('assignScreen').value;
            if (!screenId) return;
            let accessUserIds = [];
            try {
                const r = await fetch('/admin/api/screen-access/' + screenId, { headers: { 'Authorization': 'Bearer ' + token } });
                const d = await r.json();
                if (d.success) accessUserIds = d.user_ids;
            } catch(e){}

            const box = document.getElementById('userCheckboxes');
            box.innerHTML = allUsers.map(u => {
                const checked = accessUserIds.includes(parseInt(u.id)) ? 'checked' : '';
                return `<label style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;color:var(--text-main);background:rgba(255,255,255,0.03);padding:8px 14px;border-radius:8px;border:1px solid var(--border);">
                    <input type="checkbox" value="${u.id}" ${checked} style="width:16px;height:16px;accent-color:var(--accent);" />
                    <b>${u.name}</b> <span style="color:var(--text-muted)">(${u.email})</span>
                </label>`;
            }).join('');
        }

        async function saveAccess() {
            const screenId = document.getElementById('assignScreen').value;
            const checks = document.querySelectorAll('#userCheckboxes input[type=checkbox]:checked');
            const userIds = Array.from(checks).map(c => parseInt(c.value));
            const msg = document.getElementById('accessMsg');
            try {
                const r = await fetch('/admin/api/screen-access', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                    body: JSON.stringify({ screen_id: parseInt(screenId), user_ids: userIds })
                });
                const d = await r.json();
                msg.innerText = d.success ? '✅ Access saved!' : '❌ ' + d.message;
            } catch(e) { msg.innerText = '❌ ' + e.message; }
        }

        async function saveScreen() {
            const screen_key = document.getElementById('scrKey').value.trim();
            const title = document.getElementById('scrTitle').value.trim();
            const icon = document.getElementById('scrIcon').value.trim() || '📱';
            const description = document.getElementById('scrDesc').value.trim();
            const fieldsRaw = document.getElementById('scrFields').value.trim();
            const msg = document.getElementById('scrMsg');

            if (!screen_key || !title) { msg.innerText = '❌ Key & Title required'; return; }
            let fields_config = [];
            try { fields_config = JSON.parse(fieldsRaw); } catch(e) { msg.innerText = '❌ Invalid JSON: ' + e.message; return; }

            try {
                const r = await fetch('/admin/api/screens', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                    body: JSON.stringify({ screen_key, title, icon, description, fields_config })
                });
                const d = await r.json();
                if (d.success) {
                    msg.innerText = '✅ Screen saved!';
                    document.getElementById('scrKey').value = '';
                    document.getElementById('scrTitle').value = '';
                    document.getElementById('scrDesc').value = '';
                    document.getElementById('scrFields').value = '';
                    loadScreensList();
                    loadAssignDropdowns();
                } else { msg.innerText = '❌ ' + d.message; }
            } catch(e) { msg.innerText = '❌ ' + e.message; }
        }

        async function loadScreensList() {
            try {
                const r = await fetch('/admin/api/screens', { headers: { 'Authorization': 'Bearer ' + token } });
                const d = await r.json();
                if (!d.success) return;
                const box = document.getElementById('screensList');
                if (d.screens.length === 0) { box.innerHTML = '<div style="color:var(--text-muted);">No screens defined yet.</div>'; return; }
                box.innerHTML = d.screens.map(s => `
                    <div style="background:var(--bg-dark);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <b style="font-size:15px;">${s.icon} ${s.title}</b>
                            <code style="color:var(--text-muted);font-size:12px;">${s.screen_key}</code>
                        </div>
                        <div style="color:var(--text-muted);font-size:12px;margin-bottom:8px;">${s.description || ''}</div>
                        <div style="font-family:JetBrains Mono;font-size:11px;color:#a5b4fc;background:rgba(99,102,241,0.08);padding:8px;border-radius:8px;overflow-x:auto;white-space:pre;">${JSON.stringify(s.fields_config, null, 2)}</div>
                    </div>
                `).join('');
            } catch(e){}
        }

        async function editScreen(screenKey) {
            const s = allScreens.find(x => x.screen_key === screenKey);
            if (!s) return;
            document.getElementById('scrKey').value = s.screen_key;
            document.getElementById('scrTitle').value = s.title;
            document.getElementById('scrIcon').value = s.icon;
            document.getElementById('scrDesc').value = s.description;
            document.getElementById('scrFields').value = JSON.stringify(s.fields_config, null, 2);
            window.scrollTo(0, 0);
        }

        async function fetchDashboardMetrics() {
            try {
                const res = await fetch('/admin/api/overview', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                const data = await res.json();
                if (data.success) {
                    document.getElementById('dashUsers').innerText = data.stats.usersCount;
                    document.getElementById('dashCategories').innerText = data.stats.categoriesCount;
                    document.getElementById('dashExpenses').innerText = data.stats.expensesCount;
                    document.getElementById('dashTables').innerText = data.stats.tablesCount;

                    const tbody = document.getElementById('dashUsersBody');
                    tbody.innerHTML = '';
                    data.users.forEach(u => {
                        tbody.innerHTML += `
                            <tr>
                                <td>#${u.id}</td>
                                <td><b>${u.name}</b></td>
                                <td>${u.email}</td>
                                <td><span class="badge-role ${u.isAdmin ? 'badge-admin' : 'badge-user'}">${u.isAdmin ? 'ADMIN' : 'USER'}</span></td>
                                <td>₹${u.totalBudget}</td>
                                <td>${u.budgetPeriod}</td>
                                <td>${u.createdAt ? u.createdAt.substring(0, 10) : ''}</td>
                            </tr>
                        `;
                    });
                } else {
                    logout();
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function loadTablesSchema() {
            try {
                const res = await fetch('/admin/api/schema-tables', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                const data = await res.json();
                if (data.success) {
                    const list = document.getElementById('explorerTables');
                    list.innerHTML = '';
                    data.tables.forEach(t => {
                        list.innerHTML += `
                            <div class="table-item" onclick="inspectTable('${t.name}')">
                                <span>📋 ${t.name}</span>
                                <span class="count">${t.count}</span>
                            </div>
                        `;
                    });
                }
            } catch (err) {
                console.error(err);
            }
        }

        function inspectTable(tableName) {
            setQuery(`SELECT * FROM ${tableName} LIMIT 100;`);
            runQuery();
        }

        function setQuery(q) {
            document.getElementById('sqlEditor').value = q;
        }

        function clearEditor() {
            document.getElementById('sqlEditor').value = '';
        }

        document.getElementById('sqlEditor').addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                runQuery();
            }
        });

        async function runQuery() {
            const query = document.getElementById('sqlEditor').value.trim();
            const gridWrapper = document.getElementById('gridWrapper');
            const gridTitle = document.getElementById('gridTitle');
            const gridCount = document.getElementById('gridCount');

            if (!query) return;

            gridWrapper.innerHTML = '<div class="output-message">Executing SQL query...</div>';

            try {
                const res = await fetch('/admin/api/execute-sql', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token
                    },
                    body: JSON.stringify({ query })
                });

                const data = await res.json();

                if (data.success) {
                    if (data.is_select) {
                        gridTitle.innerText = 'SELECT Query Result';
                        gridCount.innerText = `${data.rows.length} rows returned`;

                        if (data.rows.length === 0) {
                            gridWrapper.innerHTML = '<div class="output-message">Query returned 0 rows.</div>';
                            return;
                        }

                        let tableHtml = '<table class="studio-table"><thead><tr>';
                        data.columns.forEach(c => tableHtml += `<th>${c}</th>`);
                        tableHtml += '</tr></thead><tbody>';

                        data.rows.forEach(r => {
                            tableHtml += '<tr>';
                            data.columns.forEach(c => {
                                tableHtml += `<td title="${r[c] !== null ? r[c] : ''}">${r[c] !== null ? r[c] : '<i style="color: #64748b;">NULL</i>'}</td>`;
                            });
                            tableHtml += '</tr>';
                        });

                        tableHtml += '</tbody></table>';
                        gridWrapper.innerHTML = tableHtml;
                    } else {
                        gridTitle.innerText = 'Statement Execution Result';
                        gridCount.innerText = `${data.affected_rows} rows affected`;
                        gridWrapper.innerHTML = `<div class="output-message">Statement executed successfully. Affected rows: ${data.affected_rows}</div>`;
                        loadTablesSchema();
                    }
                } else {
                    gridWrapper.innerHTML = `<div class="output-message error">SQL Error: ${data.message}</div>`;
                }
            } catch (err) {
                gridWrapper.innerHTML = `<div class="output-message error">Execution Error: ${err.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@admin_bp.route('/', methods=['GET'])
def admin_panel():
    return render_template_string(FULL_DATABASE_STUDIO_HTML)


@admin_bp.route('/api/overview', methods=['GET'])
@admin_required
def admin_overview(current_user_id):
    try:
        users_count = User.query.count()
        categories_count = Category.query.count()
        expenses_count = Expense.query.count()

        inspector = inspect(db.engine)
        tables_count = len(inspector.get_table_names())

        users = User.query.order_by(User.id.asc()).all()

        return jsonify({
            'success': True,
            'stats': {
                'usersCount': users_count,
                'categoriesCount': categories_count,
                'expensesCount': expenses_count,
                'tablesCount': tables_count
            },
            'users': [u.to_dict() for u in users]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/schema-tables', methods=['GET'])
@admin_required
def get_schema_tables(current_user_id):
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        tables_data = []
        for t in tables:
            count = db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            tables_data.append({'name': t, 'count': count})

        return jsonify({'success': True, 'tables': tables_data}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/execute-sql', methods=['POST'])
@admin_required
def execute_sql(current_user_id):
    try:
        data = request.get_json() or {}
        sql_query = str(data.get('query', '')).strip()

        if not sql_query:
            return jsonify({'success': False, 'message': 'SQL query string is required'}), 400

        result = db.session.execute(text(sql_query))

        is_select = sql_query.lower().startswith('select') or sql_query.lower().startswith('pragma') or sql_query.lower().startswith('explain')

        if is_select:
            columns = list(result.keys())
            rows_data = [dict(row._mapping) for row in result.fetchall()]

            # Log audit record
            try:
                log = AuditLog(user_id=int(current_user_id), action='EXECUTE_SELECT_SQL', details=sql_query[:500])
                db.session.add(log)
                db.session.commit()
            except Exception:
                pass

            return jsonify({
                'success': True,
                'is_select': True,
                'columns': columns,
                'rows': rows_data
            }), 200
        else:
            db.session.commit()

            # Log audit record
            try:
                log = AuditLog(user_id=int(current_user_id), action='EXECUTE_MUTATION_SQL', details=sql_query[:500])
                db.session.add(log)
                db.session.commit()
            except Exception:
                pass

            return jsonify({
                'success': True,
                'is_select': False,
                'affected_rows': result.rowcount
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


# ========= DYNAMIC SCREENS ADMIN API =========

@admin_bp.route('/api/screens', methods=['GET'])
@admin_required
def admin_get_screens(current_user_id):
    try:
        from models import DynamicScreen
        screens = DynamicScreen.query.all()
        return jsonify({'success': True, 'screens': [s.to_dict() for s in screens]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/screens', methods=['POST'])
@admin_required
def admin_save_screen(current_user_id):
    try:
        import json
        from models import DynamicScreen
        data = request.get_json() or {}
        screen_key = str(data.get('screen_key', '')).strip()
        title = str(data.get('title', '')).strip()
        icon = str(data.get('icon', '📱')).strip()
        description = str(data.get('description', '')).strip()
        fields_config = data.get('fields_config', [])

        if not screen_key or not title:
            return jsonify({'success': False, 'message': 'screen_key and title are required'}), 400

        fields_json = json.dumps(fields_config) if isinstance(fields_config, list) else str(fields_config)

        existing = DynamicScreen.query.filter_by(screen_key=screen_key).first()
        if existing:
            existing.title = title
            existing.icon = icon
            existing.description = description
            existing.fields_config = fields_json
        else:
            new_screen = DynamicScreen(
                screen_key=screen_key,
                title=title,
                icon=icon,
                description=description,
                fields_config=fields_json
            )
            db.session.add(new_screen)

        db.session.commit()
        return jsonify({'success': True, 'message': f'Screen "{title}" saved'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@admin_bp.route('/api/screen-access/<int:screen_id>', methods=['GET'])
@admin_required
def get_screen_access(current_user_id, screen_id):
    try:
        from models import UserScreenAccess
        entries = UserScreenAccess.query.filter_by(screen_id=screen_id).all()
        return jsonify({'success': True, 'user_ids': [e.user_id for e in entries]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/screen-access', methods=['POST'])
@admin_required
def save_screen_access(current_user_id):
    try:
        from models import UserScreenAccess
        data = request.get_json() or {}
        screen_id = data.get('screen_id')
        user_ids = data.get('user_ids', [])

        if not screen_id:
            return jsonify({'success': False, 'message': 'screen_id is required'}), 400

        # Delete existing access for this screen
        UserScreenAccess.query.filter_by(screen_id=int(screen_id)).delete()

        # Insert new access entries
        for uid in user_ids:
            db.session.add(UserScreenAccess(user_id=int(uid), screen_id=int(screen_id)))

        db.session.commit()
        return jsonify({'success': True, 'message': f'Access updated for {len(user_ids)} users'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400



