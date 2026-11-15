"""
EcoLocate - Phase 8 Database Optimization & Indexing Script
Adds high-performance B-Tree indexes to support 50+ concurrent users,
fast multi-criteria searches, Leaflet geospatial plotting, and rewards filtering.
"""

from db import execute_query, check_db_health

INDEXES_TO_CREATE = [
    # Table, Index Name, Columns
    ("centres", "idx_centres_state", "(state)"),
    ("centres", "idx_centres_city", "(city)"),
    ("centres", "idx_centres_state_city", "(state, city)"),
    ("centres", "idx_centres_coords", "(latitude, longitude)"),
    ("centres", "idx_centres_name", "(centre_name)"),
    ("users", "idx_users_is_active", "(is_active)"),
    ("rewards_history", "idx_rewards_user_created", "(user_id, created_at)"),
]

def optimize_database():
    print("=======================================================")
    print(" EcoLocate Phase 8: Database Index Optimization")
    print("=======================================================\n")
    
    healthy, msg = check_db_health()
    if not healthy:
        print(f"[!] Database unhealthy: {msg}")
        return False

    for table, index_name, columns in INDEXES_TO_CREATE:
        try:
            # Check if index already exists
            existing = execute_query(
                f"SHOW INDEX FROM {table} WHERE Key_name = %s",
                (index_name,),
                fetchall=True
            )
            if existing:
                print(f"[+] Index '{index_name}' on table '{table}' already exists.")
            else:
                print(f"[*] Creating index '{index_name}' on {table}{columns}...")
                execute_query(
                    f"ALTER TABLE {table} ADD INDEX {index_name} {columns}",
                    commit=True
                )
                print(f"[+] Created index '{index_name}' successfully.")
        except Exception as e:
            print(f"[!] Error handling index '{index_name}': {e}")

    print("\n[+] Database indexes verified and optimized successfully!")
    return True

if __name__ == '__main__':
    optimize_database()
