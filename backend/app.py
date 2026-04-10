"""
backend/app.py
──────────────
Main Flask application — MongoDB edition.
Templates → frontend/templates/
Static    → frontend/static/
Uploads   → backend/static/images/uploads/
Database  → MongoDB (local)  mongodb://localhost:27017/campus_lnf
"""

import os, uuid
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from bson import ObjectId
from pymongo import MongoClient

# ── Folder paths ──────────────────────────────────────────────────────────────
ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR  = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR   = os.path.join(FRONTEND_DIR, "static")
UPLOAD_DIR   = os.path.join(BACKEND_DIR, "static", "images", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static",
)
app.secret_key = "campus_lnf_2024_secret"
ALLOWED_EXT    = {"png", "jpg", "jpeg", "gif", "webp"}

# ── MongoDB connection ────────────────────────────────────────────────────────
#   Change MONGO_URI if your MongoDB runs on a different host/port/auth
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB  = "campus_lnf"

client    = MongoClient(MONGO_URI)
mdb       = client[MONGO_DB]

users_col = mdb["users"]   # collection: users
items_col = mdb["items"]   # collection: items


def init_db():
    """Create indexes and seed default admin account."""
    users_col.create_index("username", unique=True)
    users_col.create_index("email",    unique=True)
    items_col.create_index("type")
    items_col.create_index("title")
    items_col.create_index("location")

    if not users_col.find_one({"username": "admin"}):
        users_col.insert_one({
            "username":   "admin",
            "email":      "admin@campus.edu",
            "password":   generate_password_hash("admin123"),
            "is_admin":   True,
            "created_at": datetime.utcnow(),
        })
        print("✅ Admin account created  (username: admin | password: admin123)")


# ── Document → dict helpers ───────────────────────────────────────────────────

def user_to_dict(doc):
    if not doc:
        return None
    return {
        "id":         str(doc["_id"]),
        "username":   doc.get("username", ""),
        "email":      doc.get("email", ""),
        "is_admin":   doc.get("is_admin", False),
        "created_at": str(doc.get("created_at", ""))[:10],
    }


def item_to_dict(doc, username="", email=""):
    if not doc:
        return None
    return {
        "id":          str(doc["_id"]),
        "title":       doc.get("title", ""),
        "description": doc.get("description", ""),
        "type":        doc.get("type", ""),
        "location":    doc.get("location", ""),
        "date":        doc.get("date", ""),
        "contact":     doc.get("contact", ""),
        "image":       doc.get("image"),
        "user_id":     str(doc.get("user_id", "")),
        "status":      doc.get("status", "open"),
        "created_at":  str(doc.get("created_at", ""))[:10],
        "username":    doc.get("username", username),
        "email":       doc.get("email",    email),
    }


def enrich_items(docs):
    """Attach username to a list of item documents."""
    results = []
    for doc in docs:
        user = users_col.find_one({"_id": doc.get("user_id")})
        d = item_to_dict(doc,
                         username=user["username"] if user else "Unknown",
                         email=user.get("email", "") if user else "")
        results.append(d)
    return results


def fetch_items(item_type, q="", loc=""):
    """Return items by type with optional name/location search."""
    query = {"type": item_type}
    if q:   query["title"]    = {"$regex": q,   "$options": "i"}
    if loc: query["location"] = {"$regex": loc, "$options": "i"}
    docs = items_col.find(query).sort("created_at", -1).limit(12)
    return enrich_items(docs)


# ── Auth decorators ───────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def wrapped(*a, **kw):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapped


def admin_required(f):
    @wraps(f)
    def wrapped(*a, **kw):
        if not session.get("is_admin"):
            flash("Admin access only.", "danger")
            return redirect(url_for("home"))
        return f(*a, **kw)
    return wrapped


# ── Uploaded image serving ────────────────────────────────────────────────────

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    q   = request.args.get("q",        "").strip()
    loc = request.args.get("location", "").strip()

    lost_items  = fetch_items("lost",  q, loc)
    found_items = fetch_items("found", q, loc)

    stats = {
        "total_lost":  items_col.count_documents({"type": "lost"}),
        "total_found": items_col.count_documents({"type": "found"}),
        "total_users": users_col.count_documents({"is_admin": {"$ne": True}}),
    }
    return render_template("home.html", lost_items=lost_items,
                           found_items=found_items, stats=stats, q=q, loc=loc)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u  = request.form["username"].strip()
        e  = request.form["email"].strip()
        p  = request.form["password"]
        p2 = request.form["confirm_password"]

        if p != p2:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        if users_col.find_one({"username": u}):
            flash("Username already taken.", "danger")
            return redirect(url_for("register"))
        if users_col.find_one({"email": e}):
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        users_col.insert_one({
            "username":   u,
            "email":      e,
            "password":   generate_password_hash(p),
            "is_admin":   False,
            "created_at": datetime.utcnow(),
        })
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident = request.form["identifier"].strip()
        pwd   = request.form["password"]

        user = users_col.find_one({"$or": [{"username": ident}, {"email": ident}]})
        if user and check_password_hash(user["password"], pwd):
            session["user_id"]  = str(user["_id"])
            session["username"] = user["username"]
            session["is_admin"] = user.get("is_admin", False)
            flash(f"Welcome back, {user['username']}! 👋", "success")
            return redirect(url_for("home"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/post/<item_type>", methods=["GET", "POST"])
@login_required
def post_item(item_type):
    if item_type not in ("lost", "found"):
        return redirect(url_for("home"))

    if request.method == "POST":
        img = save_image(request.files.get("image"))
        items_col.insert_one({
            "title":       request.form["title"].strip(),
            "description": request.form["description"].strip(),
            "type":        item_type,
            "location":    request.form["location"].strip(),
            "date":        request.form["date"],
            "contact":     request.form["contact"].strip(),
            "image":       img,
            "user_id":     ObjectId(session["user_id"]),
            "status":      "open",
            "created_at":  datetime.utcnow(),
        })
        flash(f"Your {item_type} item has been posted! ✅", "success")
        return redirect(url_for("home"))

    return render_template("post_item.html", item_type=item_type,
                           today=datetime.today().strftime("%Y-%m-%d"))


@app.route("/item/<item_id>")
def item_details(item_id):
    try:
        doc = items_col.find_one({"_id": ObjectId(item_id)})
    except Exception:
        flash("Invalid item ID.", "danger")
        return redirect(url_for("home"))

    if not doc:
        flash("Item not found.", "danger")
        return redirect(url_for("home"))

    user = users_col.find_one({"_id": doc.get("user_id")})
    item = item_to_dict(doc,
                        username=user["username"] if user else "Unknown",
                        email=user.get("email", "") if user else "")
    return render_template("item_details.html", item=item)


@app.route("/my-posts")
@login_required
def my_posts():
    docs  = items_col.find({"user_id": ObjectId(session["user_id"])}).sort("created_at", -1)
    items = [item_to_dict(d) for d in docs]
    return render_template("my_posts.html", items=items)


@app.route("/delete/<item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    try:
        doc = items_col.find_one({"_id": ObjectId(item_id)})
    except Exception:
        flash("Invalid item.", "danger")
        return redirect(url_for("my_posts"))

    if not doc:
        flash("Item not found.", "danger")
        return redirect(url_for("my_posts"))

    if str(doc["user_id"]) != session["user_id"] and not session.get("is_admin"):
        flash("Permission denied.", "danger")
        return redirect(url_for("my_posts"))

    if doc.get("image"):
        path = os.path.join(UPLOAD_DIR, doc["image"])
        if os.path.exists(path):
            os.remove(path)

    items_col.delete_one({"_id": ObjectId(item_id)})
    flash("Item deleted.", "success")
    return redirect(request.referrer or url_for("my_posts"))


@app.route("/toggle-status/<item_id>", methods=["POST"])
@login_required
def toggle_status(item_id):
    try:
        doc = items_col.find_one({"_id": ObjectId(item_id)})
    except Exception:
        return redirect(url_for("my_posts"))

    if doc and str(doc["user_id"]) == session["user_id"]:
        new = "recovered" if doc.get("status", "open") == "open" else "open"
        items_col.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": new}})
        flash(f"Marked as {new}.", "success")
    return redirect(request.referrer or url_for("my_posts"))


@app.route("/profile")
@login_required
def profile():
    doc  = users_col.find_one({"_id": ObjectId(session["user_id"])})
    user = user_to_dict(doc)
    uid  = ObjectId(session["user_id"])

    post_count  = items_col.count_documents({"user_id": uid})
    lost_count  = items_col.count_documents({"user_id": uid, "type": "lost"})
    found_count = items_col.count_documents({"user_id": uid, "type": "found"})

    return render_template("profile.html", user=user, post_count=post_count,
                           lost_count=lost_count, found_count=found_count)


@app.route("/admin")
@login_required
@admin_required
def admin():
    # All users with post count
    users = []
    for u in users_col.find().sort("created_at", -1):
        d = user_to_dict(u)
        d["post_count"] = items_col.count_documents({"user_id": u["_id"]})
        users.append(d)

    # All items with username
    items = enrich_items(items_col.find().sort("created_at", -1))

    return render_template("admin.html", users=users, items=items)


# ── Image save helper (defined after app) ─────────────────────────────────────
<<<<<<< HEAD
def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT
=======
>>>>>>> 4a746e126a9b2ae25269d7e28a29f7abc1bf82c4

def save_image(file):
    if file and file.filename and allowed(file.filename):
        ext  = file.filename.rsplit(".", 1)[1].lower()
        name = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_DIR, name))
        return name
    return None
