# **Tattoo Studio Management – Offline Desktop App**

A fully offline, standalone desktop application for tattoo studio management. Built entirely in Python, using Flet for the UI, Flask for backend logic, and SQLite for local data storage. Designed for portability, privacy, and extensibility.

---

## 🧠 Core Architecture

````
[Flet UI] ↔ [Flask Backend] ↔ [SQLite Local DB]
     ↑            ↑
 [Local Tasks] ← [Prefect Automations]
                     ↑
         [Optional: LangChain + Llama.cpp]

`````

---

## 🛠️ Technology Stack

|Layer|Technology|Purpose|
|---|---|---|
|**Frontend**|Flet (Python)|Cross-platform native UI (desktop)|
|**Backend**|Flask|API logic and internal processing|
|**Database**|SQLite|Local embedded storage (portable)|
|**Automation**|Prefect|Orchestration for tasks and backups|
|**AI**|LangChain + Llama.cpp (opt.)|Offline AI capabilities (local LLM)|
|**Packaging**|PyInstaller|Executable ZIP with no external install|

---

## 🏗️ Project Structure

````
tattoo_studio_app/
├── app/
│   ├── ui/                 # Flet UI components
│   ├── api/                # Flask routes
│   ├── core/               # Configs, logging, constants
│   ├── db/                 # SQLite models and helpers
│   ├── logic/              # Business logic, services
│   └── ai/                 # LangChain setup (optional)
│
├── flows/                  # Prefect automations (e.g. backup)
├── static/                 # Icons, qrcode templates, etc
├── scripts/                # Build and zip utilities
├── Dockerfile              # Dev container (optional)
└── main.py                 # App entrypoint
`````

---

## 🚀 Main Features

- **Client Management**
    
    - Personal info, medical warnings, allergies
        
    - QR code generator for client self-registration
        
- **Session & Schedule Management**
    
    - Drag-and-drop calendar for sessions
        
    - Link sessions to clients
        
- **Daily Cash Register**
    
    - Record daily payments by method
        
    - Export to CSV or PDF
        
- **Dashboard & Financial Reports**
    
    - Graphs and stats for income, activity, etc.
        
- **Backup & Recovery**
    
    - Auto-local backups
        
    - Manual export to ZIP or USB
        
- **Authentication & Permissions**
    
    - Login with role-based access: admin or staff
        
- **Plugin System**
    
    - Add new modules via Python files (`/plugins` folder)
        
- **Sync-on-Connect Mode**
    
    - Runs 100% offline but can sync with cloud server (optional)
        

---

## 🔧 Development Setup

### Requirements

- Python 3.11+
    
- Flet
    
- Prefect (`pip install prefect`)
    
- LangChain + Llama.cpp (optional)
    

### Running the App

````
git clone https://github.com/youruser/tattoo-studio-app
cd tattoo-studio-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
`````

---

## 🧪 Testing Strategy

|Type|Tool|Notes|
|---|---|---|
|Unit|`pytest`|Core logic and models|
|UI snapshot|`pytest-flet`|(if used) Flet UI states|
|API|`FlaskClient`|Endpoints and responses|

---

## 🔄 Backup Flow (Prefect)

````
@flow
def backup_local_database():
    shutil.copy("db/database.sqlite", f"backups/{today()}.sqlite")

@flow
def zip_and_export_backup():
    shutil.make_archive("export/db_backup", 'zip', "db/")
`````

---

## 🔒 Authentication Example

````
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = validate_user(data["email"], data["password"])
    return {"token": create_jwt(user)}
`````


---

## 📦 Packaging

````
pyinstaller main.py --onefile --add-data="static;static"
# Output: dist/main.exe (or ELF/Mac binary)
`````
You can also zip the output folder for distribution.

---

## 🧩 Plugin System

1. Drop new `.py` module into `/plugins`
    
2. Detected and loaded dynamically by `main.py`
    
3. Allows extending system with:
    
    - New routes
        
    - UI components
        
    - Automations
        

---

## 🧠 AI Module (optional)

Powered by LangChain + Llama.cpp:

- Local LLM chat for recommendations
    
- No internet or external API required
    

---

## 📜 License

MIT License – Uses only open-source dependencies:

- Flask (MIT)
    
- Flet (BSD)
    
- SQLite (Public Domain)
    
- Prefect (Apache 2.0)
    
- LangChain (MIT)
    
- Llama.cpp (MIT)