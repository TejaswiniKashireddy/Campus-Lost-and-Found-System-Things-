"""
run.py  —  Start the Campus Lost & Found System (MongoDB edition)
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
    print("\n✅ Campus Lost & Found is running!")
    
    # 🔥 IMPORTANT CHANGE FOR DEPLOYMENT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)