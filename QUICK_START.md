# 🚀 QUICK START GUIDE
## One Command to Start Everything

---

## ⚡ THE ONE COMMAND

### For Windows (Recommended):
```batch
START_SYSTEM.bat
```
**Just double-click the file or run it from command prompt!**

### For Windows PowerShell:
```powershell
.\START_SYSTEM.ps1
```

### For Linux/Mac:
```bash
chmod +x START_SYSTEM.sh
./START_SYSTEM.sh
```

### Using Django Management Command:
```bash
python manage.py start_system
```

---

## 🎯 What It Does Automatically

The startup script will:

1. ✅ **Check Python Installation** - Verifies Python 3.8+ is installed
2. ✅ **Setup Virtual Environment** - Creates `venv` if it doesn't exist
3. ✅ **Install Dependencies** - Installs all packages from `requirements.txt`
4. ✅ **Check Database** - Verifies database connection
5. ✅ **Run Migrations** - Applies all database migrations
6. ✅ **Collect Static Files** - Prepares static files for serving
7. ✅ **Verify System** - Checks all components are ready
8. ✅ **Start Server** - Launches Django development server
9. ✅ **Open Browser** - Automatically opens http://127.0.0.1:8000

---

## 📋 Prerequisites

- **Python 3.8+** installed and in PATH
- **Database** configured in `settings.py`
- **Internet connection** (for first-time dependency installation)

---

## 🔧 Command Options

### Using the Management Command:

```bash
# Basic usage
python manage.py start_system

# Custom port
python manage.py start_system --port 8080

# Custom host
python manage.py start_system --host 0.0.0.0

# Don't open browser
python manage.py start_system --no-browser

# Skip migrations
python manage.py start_system --skip-migrations

# Skip static files
python manage.py start_system --skip-static

# Skip dependency check
python manage.py start_system --skip-deps
```

---

## 🎨 What You'll See

```
============================================================
  TopStyle Business Management System
  Complete System Startup
============================================================

Step 1: Checking Python installation...
✓ Python 3.11.0 found

Step 2: Checking virtual environment...
✓ Virtual environment found

Step 3: Checking dependencies...
✓ Dependencies check passed

Step 4: Checking database connection...
✓ Database connection successful

Step 5: Running database migrations...
✓ Migrations completed

Step 6: Collecting static files...
✓ Static files collected

Step 7: Verifying system...
✓ Django 4.2.0
✓ Database connection successful
✓ Settings loaded
✓ System verified and ready

============================================================
  Starting Development Server
============================================================

Server URL: http://127.0.0.1:8000
Press Ctrl+C to stop the server

✓ Browser opened at http://127.0.0.1:8000
```

---

## 🛑 Stopping the Server

Press **Ctrl+C** in the terminal/command prompt to stop the server.

---

## 🐛 Troubleshooting

### "Python is not installed"
- Install Python 3.8+ from https://www.python.org/
- Make sure Python is added to PATH during installation

### "Virtual environment creation failed"
- Make sure you have write permissions in the project directory
- Try running as administrator (Windows) or with sudo (Linux/Mac)

### "Dependencies installation failed"
- Check your internet connection
- Make sure `requirements.txt` exists
- Try installing manually: `pip install -r requirements.txt`

### "Database connection failed"
- Check your database settings in `settings.py`
- Make sure your database server is running
- Verify database credentials are correct

### "Port 8000 already in use"
- Use a different port: `python manage.py start_system --port 8001`
- Or stop the process using port 8000

### PowerShell Execution Policy Error
Run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Manual Steps (If Needed)

If the automated script doesn't work, you can run these steps manually:

```bash
# 1. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic

# 5. Start server
python manage.py runserver
```

---

## 🎉 Success!

Once the server starts, you'll see:
- ✅ Server running at http://127.0.0.1:8000
- ✅ Browser automatically opened
- ✅ All systems ready

**That's it! Your system is now running!** 🚀

---

## 💡 Pro Tips

1. **Bookmark the startup script** - Keep it easily accessible
2. **Use the management command** - More control and options
3. **Check the logs** - If something fails, check the error messages
4. **Keep dependencies updated** - Run `pip install -r requirements.txt --upgrade` periodically

---

## 📞 Need Help?

- Check the error messages in the terminal
- Review the troubleshooting section above
- Check `AUTO_SAVE_SYSTEM.md` for persistence system info
- Review Django documentation if needed

---

**Enjoy your fully automated system startup!** 🎊

