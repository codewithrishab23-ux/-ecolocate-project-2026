"""
EcoLocate - Setup Phase 7 Database Schema Additions
Adds `is_active` status to users table if not already present.
"""

from db import execute_query, check_db_health
from werkzeug.security import generate_password_hash

def setup_phase7():
    print("[*] Checking database health...")
    healthy, msg = check_db_health()
    if not healthy:
        print(f"[!] Database unhealthy: {msg}")
        return False

    # 1. Add is_active column to users table if not exists
    columns = execute_query("SHOW COLUMNS FROM users LIKE 'is_active'", fetchall=True)
    if not columns:
        print("[*] Adding 'is_active' column to 'users' table...")
        execute_query("ALTER TABLE users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1", commit=True)
        print("[+] 'is_active' column added successfully.")
    else:
        print("[+] 'is_active' column already exists in 'users' table.")

    # 2. Ensure default admin exists
    admin = execute_query("SELECT id, username FROM admins WHERE username = 'admin'", fetchone=True)
    if not admin:
        print("[*] Creating default admin 'admin'...")
        execute_query(
            "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
            ('admin', generate_password_hash('AdminSecure2026!')),
            commit=True
        )
        print("[+] Default admin account created.")
    else:
        print("[+] Admin account 'admin' exists.")

    print("\n[+] Phase 7 database setup verified successfully!")
    return True

if __name__ == '__main__':
    setup_phase7()
