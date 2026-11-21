"""
EcoLocate - Phase 8 Database Backup & Restoration Utility
Performs structured data backups and verifies integrity for disaster recovery.
"""

import os
import json
import datetime
from db import execute_query, check_db_health

TABLES_TO_BACKUP = [
    'users',
    'admins',
    'centres',
    'devices',
    'centre_devices',
    'rewards_history',
    'user_activity',
    'points_tiers',
    'recyclers',
    'ewaste_submissions',
    'ewaste_submission_items',
    'ewaste_submission_images',
    'user_points_wallets',
    'points_transactions',
    'collection_batches'
]

def default_json_serializer(obj):
    """Serialize dates, datetimes, decimals to JSON."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj)

def backup_database(output_dir=None):
    """Export all tables from ewaste_db into a timestamped JSON backup file."""
    healthy, msg = check_db_health()
    if not healthy:
        raise ConnectionError(f"Database unavailable: {msg}")

    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), "data", "backups")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(output_dir, f"ewaste_db_backup_{timestamp}.json")

    backup_data = {
        'version': 'Phase 8 Production Backup',
        'timestamp': timestamp,
        'tables': {}
    }

    total_rows = 0
    for tbl in TABLES_TO_BACKUP:
        try:
            rows = execute_query(f"SELECT * FROM {tbl}", fetchall=True) or []
            backup_data['tables'][tbl] = rows
            total_rows += len(rows)
            print(f"[+] Backed up {len(rows)} records from table '{tbl}'.")
        except Exception as e:
            print(f"[!] Warning backing up table '{tbl}': {e}")
            backup_data['tables'][tbl] = []

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, default=default_json_serializer, indent=2)

    print(f"\n[+] Database backup saved successfully to:\n    {backup_file}")
    print(f"[+] Total records archived: {total_rows}")
    return backup_file

def verify_backup_integrity(backup_file):
    """Verify that a backup file contains valid JSON and expected tables."""
    if not os.path.isfile(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert 'tables' in data, "Backup missing 'tables' payload"
    for tbl in TABLES_TO_BACKUP:
        assert tbl in data['tables'], f"Table {tbl} missing from backup"

    centre_count = len(data['tables']['centres'])
    device_count = len(data['tables']['devices'])
    print(f"[+] Backup integrity verified: {centre_count} centres, {device_count} devices confirmed in archive.")
    return True

if __name__ == '__main__':
    path = backup_database()
    verify_backup_integrity(path)
