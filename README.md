# 💕 CampusDate — Campus Dating Platform

A full-stack Django dating website built exclusively for university students.

---

## 📋 Features

| Feature | Details |
|---|---|
| **Auth** | Register, login, logout with hashed passwords (Django's built-in PBKDF2) |
| **Profiles** | Photo upload, bio, age, gender, campus, interests |
| **Campus Filtering** | Browse students from same campus or search others |
| **Likes** | Like/unlike any student; AJAX — no page reload |
| **Matching** | Mutual likes auto-create a Match with popup notification |
| **Messaging** | Real-time-ish chat (3-second polling) — matched users only |
| **Admin** | Django admin at `/admin/` for full data management |
| **Security** | CSRF protection, SQL injection protection, secure password hashing, file upload validation |

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+ / Django 4.2
- **Database**: SQLite (dev) — swap to PostgreSQL for production
- **Frontend**: Vanilla HTML/CSS/JS — no frameworks, fully responsive
- **Storage**: Local media files (swap to S3 for production)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone / Extract the project
```bash
cd campusdate
```

### 2. Run setup script (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

### OR manual setup (Windows / any OS)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (creates DB + seeds campuses)
python manage.py migrate

# (Optional) Create an admin account
python manage.py createsuperuser
```

### 3. Start the server
```bash
python manage.py runserver
```

### 4. Open your browser
- **App**: http://127.0.0.1:8000
- **Admin**: http://127.0.0.1:8000/admin/

---

## 📁 Project Structure

```
campusdate/
├── manage.py                   # Django CLI entry point
├── requirements.txt            # Python dependencies
├── setup.sh                    # One-command setup script
├── db.sqlite3                  # Created after migrations
├── media/                      # User-uploaded files (profile pics)
│   └── profile_pics/
│
├── campusdate/                 # Project config package
│   ├── settings.py             # All Django settings
│   ├── urls.py                 # Root URL router
│   └── wsgi.py                 # WSGI entry point
│
└── core/                       # Main application
    ├── models.py               # Database models (Campus, UserProfile, Like, Match, Message)
    ├── views.py                # All view logic
    ├── forms.py                # Form validation
    ├── urls.py                 # App URL patterns
    ├── admin.py                # Admin panel config
    ├── migrations/
    │   ├── 0001_initial.py     # Creates all tables
    │   └── 0002_seed_campuses.py  # Populates 20 sample universities
    │
    ├── templates/core/
    │   ├── base.html           # Shared layout (navbar, footer, alerts)
    │   ├── home.html           # Landing page
    │   ├── register.html       # Registration form
    │   ├── login.html          # Login form
    │   ├── dashboard.html      # Browse users with filters
    │   ├── profile.html        # View any user's profile
    │   ├── edit_profile.html   # Edit own profile
    │   ├── matches.html        # All mutual matches
    │   └── chat.html           # Messaging UI
    │
    └── static/core/
        ├── css/style.css       # Full design system
        ├── js/main.js          # AJAX likes, chat polling, UI
        └── img/default_avatar.svg
```

---

## 🗄 Database Models

### `Campus`
| Field | Type | Description |
|---|---|---|
| name | CharField | University name (unique) |
| location | CharField | City, Country |

### `UserProfile`
| Field | Type | Description |
|---|---|---|
| user | OneToOneField → User | Django auth user |
| age | PositiveIntegerField | Student age |
| gender | CharField (choices) | M/F/NB/Other |
| bio | TextField | Self description |
| profile_picture | ImageField | Uploaded photo |
| campus | ForeignKey → Campus | Their university |
| interests | CharField | Comma-separated hobbies |

### `Like`
| Field | Type | Description |
|---|---|---|
| from_user | ForeignKey → User | Who liked |
| to_user | ForeignKey → User | Who was liked |

Auto-creates a `Match` on save if mutual.

### `Match`
| Field | Type | Description |
|---|---|---|
| user1 | ForeignKey → User | Lower user ID |
| user2 | ForeignKey → User | Higher user ID |

### `Message`
| Field | Type | Description |
|---|---|---|
| match | ForeignKey → Match | The conversation |
| sender | ForeignKey → User | Message author |
| content | TextField | Message text |
| is_read | BooleanField | Read receipt |

---

## 🔗 URL Routes

| URL | View | Auth Required |
|---|---|---|
| `/` | Home / Landing | No |
| `/register/` | Registration form | No |
| `/login/` | Login form | No |
| `/logout/` | Logout | Yes |
| `/dashboard/` | Browse students | Yes |
| `/profile/` | Own profile | Yes |
| `/profile/<username>/` | Any profile | Yes |
| `/profile/edit/` | Edit profile | Yes |
| `/like/<user_id>/` | Like/unlike (POST) | Yes |
| `/matches/` | Matches list | Yes |
| `/chat/<match_id>/` | Chat window | Yes |
| `/chat/<match_id>/messages/` | AJAX message poll | Yes |
| `/admin/` | Django admin | Superuser |

---

## ⚙️ Adding More Campuses

Option 1: Via Django Admin
1. Go to `/admin/`
2. Click **Campuses** → **Add Campus**

Option 2: Via Django shell
```bash
python manage.py shell
>>> from core.models import Campus
>>> Campus.objects.create(name="My University", location="City, Country")
```

Option 3: Edit `0002_seed_campuses.py` before running migrations.

---

## 🔒 Security Notes

- **Passwords** are hashed with Django's PBKDF2 (256,000 iterations by default)
- **CSRF tokens** protect all POST forms
- **SQL injection** is prevented by Django's ORM (parameterized queries)
- **File uploads** are validated for type and size (5MB max)
- **Chat access** is enforced — only matched users can message each other
- **Session cookies** have HttpOnly flag

---

## 🏭 Production Checklist

Before deploying to production:

1. Change `SECRET_KEY` in `settings.py` to a long random string
2. Set `DEBUG = False`
3. Set `ALLOWED_HOSTS = ['yourdomain.com']`
4. Switch database to PostgreSQL: `pip install psycopg2-binary`
5. Set up media file storage (AWS S3 / Cloudinary)
6. Run `python manage.py collectstatic`
7. Use a production WSGI server (Gunicorn + Nginx)

```python
# settings.py for PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'campusdate_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🧪 Sample Data / Testing

Register a few accounts in different roles to test:
1. Register User A on "University of Nairobi"
2. Register User B on "University of Nairobi"
3. As User A → like User B
4. As User B → like User A → 💕 Match created!
5. Go to Matches → open Chat → send messages

---

Built with ❤️ using Django · Python · HTML/CSS/JS
