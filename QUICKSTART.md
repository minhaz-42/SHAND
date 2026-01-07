# SHAND Quick Start Guide

## Starting the Server

You can now run the server from the project root directory using the convenience script:

### Option 1: Using the runserver script (Recommended)
```bash
cd /Users/tanvir/Desktop/SHAND
./runserver.sh
```

### Option 2: Using the manage script
```bash
cd /Users/tanvir/Desktop/SHAND
./manage.sh runserver
```

### Option 3: Manual (if scripts don't work)
```bash
cd /Users/tanvir/Desktop/SHAND/backend
python3 manage.py runserver
```

## Accessing the Application

Once the server is running, open your browser and visit:

### Landing Page
http://127.0.0.1:8000/landing.html

### Analysis Input
http://127.0.0.1:8000/index.html

### About Page
http://127.0.0.1:8000/about.html

## Testing the API

While the server is running, you can test the API:

```bash
curl -X POST http://127.0.0.1:8000/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text": "We assume users will adopt this quickly."}'
```

## Other Management Commands

You can use the manage script for any Django command:

```bash
# Run migrations
./manage.sh migrate

# Run tests
./manage.sh test

# Create a superuser
./manage.sh createsuperuser

# Open Django shell
./manage.sh shell
```

## Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

## Project Structure

```
/Users/tanvir/Desktop/SHAND/
├── runserver.sh          ← Start server from here
├── manage.sh             ← Run any Django command
├── README.md             ← Full documentation
├── PROJECT_STATUS.md     ← Status report
├── frontend/             ← HTML files (served by Django)
│   ├── index.html
│   ├── landing.html
│   ├── analysis.html
│   ├── assumption.html
│   ├── about.html
│   └── result.html
└── backend/              ← Django project
    ├── manage.py
    ├── db.sqlite3
    ├── shand/            ← Django settings
    └── engine/           ← SHAND logic
```

## Environment Setup

If you haven't installed dependencies yet:

```bash
# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install django djangorestframework
```

## Troubleshooting

### "Command not found: ./runserver.sh"
Make sure you're in the `/Users/tanvir/Desktop/SHAND` directory:
```bash
cd /Users/tanvir/Desktop/SHAND
./runserver.sh
```

### "Permission denied"
Make scripts executable:
```bash
chmod +x /Users/tanvir/Desktop/SHAND/*.sh
```

### Port 8000 already in use
Run on a different port:
```bash
./manage.sh runserver 8001
```

### Django not installed
```bash
pip install django djangorestframework
```

---

**Server Status:** ✅ Running at http://127.0.0.1:8000
**Database:** SQLite (db.sqlite3)
**API Endpoint:** POST /analyze/
