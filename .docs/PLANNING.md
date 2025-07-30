# PLANNING.md – Tattoo Studio Management System (Python Desktop App)

## 🧠 Project Goal

Build a **professional, offline-first desktop application** for managing tattoo studios using only Python technologies. The system includes scheduling, client and artist management, inventory, finance, reports, data backup, local AI assistance, and user authentication — all packaged as a standalone executable via PyInstaller.

---

## 🧱 Architecture Overview

### Core Stack

| Layer         | Technology               | Purpose                                 |
|---------------|---------------------------|------------------------------------------|
| Backend       | Flask + SQLAlchemy       | API layer and business logic             |
| Frontend      | Flet                     | Desktop UI (cross-platform)              |
| Database      | SQLite                   | Lightweight embedded DB                  |
| Automation    | Prefect                  | Scheduled tasks (backup, alerts, etc.)   |
| Packaging     | PyInstaller              | Executable generation (no install)       |

---

## 🧩 System Modules

### 1. Authentication & Permissions
- Login system with `Flask-Login`
- Role-based access: **Admin** vs **Employee**
- Restricted actions by role

### 2. Client Management
- Full registration (contact, allergies, medical conditions)
- QR Code per client (generate + scan)
- Self-registration form via smartphone (served by Flask)
- Automatic sync of form data into the system
- Digital signature capture for consent forms
- PDF generation of signed documents

### 3. Session Scheduling
- Calendar view with per-artist filtering
- Drag & drop scheduling (Flet gestures)
- Session statuses (planned, in progress, done)
- Notifications for pending sessions

### 4. Artist Management
- Artist profile and portfolio gallery (GridView)
- Artist session history
- Signature input on screen

### 5. Inventory Control
- CRUD for materials (inks, needles, gloves, etc.)
- QR code scanning via OpenCV
- Low-stock alerts (background monitor)

### 6. Finance Module
- Session-based revenue tracking
- Categorized input/output (service, product, others)
- Pandas-powered reporting
- Matplotlib/Plotly charts displayed in Flet

### 7. Daily Cash Register
- Manual entry of payments and expenses
- Cash closure system
- Multi-payment type support
- Export CSV/PDF per day

### 8. Reports & Dashboard
- Visual overview of financial data
- Filterable reports by date, artist, client
- Usage analytics (most frequent clients, peak hours)

### 9. Backup & Restore
- Automatic daily backup to local folder
- Manual export to pendrive (.zip/.tar.gz)
- Restore via simple UI option

### 10. Optional Remote Sync
- Optional sync layer for future online backup/sync
- Encrypt and push updates when internet is available
- Useful for multi-branch studios or remote support

### 11. Plugin System
- Modules dynamically loaded from `/plugins`
- Easy to extend: just drop Python files in the folder
- Sample plugins: WhatsApp reminder, CSV importer

---

## ⚙️ Tools & Libraries

### Backend – Flask
- `Flask-SQLAlchemy`
- `Flask-Login`
- `Flask-CORS`
- `python-dotenv`

### Frontend – Flet
- Flet core widgets (ListView, Calendar, Forms)
- `flet_contrib` for advanced UI components


### Utility
- `qrcode`, `opencv-python` for QR
- `pytesseract` for receipt OCR
- `reportlab` / `fpdf` for PDF generation
- `zipfile`, `shutil`, `tarfile` for backup

---

## 🧪 Testing Strategy

### Backend
- `pytest` with Flask client fixtures
- Use SQLite in-memory for isolated tests

### Frontend
- `pytest-flet` (custom component testing)
- Snapshot / screenshot testing

### Integration
- Mock API responses for AI
- Simulate offline-only operation

---

## 📦 Packaging

```bash
pyinstaller --onefile --windowed \
  --add-data "assets;assets" \
  --add-data "app/ui;ui" \
  --add-data "app/server;server" \
  main.py

````

---

**Deliverable**:

- `.exe` for Windows or `.app` for macOS
    
- No installer needed — unzip and run
    
    

---

## 🧮 Data Models (simplified)

````
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    allergies = db.Column(db.Text)
    medical_issues = db.Column(db.Text)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    date = db.Column(db.DateTime)
    status = db.Column(db.String)
`````

---

## ✅ System Constraints

- 100% Offline by default (no internet required)
    
- Zero Node.js or JS dependencies
    
- Single executable file output
    
- Optional plugin and sync layers
    

---

## ✨ Key Benefits

1. **Python-only stack** → consistent dev workflow
    
2. **Cross-platform UI** → Windows/macOS/Linux
    
3. **Local-first philosophy** → total user control
    
4. **Modular architecture** → easy to expand
    

---

## 🚧 Development Steps

1. Design core models (Client, Session, Artist, etc.)
    
2. Build RESTful API with Flask
    
3. Build UI with Flet views
    
4. Add QR code flow and mobile client form
    
5. Add calendar/scheduler and finance logic
    
6. Build backup & restore logic
    
7. Add packaging + PyInstaller script
    
8. Write unit/integration tests
    
9. Add optional plugin loader and sync layer