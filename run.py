"""
run.py  —  Start the Campus Lost & Found System (MongoDB edition)
─────────────────────────────────────────────────────────────────
Just run:  python run.py
"""
import subprocess, sys, os

# Auto-install dependencies if missing
try:
    import flask
    from werkzeug.security import generate_password_hash
    from pymongo import MongoClient
except ImportError:
    print("📦 Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "werkzeug", "pymongo"])
    print("✅ Packages installed!\n")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app, init_db

if __name__ == "__main__":
    init_db()
    print("\n✅  Campus Lost & Found is running!")
    print("🌐  Open your browser: http://127.0.0.1:5000")
    print("🍃  MongoDB: mongodb://localhost:27017/campus_lnf")
    print("🔐  Admin login  →  username: admin  |  password: admin123")
    print("    Press Ctrl+C to stop.\n")
    app.run(debug=True, use_reloader=False)
