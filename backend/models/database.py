import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'claimassist.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            claim_number TEXT UNIQUE NOT NULL,
            insurance_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            claim_amount REAL DEFAULT 0,
            health_score REAL DEFAULT 0,
            rejection_probability REAL DEFAULT 0,
            ai_reasons TEXT DEFAULT '[]',
            file_path TEXT,
            extracted_data TEXT DEFAULT '{}',
            hitl_action TEXT DEFAULT 'pending',
            date_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_approved TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")