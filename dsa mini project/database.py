"""
WL Predictor - Database Management & Seeding
============================================
SQLite database layer for storing predictions, daily waiting-list
movements, cancellation stats, and final journey outcomes.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'railway_wl.db')

def get_db_connection():
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes schema and pre-fills default data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_no TEXT NOT NULL,
            journey_date TEXT NOT NULL,
            travel_class TEXT NOT NULL,
            quota TEXT NOT NULL,
            current_wl INTEGER NOT NULL,
            days_left INTEGER NOT NULL,
            probability INTEGER NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # 2. Waiting-list history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wl_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            wl_number INTEGER NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        );
    ''')

    # 3. Cancellations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cancellations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_no TEXT NOT NULL,
            date TEXT NOT NULL,
            count INTEGER NOT NULL
        );
    ''')

    # 4. Outcomes table (30+ sample historical tickets)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_no TEXT NOT NULL,
            class TEXT NOT NULL,
            final_status TEXT NOT NULL
        );
    ''')

    conn.commit()

    # Check if outcomes table is already seeded
    cursor.execute("SELECT COUNT(*) FROM outcomes")
    outcomes_count = cursor.fetchone()[0]

    if outcomes_count == 0:
        _seed_sample_data(conn)

    conn.close()

def _seed_sample_data(conn):
    """Pre-fills 30+ sample outcomes, historical cancellations, and sample tickets with WL history."""
    cursor = conn.cursor()

    # 35 Sample ticket outcomes across popular Indian Railway trains
    sample_outcomes = [
        # Mumbai Rajdhani (12951)
        ('12951', '3A', 'Confirmed'),
        ('12951', '3A', 'Confirmed'),
        ('12951', '2A', 'RAC'),
        ('12951', '2A', 'Confirmed'),
        ('12951', '1A', 'Waiting'),
        ('12951', '3A', 'Confirmed'),
        # Howrah Rajdhani (12301)
        ('12301', '3A', 'Confirmed'),
        ('12301', '2A', 'RAC'),
        ('12301', '3A', 'Confirmed'),
        ('12301', '1A', 'Waiting'),
        ('12301', '2A', 'Confirmed'),
        # Kerala Express (12626)
        ('12626', 'SL', 'Confirmed'),
        ('12626', 'SL', 'Confirmed'),
        ('12626', 'SL', 'RAC'),
        ('12626', '3A', 'Confirmed'),
        ('12626', '3A', 'RAC'),
        ('12626', '2A', 'Waiting'),
        ('12626', 'SL', 'Confirmed'),
        # Sealdah Duronto (12259)
        ('12259', '3A', 'Confirmed'),
        ('12259', '2A', 'Confirmed'),
        ('12259', '3A', 'RAC'),
        ('12259', '1A', 'Waiting'),
        # Lucknow Shatabdi (12004)
        ('12004', 'CC', 'Confirmed'),
        ('12004', 'CC', 'Confirmed'),
        ('12004', 'CC', 'RAC'),
        ('12004', 'CC', 'Waiting'),
        # Punjab Mail (12138)
        ('12138', 'SL', 'Confirmed'),
        ('12138', 'SL', 'RAC'),
        ('12138', '3A', 'Confirmed'),
        ('12138', '2A', 'Waiting'),
        ('12138', 'SL', 'Confirmed'),
        # Bengaluru Rajdhani (22691)
        ('22691', '3A', 'Confirmed'),
        ('22691', '2A', 'RAC'),
        ('22691', '3A', 'Waiting'),
        ('22691', '1A', 'Waiting'),
        ('22691', '3A', 'Confirmed')
    ]

    cursor.executemany(
        "INSERT INTO outcomes (train_no, class, final_status) VALUES (?, ?, ?)",
        sample_outcomes
    )

    # Seed daily cancellations for recent dates
    today = datetime.now()
    sample_cancellations = [
        ('12951', (today - timedelta(days=6)).strftime('%Y-%m-%d'), 14),
        ('12951', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 18),
        ('12951', (today - timedelta(days=4)).strftime('%Y-%m-%d'), 12),
        ('12951', (today - timedelta(days=3)).strftime('%Y-%m-%d'), 16),
        ('12951', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 22),
        ('12951', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 19),
        ('12951', today.strftime('%Y-%m-%d'), 15),

        ('12626', (today - timedelta(days=6)).strftime('%Y-%m-%d'), 28),
        ('12626', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 32),
        ('12626', (today - timedelta(days=4)).strftime('%Y-%m-%d'), 25),
        ('12626', (today - timedelta(days=3)).strftime('%Y-%m-%d'), 30),
        ('12626', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 35),
        ('12626', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 27),
        ('12626', today.strftime('%Y-%m-%d'), 31),

        ('12301', (today - timedelta(days=4)).strftime('%Y-%m-%d'), 10),
        ('12301', (today - timedelta(days=3)).strftime('%Y-%m-%d'), 14),
        ('12301', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 11),
        ('12301', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 15),
        ('12301', today.strftime('%Y-%m-%d'), 13)
    ]

    cursor.executemany(
        "INSERT INTO cancellations (train_no, date, count) VALUES (?, ?, ?)",
        sample_cancellations
    )

    # Seed 3 initial tickets with real WL movement histories
    # Ticket 1: 12951 - Started WL 35, now WL 15
    cursor.execute('''
        INSERT INTO tickets (train_no, journey_date, travel_class, quota, current_wl, days_left, probability, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        '12951',
        (today + timedelta(days=8)).strftime('%Y-%m-%d'),
        '3A',
        'General',
        15,
        8,
        78,
        'High',
        (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    ))
    ticket_id_1 = cursor.lastrowid

    cursor.executemany(
        "INSERT INTO wl_history (ticket_id, date, wl_number) VALUES (?, ?, ?)",
        [
            (ticket_id_1, (today - timedelta(days=3)).strftime('%Y-%m-%d'), 35),
            (ticket_id_1, (today - timedelta(days=2)).strftime('%Y-%m-%d'), 28),
            (ticket_id_1, (today - timedelta(days=1)).strftime('%Y-%m-%d'), 21),
            (ticket_id_1, today.strftime('%Y-%m-%d'), 15)
        ]
    )

    # Ticket 2: 12626 - Kerala Express Sleeper
    cursor.execute('''
        INSERT INTO tickets (train_no, journey_date, travel_class, quota, current_wl, days_left, probability, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        '12626',
        (today + timedelta(days=14)).strftime('%Y-%m-%d'),
        'SL',
        'General',
        38,
        14,
        64,
        'Medium',
        (today - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
    ))
    ticket_id_2 = cursor.lastrowid

    cursor.executemany(
        "INSERT INTO wl_history (ticket_id, date, wl_number) VALUES (?, ?, ?)",
        [
            (ticket_id_2, (today - timedelta(days=2)).strftime('%Y-%m-%d'), 56),
            (ticket_id_2, (today - timedelta(days=1)).strftime('%Y-%m-%d'), 47),
            (ticket_id_2, today.strftime('%Y-%m-%d'), 38)
        ]
    )

    # Ticket 3: 12004 - Shatabdi Tatkal (Low confirmation)
    cursor.execute('''
        INSERT INTO tickets (train_no, journey_date, travel_class, quota, current_wl, days_left, probability, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        '12004',
        (today + timedelta(days=1)).strftime('%Y-%m-%d'),
        'CC',
        'Tatkal',
        22,
        1,
        24,
        'Low',
        (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    ))
    ticket_id_3 = cursor.lastrowid

    cursor.executemany(
        "INSERT INTO wl_history (ticket_id, date, wl_number) VALUES (?, ?, ?)",
        [
            (ticket_id_3, (today - timedelta(days=1)).strftime('%Y-%m-%d'), 25),
            (ticket_id_3, today.strftime('%Y-%m-%d'), 22)
        ]
    )

    conn.commit()

def add_ticket(train_no, journey_date, travel_class, quota, current_wl, days_left, probability, category):
    """Inserts a newly predicted ticket and creates its initial WL history entry."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tickets (train_no, journey_date, travel_class, quota, current_wl, days_left, probability, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (train_no, journey_date, travel_class, quota, current_wl, days_left, probability, category))

    ticket_id = cursor.lastrowid

    # Automatically log initial WL status into wl_history
    today_str = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO wl_history (ticket_id, date, wl_number)
        VALUES (?, ?, ?)
    ''', (ticket_id, today_str, current_wl))

    conn.commit()
    conn.close()
    return ticket_id

def get_ticket(ticket_id):
    """Fetches single ticket by primary key."""
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    return ticket

def get_recent_tickets(limit=15):
    """Returns recent predictions ordered by latest first."""
    conn = get_db_connection()
    tickets = conn.execute(
        "SELECT * FROM tickets ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return tickets

def get_all_tickets():
    """Returns all tickets for selection dropdowns."""
    conn = get_db_connection()
    tickets = conn.execute(
        "SELECT * FROM tickets ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return tickets

def add_wl_history(ticket_id, date, wl_number):
    """Adds a daily status record and updates ticket's current_wl."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO wl_history (ticket_id, date, wl_number) VALUES (?, ?, ?)",
        (ticket_id, date, wl_number)
    )

    # Update current_wl in tickets table
    cursor.execute(
        "UPDATE tickets SET current_wl = ? WHERE id = ?",
        (wl_number, ticket_id)
    )

    conn.commit()
    conn.close()

def get_wl_history(ticket_id):
    """Returns chronological WL movement history for a given ticket."""
    conn = get_db_connection()
    history = conn.execute(
        "SELECT * FROM wl_history WHERE ticket_id = ? ORDER BY date ASC, id ASC",
        (ticket_id,)
    ).fetchall()
    conn.close()
    return history

def calculate_avg_daily_drop(ticket_id=None, train_no=None):
    """Computes average drop per day from stored history."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if ticket_id:
        rows = cursor.execute(
            "SELECT date, wl_number FROM wl_history WHERE ticket_id = ? ORDER BY date ASC, id ASC",
            (ticket_id,)
        ).fetchall()
    elif train_no:
        rows = cursor.execute('''
            SELECT h.date, h.wl_number
            FROM wl_history h
            JOIN tickets t ON h.ticket_id = t.id
            WHERE t.train_no = ?
            ORDER BY h.ticket_id, h.date ASC
        ''', (train_no,)).fetchall()
    else:
        rows = cursor.execute(
            "SELECT date, wl_number FROM wl_history ORDER BY ticket_id, date ASC"
        ).fetchall()

    conn.close()

    if len(rows) < 2:
        return 2.5  # reasonable default

    total_drops = 0
    count = 0
    for i in range(1, len(rows)):
        drop = rows[i-1]['wl_number'] - rows[i]['wl_number']
        if drop >= 0:
            total_drops += drop
            count += 1

    return round(total_drops / max(1, count), 2)

def get_avg_cancellations(train_no=None):
    """Returns average cancellations recorded in database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if train_no:
        cursor.execute("SELECT AVG(count) FROM cancellations WHERE train_no = ?", (train_no,))
    else:
        cursor.execute("SELECT AVG(count) FROM cancellations")

    val = cursor.fetchone()[0]
    conn.close()
    return round(val if val is not None else 8.0, 1)

def get_analytics_summary():
    """Calculates all key performance figures for the Analytics dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total tickets checked in this system
    cursor.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cursor.fetchone()[0]

    # Outcomes breakdown
    cursor.execute("SELECT COUNT(*) FROM outcomes WHERE final_status = 'Confirmed'")
    confirmed_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM outcomes WHERE final_status = 'RAC'")
    rac_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM outcomes WHERE final_status = 'Waiting'")
    waiting_count = cursor.fetchone()[0]

    # Average daily cancellations
    cursor.execute("SELECT AVG(count) FROM cancellations")
    avg_canc = cursor.fetchone()[0]
    avg_canc_val = round(avg_canc, 1) if avg_canc is not None else 18.5

    conn.close()

    return {
        'total_tickets': total_tickets,
        'confirmed_count': confirmed_count,
        'rac_count': rac_count,
        'waiting_count': waiting_count,
        'avg_cancellations': avg_canc_val
    }

def get_cancellation_chart_data():
    """Aggregates cancellations by date for the Chart.js bar chart."""
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT date, SUM(count) as total_cancellations
        FROM cancellations
        GROUP BY date
        ORDER BY date ASC
        LIMIT 10
    ''').fetchall()
    conn.close()

    dates = [row['date'] for row in rows]
    counts = [row['total_cancellations'] for row in rows]
    return {'dates': dates, 'counts': counts}

def get_outcomes_chart_data():
    """Provides counts for Confirmed, RAC, Waiting for doughnut/pie chart."""
    conn = get_db_connection()
    cursor = conn.cursor()

    statuses = ['Confirmed', 'RAC', 'Waiting']
    counts = []
    for s in statuses:
        cursor.execute("SELECT COUNT(*) FROM outcomes WHERE final_status = ?", (s,))
        counts.append(cursor.fetchone()[0])

    conn.close()
    return {'labels': statuses, 'counts': counts}
