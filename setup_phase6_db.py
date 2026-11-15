"""
EcoLocate - Phase 6 Database Setup Script
Sets up devices table with standard devices and creates rewards_history table.
"""

import sys
import db

STANDARD_DEVICES = [
    {"name": "Mobile Phone", "points": 10},
    {"name": "Laptop", "points": 25},
    {"name": "Tablet", "points": 15},
    {"name": "Desktop Computer", "points": 30},
    {"name": "Television", "points": 35},
    {"name": "Keyboard", "points": 5},
    {"name": "Mouse", "points": 5},
    {"name": "Charger", "points": 5},
    {"name": "Batteries & Accessories", "points": 8},
    {"name": "Large Home Appliances", "points": 50}
]

def setup_phase6():
    print("=" * 65)
    print("EcoLocate - Phase 6 Database Migration")
    print("=" * 65)
    
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Create rewards_history table
        create_history_sql = """
        CREATE TABLE IF NOT EXISTS rewards_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            device_id INT NOT NULL,
            quantity INT NOT NULL,
            total_points INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_rewards_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_rewards_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_history_sql)
        print(" [OK] rewards_history table verified / created.")

        # 2. Populate / Update devices table
        for item in STANDARD_DEVICES:
            # Check if device already exists by exact name
            cursor.execute("SELECT id, device_name, points_per_unit FROM devices WHERE LOWER(device_name) = LOWER(%s)", (item["name"],))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE devices SET points_per_unit = %s WHERE id = %s",
                    (item["points"], row["id"])
                )
                print(f" [UPDATED] Device ID {row['id']}: {row['device_name']} -> {item['points']} pts/unit")
            else:
                cursor.execute(
                    "INSERT INTO devices (device_name, points_per_unit) VALUES (%s, %s)",
                    (item["name"], item["points"])
                )
                print(f" [INSERTED] Device: {item['name']} -> {item['points']} pts/unit")

        conn.commit()
        
        # Display current device registry
        cursor.execute("SELECT id, device_name, points_per_unit FROM devices ORDER BY id ASC")
        devices = cursor.fetchall()
        print("-" * 65)
        print("Current Active Devices Registry in ewaste_db:")
        for d in devices:
            print(f"  ID {d['id']:2d} | {d['device_name']:<25} | {d['points_per_unit']:3d} points/unit")
        print("=" * 65)

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_phase6()
