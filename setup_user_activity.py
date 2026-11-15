"""
EcoLocate - Setup User Activity Table
Creates the user_activity table in MySQL ewaste_db for audit logging and analytics.
"""

from db import execute_query, check_db_health

def setup_user_activity():
    print("[*] Checking database health...")
    healthy, msg = check_db_health()
    if not healthy:
        print(f"[!] Database unhealthy: {msg}")
        return False

    ddl = """
    CREATE TABLE IF NOT EXISTS user_activity (
        activity_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT DEFAULT NULL,
        activity_type VARCHAR(50) NOT NULL,
        search_query VARCHAR(255) DEFAULT NULL,
        city VARCHAR(100) DEFAULT NULL,
        state VARCHAR(100) DEFAULT NULL,
        centre_id INT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_activity_user (user_id),
        INDEX idx_activity_type (activity_type),
        INDEX idx_activity_created (created_at),
        INDEX idx_activity_state_city (state, city),
        CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
        CONSTRAINT fk_activity_centre FOREIGN KEY (centre_id) REFERENCES centres(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """

    print("[*] Creating 'user_activity' table if not exists...")
    try:
        execute_query(ddl, commit=True)
        print("[+] 'user_activity' table verified/created successfully.")
        
        # Verify columns
        columns = execute_query("SHOW COLUMNS FROM user_activity", fetchall=True)
        col_names = [col['Field'] for col in columns]
        print(f"[+] Columns in 'user_activity': {col_names}")
        return True
    except Exception as e:
        print(f"[!] Error creating 'user_activity' table: {e}")
        return False

if __name__ == '__main__':
    setup_user_activity()
