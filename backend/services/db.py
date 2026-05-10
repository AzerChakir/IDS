import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import random

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ids_database.db"

def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS traffic_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        source_ip TEXT NOT NULL,
        dest_ip TEXT NOT NULL,
        protocol TEXT NOT NULL,
        bytes INTEGER NOT NULL,
        status TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        severity TEXT NOT NULL,
        source_ip TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blacklisted_ips (
        ip TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS whitelisted_ips (
        ip TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS isolated_destinations (
        ip TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )
    ''')
    
    # Insert default admin if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('admin', hashed_admin_password, 'admin')
        )

    # Insert mock data if DB is empty
    cursor.execute('SELECT COUNT(*) FROM traffic_logs')
    if cursor.fetchone()[0] == 0:
        now = datetime.now()
        for i in range(50):
            timestamp = (now - timedelta(minutes=i*15)).isoformat()
            source_ip = f"192.168.1.{random.randint(2, 254)}"
            
            cursor.execute(
                'INSERT INTO traffic_logs (timestamp, source_ip, dest_ip, protocol, bytes, status) VALUES (?, ?, ?, ?, ?, ?)',
                (
                    timestamp,
                    source_ip,
                    f"10.0.0.{random.randint(1, 100)}",
                    random.choice(["TCP", "UDP", "ICMP"]),
                    random.randint(100, 15000),
                    random.choice(["ALLOWED", "BLOCKED", "ALLOWED"])
                )
            )
            
            if random.random() < 0.1:
                cursor.execute(
                    'INSERT INTO alerts (timestamp, severity, source_ip, type, description, status) VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        timestamp,
                        random.choice(["HIGH", "CRITICAL"]),
                        source_ip,
                        random.choice(["DDoS Attempt", "Port Scan", "Malware C2"]),
                        "Suspicious traffic pattern detected",
                        "UNRESOLVED"
                    )
                )

    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
