# ✅ TASKS – Tattoo Studio Management App (Python Only)

Step-by-step tasks to build the desktop app from scratch, combining frontend (Flet) and backend (Flask) development in parallel, with tips and suggestions.

---

## 🔧 INITIAL SETUP (Day 1)

1. **Project & Repo**
    
    - Initialize Git repository.
        
    - Create folder structure:
        
        ```
        tattoo_studio_app/
        ├── backend/     # Flask API
        ├── frontend/    # Flet UI
        ├── flows/       # Prefect workflows
        ├── plugins/     # Plugin modules
        ├── scripts/     # Build & helper scripts
        └── configs/     # .env.template, config.py
        ```
        
    - Add `.gitignore`, `.env.template`, initial `README.md`, `PLANNING.md`, `TASKS.md`.
        
2. **Virtual Environments & Dependencies**
    
    - Create `venv` for backend and frontend (`python -m venv venv`).
        
    - Install common requirements:
        
        ```bash
        pip install flet flask sqlalchemy flask-jwt-extended python-dotenv prefect llama-cpp-python langchain qrcode opencv-python reportlab
        ```
        
    - Freeze into `requirements.txt`.
        
3. **Basic Config & Logging**
    
    - Create `configs/config.py` using Pydantic BaseSettings.
        
    - Setup Python `logging` in both backend and frontend.
        

> **Tip**: Keep secret keys and DB paths in `.env`, load in `config.py`.

---

## 🖥️ FIRST MVP – AUTHENTICATION & LAYOUT (Day 2–3)

Parallel tasks ensure UI and API align.

|Step|Frontend (Flet)|Backend (Flask)|
|---|---|---|
|1|Create `main.py`, initialize Flet App|Create `app.py`, initialize Flask App|
|2|Build login page UI (email, password)|Implement `/auth/login` and `/auth/register`|
|3|Add navigation shell (Sidebar/Tabs)|Create User model (`id`, `email`, `password`, `role`) with SQLAlchemy|
|4|Store JWT in app state|Setup `flask-jwt-extended` and permission decorators|
|5|Redirect to dashboard if authenticated|Write login tests (`pytest`)|

> **Suggestion**: Test login flow manually before moving on.

---

## 👥 CLIENT MODULE (Day 4–5)

### Backend

- Create `Client` model: fields `name`, `phone`, `address`, `allergies`, `medical_info`, `qr_id`.
    
- CRUD endpoints: `/clients/` (GET, POST), `/clients/<id>/` (GET, PUT, DELETE).
    
- Route to generate QR code image: `/clients/<id>/qrcode`.
    
- Endpoint to receive form POST: `/clients/submit/<qr_id>`.
    

### Frontend

- Build Clients list view: table or ListView.
    
- Client form page: bind to backend schema.
    
- Button to fetch and display QR code (calls `/qrcode`).
    
- Embed `flet.WebView` for client form (optional).
    

> **Tip**: Use `qrcode` lib on backend to generate PNG and serve as Base64.

---

## 📅 SCHEDULING MODULE (Day 6–7)

### Backend

- Define `Session` model: `client_id`, `artist_id`, `date`, `status`.
    
- CRUD endpoints for `/sessions/`.
    
- API to fetch all sessions within date range.
    

### Frontend

- Add Calendar control: `ft.Calendar` with `events` from backend.
    
- Implement day-click handler to create session.
    
- Drag & drop events: update via `/sessions/<id>/` PUT.
    

> **Suggestion**: Keep UI state minimal; always refresh from API after changes.

---

## 🧾 FINANCE & DASHBOARD (Day 8–9)

### Backend

- Endpoint `/finance/summary`: totals by day, month.
    
- Endpoint `/finance/report`: historical data list.
    

### Frontend

- Dashboard page: cards for key metrics.
    
- Chart component: `ft.LineChart` using data from `/finance/summary`.
    
- Table of transactions with filter controls.
    

> **Tip**: Use `pandas` in backend to compute rolling averages or summaries.

---

## 🛒 INVENTORY & CASH REGISTER (Day 10–11)

### Backend

- `Inventory` model: `name`, `quantity`, `unit`, `threshold`.
    
- Endpoints for `/inventory/` CRUD and movement log.
    
- `CashEntry` model: `amount`, `type`, `date`, `method`.
    
- Endpoints `/cash/entries` and `/cash/close`.
    

### Frontend

- Inventory page: CRUD form and alerts when `quantity <= threshold`.
    
- Cash register UI: entry form, method selector, close-day button triggers CSV/PDF export.
    

> **Suggestion**: Export CSV via `flask.send_file` and PDF via `reportlab`.

---

## 💾 BACKUP & RECOVERY (Day 12)

### Automation (Prefect)

- Flow `backup_db()`: copies `data.db` to `backups/YYYYMMDD.db` daily.
    
- Flow `zip_backup()`: archives backup folder into ZIP.
    

### Frontend

- Admin settings page: buttons to trigger backup and restore.
    
- Progress indicators during backup.
    

> **Tip**: Keep backups small; rotate old backups automatically.

---

## 🔒 SECURITY & PERMISSIONS (Day 13)

- Enforce JWT authentication on all routes.
    
- Decorators for role checks (`@admin_required`).
    
- Secure storage of JWT and secrets.
    
- Throttle requests to sensitive endpoints.
    

---

## 🧩 PLUGIN SYSTEM (Day 15)

- Scan `/plugins` folder at startup.
    
- Each plugin defines `register(app, ui)` function.
    
- Example plugin: `tattoo_ideas.py` shows image gallery.
    

---

## 📦 PACKAGING & DEPLOYMENT (Day 16)

1. **PyInstaller Build**
    
    ```bash
    pyinstaller --onefile --add-data "frontend;frontend" --add-data "app;app" main.py
    ```
    
2. **Zip Distribution**
    
    - Combine executable and `backups/`, `plugins/`, `static/` into `release.zip`.
        
3. **Test**
    
    - Validate full offline run on clean machine.
        

> **Tip**: Exclude dev dependencies to reduce bundle size.

---

## 🧪 TESTING & QA (Ongoing)

- Write `pytest` tests for CRUD and auth.
    
- Manual UI validation at each milestone.
    
- Test backup/restore on both Windows and macOS.
    
- Verify plugin load/unload functionality.
    

---

## 🚩 PRIORITY & MILESTONES

1. Authentication & Layout
    
2. Client Onboarding + QR Workflow
    
3. Session Scheduling
    
4. Finance Dashboard
    
5. Inventory + Cash Register
    
6. Backup & Admin Tools
    
7. Packaging & Distribution
    

---

**Start each day by reviewing previous tasks and writing commit messages reflecting completed features.**