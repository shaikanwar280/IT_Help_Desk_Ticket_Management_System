# IT Help Desk Ticket Management System

A small Flask and SQLite application for logging support requests, tracking status, and assigning a technician. It is suitable as a starter portfolio project.

## Features
- Create tickets with requester, description, and priority
- List all tickets or filter by status
- Assign a technician and update ticket status
- Dashboard counts and persistent SQLite storage
- Input validation and clear not-found handling

## Run locally
Requires Python 3.9 or newer.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. SQLite data is created automatically in `instance/helpdesk.sqlite3`.

Set `SECRET_KEY` to a private random value before deploying. This starter app has no login or role-based access; add authentication and CSRF protection before exposing it to the public internet.

## Project layout
```
app.py
templates/
  base.html
  index.html
  new.html
  detail.html
  404.html
requirements.txt
```
