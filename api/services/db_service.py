import sqlite3
import os
from datetime import datetime

# Place database predictably inside the data folder alongside raw files
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chats.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            model_used TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
        )
    ''')
    conn.commit()
    conn.close()

def create_chat(chat_id: str, title: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    cursor.execute('''
        INSERT OR IGNORE INTO chats (chat_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, title, now_iso, now_iso))
    conn.commit()
    conn.close()

def add_message(message_id: str, chat_id: str, role: str, content: str, model_used: str, source: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO messages (message_id, chat_id, role, content, model_used, source, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (message_id, chat_id, role, content, model_used, source, now_iso))
    # Update parent chat's updated_at
    cursor.execute('''
        UPDATE chats SET updated_at = ? WHERE chat_id = ?
    ''', (now_iso, chat_id))
    conn.commit()
    conn.close()

def get_all_chats() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT chat_id, title, updated_at FROM chats
        ORDER BY updated_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [{"chat_id": row[0], "title": row[1], "updated_at": row[2]} for row in rows]

def get_chat_history_full(chat_id: str) -> list[dict]:
    """Returns the full history of the conversation (frontend API purpose)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content, source FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    ''', (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1], "source": row[2] if len(row) > 2 else "{}"} for row in rows]

def get_recent_history(chat_id: str, limit: int = 10) -> list:
    """Returns history formatted perfectly for the google.generativeai SDK."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    ''', (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    
    # Truncate older context if it exceeds limit token window
    recent_rows = rows[-limit:] if len(rows) > limit else rows
    
    history = []
    for role, content in recent_rows:
        # generative ai uses "user" and "model"
        history.append({"role": role, "parts": [content]})
    return history

# Initialize the db schema on boot
init_db()
