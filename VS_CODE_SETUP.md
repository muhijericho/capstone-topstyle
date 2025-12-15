# Visual Studio Code Setup Guide

## Quick Start Commands

### 1. Open Terminal in VS Code
- Press `Ctrl + `` (backtick) or go to `Terminal > New Terminal`
- Make sure the terminal is set to **PowerShell** (not CMD)

### 2. Navigate to Project Directory (if not already there)
```powershell
cd C:\Users\vince\Videos\CAPSTONE_FINAL_SYSTEM\CAPSTONE2.0_CURSUR
```

### 3. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies (if needed)
```powershell
pip install -r requirements.txt
```

### 5. Run Database Migrations
```powershell
python manage.py migrate
```

### 6. Create Superuser (if needed)
```powershell
python manage.py createsuperuser
```

### 7. Start Django Development Server
```powershell
python manage.py runserver
```

The server will start at: **http://127.0.0.1:8000/**

---

## All-in-One Command Sequence

Run these commands one by one in VS Code terminal:

```powershell
cd C:\Users\vince\Videos\CAPSTONE_FINAL_SYSTEM\CAPSTONE2.0_CURSUR
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

---

## VS Code Python Extension Setup

1. Install Python extension if not already installed
2. Press `F1` and type "Python: Select Interpreter"
3. Choose: `.\venv\Scripts\python.exe`

---

## Running the Server on a Different Port

```powershell
python manage.py runserver 8080
```

---

## Troubleshooting

### If virtual environment is not activated:
- You should see `(venv)` at the start of your terminal prompt
- If not, activate it with: `.\venv\Scripts\Activate.ps1`

### If port 8000 is already in use:
```powershell
python manage.py runserver 8001
```

### If you need to stop the server:
- Press `Ctrl + C` in the terminal

















