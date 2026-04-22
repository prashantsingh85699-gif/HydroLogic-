import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "utilityguard.db")

def init_db():
    """Initializes the local SQLite database to store user credentials."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            auth_provider TEXT DEFAULT 'local'
        )
    ''')
    conn.commit()
    conn.close()

def _hash_password(password: str) -> str:
    """Creates a simple SHA-256 hash of the password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(name: str, username: str, password: str) -> bool:
    """Registers a new normal user with hashed password."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, username, password_hash, auth_provider) VALUES (?, ?, ?, 'local')",
            (name, username, _hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> dict:
    """Verifies local user credentials and returns user details if successful."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, username FROM users WHERE username = ? AND password_hash = ? AND auth_provider = 'local'",
        (username, _hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"success": True, "name": user[0], "username": user[1]}
    else:
        return {"success": False, "error": "Invalid username or password"}

def authenticate_oauth(provider: str, email: str, name: str) -> dict:
    """Simulates OAuth authentication. Seamlessly registers them if they don't exist."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if they exist for this provider
    cursor.execute(
        "SELECT name, username FROM users WHERE username = ? AND auth_provider = ?",
        (email, provider)
    )
    user = cursor.fetchone()
    
    if user:
        conn.close()
        return {"success": True, "name": user[0], "username": user[1]}
    else:
        # Auto-register the OAuth user
        try:
            cursor.execute(
                "INSERT INTO users (name, username, password_hash, auth_provider) VALUES (?, ?, 'NA', ?)",
                (name, email, provider)
            )
            conn.commit()
            conn.close()
            return {"success": True, "name": name, "username": email}
        except sqlite3.IntegrityError:
            conn.close()
            return {"success": False, "error": f"Email {email} is already linked to a different sign-in method."}
