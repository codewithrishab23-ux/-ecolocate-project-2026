"""
Script to securely initialize or update an Admin account in EcoLocate.
Credentials are NOT hardcoded. Passwords are encrypted using Werkzeug hashing.
"""

import sys
import argparse
import getpass
from werkzeug.security import generate_password_hash
from db import execute_query, check_db_health

def create_admin(username, password):
    """Hash password and insert or update admin in the database."""
    if not username or len(username.strip()) < 3:
        print("[Error] Username must be at least 3 characters.")
        return False
        
    if not password or len(password) < 8:
        print("[Error] Password must be at least 8 characters.")
        return False

    username = username.strip()
    hashed_password = generate_password_hash(password)

    # Check if admin already exists
    existing = execute_query(
        "SELECT id, username FROM admins WHERE username = %s",
        (username,),
        fetchone=True
    )

    if existing:
        execute_query(
            "UPDATE admins SET password_hash = %s WHERE username = %s",
            (hashed_password, username),
            commit=True
        )
        print(f"[Success] Password updated for existing admin '{username}'.")
    else:
        execute_query(
            "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
            (username, hashed_password),
            commit=True
        )
        print(f"[Success] Admin account '{username}' created successfully.")

    return True

def main():
    parser = argparse.ArgumentParser(description="Initialize or update EcoLocate administrator account.")
    parser.add_argument("--username", "-u", help="Admin username")
    parser.add_argument("--password", "-p", help="Admin password (if omitted, will prompt securely)")
    args = parser.parse_args()

    healthy, msg = check_db_health()
    if not healthy:
        print(f"[Database Error] {msg}")
        sys.exit(1)

    username = args.username
    password = args.password

    if not username:
        username = input("Enter admin username: ").strip()

    if not password:
        password = getpass.getpass("Enter admin password (min 8 chars): ")
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("[Error] Passwords do not match.")
            sys.exit(1)

    success = create_admin(username, password)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
