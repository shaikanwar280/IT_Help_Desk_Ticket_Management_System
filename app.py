import os
import sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-me")
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(app.instance_path, "helpdesk.sqlite3"))
os.makedirs(app.instance_path, exist_ok=True)


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL,
            requester TEXT NOT NULL, priority TEXT NOT NULL CHECK(priority IN ('Low','Medium','High')),
            status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','In Progress','Resolved','Closed')),
            assigned_to TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")


@app.route('/')
def index():
    status = request.args.get('status', '')
    with connect() as db:
        rows = db.execute("SELECT * FROM tickets WHERE status=? ORDER BY id DESC", (status,)).fetchall() if status else db.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
        counts = {r['status']: r['n'] for r in db.execute("SELECT status, COUNT(*) n FROM tickets GROUP BY status")}
    return render_template('index.html', tickets=rows, counts=counts, selected=status)


@app.route('/tickets/new', methods=['GET', 'POST'])
def create_ticket():
    if request.method == 'POST':
        title, description, requester = (request.form.get(k, '').strip() for k in ('title','description','requester'))
        priority = request.form.get('priority', 'Medium')
        if not title or not description or not requester or priority not in ('Low','Medium','High'):
            flash('Complete all fields and choose a valid priority.', 'error')
            return render_template('new.html')
        now = datetime.now().isoformat(timespec='minutes')
        with connect() as db:
            cur = db.execute("INSERT INTO tickets(title,description,requester,priority,created_at,updated_at) VALUES(?,?,?,?,?,?)", (title,description,requester,priority,now,now))
            ticket_id = cur.lastrowid
        flash('Ticket created.', 'success')
        return redirect(url_for('detail', ticket_id=ticket_id))
    return render_template('new.html')


@app.route('/tickets/<int:ticket_id>', methods=['GET', 'POST'])
def detail(ticket_id):
    if request.method == 'POST':
        status, assigned_to = request.form.get('status'), request.form.get('assigned_to','').strip()
        if status not in ('Open','In Progress','Resolved','Closed'):
            flash('Choose a valid status.', 'error')
        else:
            with connect() as db:
                db.execute("UPDATE tickets SET status=?, assigned_to=?, updated_at=? WHERE id=?", (status,assigned_to,datetime.now().isoformat(timespec='minutes'),ticket_id))
            flash('Ticket updated.', 'success')
        return redirect(url_for('detail', ticket_id=ticket_id))
    with connect() as db:
        ticket = db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    if ticket is None:
        return render_template('404.html'), 404
    return render_template('detail.html', ticket=ticket)


init_db()
if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')
