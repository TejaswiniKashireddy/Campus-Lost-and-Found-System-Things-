# 🎒 Campus Lost & Found System

A Flask web application for college students to report and search for lost & found items on campus.

---

## 📁 Folder Structure

```
campus-lnf/
│
├── run.py                          ← START HERE — launches the app
├── requirements.txt                ← Python dependencies
├── README.md
│
├── backend/                        ← Python / Flask / Database
│   ├── __init__.py
│   ├── app.py                      ← All Flask routes & logic
│   ├── database.db                 ← SQLite database (auto-created)
│   │
│   ├── models/                     ← Database helper functions
│   │   ├── __init__.py
│   │   ├── user_model.py           ← User queries
│   │   └── item_model.py           ← Item queries
│   │
│   └── static/
│       └── images/
│           └── uploads/            ← Uploaded item photos stored here
│
└── frontend/                       ← HTML / CSS / JavaScript
    ├── templates/                  ← Jinja2 HTML pages
    │   ├── base.html               ← Shared navbar + flash layout
    │   ├── login.html
    │   ├── register.html
    │   ├── home.html               ← Dashboard with search & cards
    │   ├── post_item.html          ← Post lost or found item
    │   ├── item_details.html       ← Full item view
    │   ├── my_posts.html           ← User's own posts
    │   ├── profile.html
    │   └── admin.html              ← Admin panel
    │
    └── static/
        ├── css/
        │   └── style.css           ← All styling
        ├── js/
        │   └── script.js           ← UI interactions
        └── images/                 ← Static frontend images
```

---

## ▶️ How to Run (3 steps)

### Step 1 — Install Python
Download Python 3.8+ from https://www.python.org
✅ Check **"Add Python to PATH"** during installation on Windows.

### Step 2 — Install Flask
Open **Command Prompt** (Windows) or **Terminal** (Mac/Linux):
```
pip install flask werkzeug
```

### Step 3 — Run the App
```
cd campus-lnf
python run.py
```

Open your browser at: **http://127.0.0.1:5000**

> `run.py` also auto-installs Flask if it's missing — so Step 2 is optional.

---

## 🔐 Default Login Credentials

| Role    | Username | Password  |
|---------|----------|-----------|
| Admin   | `admin`  | `admin123`|

Register new student accounts from the **Register** page.

---

## ✨ Features

| Feature           | Description                                               |
|-------------------|-----------------------------------------------------------|
| 🔐 Auth           | Register, login, logout with hashed passwords             |
| 🏠 Dashboard      | Latest lost & found cards with live stats                 |
| 🔍 Search         | Filter by item name and/or location                       |
| 📍 Post Lost      | Title, description, location, date, contact, photo        |
| ✅ Post Found     | Same fields, tagged as "found"                            |
| 📋 My Posts       | View all your posts, mark recovered, delete               |
| 🔎 Item Details   | Full detail view with contact sidebar                     |
| 👤 Profile        | Account info + activity stats + quick actions             |
| 🛡️ Admin Panel    | View all users, delete any post                           |
| 📸 Image Upload   | Optional photo with drag-and-drop support                 |
| 📱 Responsive     | Works on mobile and tablet screens                        |

---

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT UNIQUE NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,        -- hashed with Werkzeug
    is_admin   INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Items table
CREATE TABLE items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    type        TEXT NOT NULL CHECK(type IN ('lost','found')),
    location    TEXT NOT NULL,
    date        TEXT NOT NULL,
    contact     TEXT NOT NULL,
    image       TEXT,                -- filename in backend/static/images/uploads/
    user_id     INTEGER NOT NULL,
    status      TEXT DEFAULT 'open', -- 'open' or 'recovered'
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 🌐 Routes Reference

| Method | URL                       | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/`                       | Redirect to home               |
| GET    | `/home`                   | Dashboard + search             |
| GET    | `/register`               | Register form                  |
| POST   | `/register`               | Create new account             |
| GET    | `/login`                  | Login form                     |
| POST   | `/login`                  | Authenticate user              |
| GET    | `/logout`                 | Clear session                  |
| GET    | `/post/lost`              | Post lost item form            |
| POST   | `/post/lost`              | Submit lost item               |
| GET    | `/post/found`             | Post found item form           |
| POST   | `/post/found`             | Submit found item              |
| GET    | `/item/<id>`              | Item detail page               |
| GET    | `/my-posts`               | Current user's posts           |
| POST   | `/delete/<id>`            | Delete an item                 |
| POST   | `/toggle-status/<id>`     | Mark item as recovered/open    |
| GET    | `/profile`                | User profile page              |
| GET    | `/admin`                  | Admin panel (admin only)       |
| GET    | `/uploads/<filename>`     | Serve uploaded images          |

---

## 🔧 Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python 3 + Flask 3.0                |
| Database  | SQLite (built into Python)          |
| Auth      | Werkzeug password hashing           |
| Templates | Jinja2 (via Flask)                  |
| Frontend  | HTML5 + Custom CSS + Vanilla JS     |
| Fonts     | Plus Jakarta Sans + Instrument Serif|

---

## ⭐ Optional Upgrades

- **Google Maps** — location picker on post form
- **Email alerts** — Flask-Mail when a matching item is posted
- **Chat feature** — Flask-SocketIO between finder and owner
- **Dark mode** — CSS variable toggle button
- **Pagination** — for large numbers of items
