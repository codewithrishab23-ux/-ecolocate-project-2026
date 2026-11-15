"""
EcoLocate - E-Waste Facility Locator
Phase 3: CPCB Recycling Centre Data Ingestion Script
Reads researched CSV data, validates fields, checks for duplicates, and inserts records into MySQL.
"""

import os
import sys
import argparse
import pandas as pd
from db import get_db_connection, check_db_health

# Required columns expected in the CPCB researched CSV file
REQUIRED_COLUMNS = [
    'state',
    'city_district',
    'name',
    'address',
    'capacity_mta',
    'type',
    'source',
    'website_url',
    'website_verification',
    'website_checked_date'
]

def clean_value(val):
    """Clean string values and return None for NaN, null or whitespace-only entries."""
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    return s if s else None

def resolve_csv_path(custom_path=None):
    """Resolve the location of the CSV file across potential working directories."""
    candidates = []
    if custom_path:
        candidates.append(custom_path)
    
    # Common standard paths
    candidates.extend([
        os.path.join("data", "ewaste_centres_cpcb_all_websites_researched.csv"),
        os.path.join("ewaste_locator", "data", "ewaste_centres_cpcb_all_websites_researched.csv"),
        os.path.join(os.path.dirname(__file__), "data", "ewaste_centres_cpcb_all_websites_researched.csv")
    ])

    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)

    return None

def import_centres(csv_path):
    """
    Main ingestion pipeline:
    1. Reads CSV via Pandas
    2. Validates schema
    3. Checks existing database records to prevent duplicates
    4. Inserts new records with parameterized queries within a database transaction
    5. Produces a detailed verification summary
    """
    print(f"\n=======================================================")
    print(f" EcoLocate Phase 3: Recycling Centre CSV Ingestion")
    print(f"=======================================================\n")
    print(f"[*] Target CSV File: {csv_path}")

    # 1. Check database connectivity
    healthy, msg = check_db_health()
    if not healthy:
        print(f"[!] Database Error: {msg}")
        return False

    # 2. Read CSV using Pandas
    try:
        df = pd.read_csv(csv_path)
        total_csv_records = len(df)
        print(f"[+] Successfully loaded {total_csv_records} records from CSV.")
    except Exception as e:
        print(f"[!] Failed to read CSV file: {e}")
        return False

    # 3. Validate required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"[!] Schema Error: Missing required CSV columns: {missing_cols}")
        return False

    conn = get_db_connection()
    if not conn:
        print("[!] Could not connect to MySQL database.")
        return False

    cursor = conn.cursor(dictionary=True)

    imported_count = 0
    duplicate_count = 0
    failed_count = 0

    with_website_count = 0
    without_website_count = 0
    with_phone_count = 0
    with_email_count = 0
    missing_coords_count = 0

    insert_sql = """
    INSERT INTO centres (
        centre_name, state, city, address, capacity_mta, centre_type,
        source, website_url, website_verification, website_checked_date,
        phone_number, email, latitude, longitude
    ) VALUES (
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s
    )
    """

    check_duplicate_sql = """
    SELECT id, centre_name FROM centres 
    WHERE LOWER(TRIM(centre_name)) = LOWER(TRIM(%s)) 
      AND LOWER(TRIM(address)) = LOWER(TRIM(%s))
    LIMIT 1
    """

    print(f"[*] Processing records and executing duplicate verification...\n")

    try:
        for idx, row in df.iterrows():
            name = clean_value(row['name'])
            state = clean_value(row['state'])
            city = clean_value(row['city_district'])
            address = clean_value(row['address'])
            capacity = clean_value(row['capacity_mta'])
            centre_type = clean_value(row['type']) or 'Authorised dismantler/recycler'
            source = clean_value(row['source'])
            website_url = clean_value(row['website_url'])
            website_verification = clean_value(row['website_verification'])
            website_checked_date = clean_value(row['website_checked_date'])

            # Prepared contact & coordinates (clean NULL values, never fabricated)
            phone_number = None
            email = None
            latitude = None
            longitude = None

            # Skip incomplete critical rows
            if not name or not address:
                print(f"[-] Row {idx + 1}: Skipped (Missing required name or address)")
                failed_count += 1
                continue

            # Check if record already exists in database
            cursor.execute(check_duplicate_sql, (name, address))
            existing = cursor.fetchone()

            if existing:
                duplicate_count += 1
                continue

            # Execute parameterized insert
            params = (
                name, state, city, address, capacity, centre_type,
                source, website_url, website_verification, website_checked_date,
                phone_number, email, latitude, longitude
            )
            
            cursor.execute(insert_sql, params)
            imported_count += 1

            # Track verification metrics for summary
            if website_url:
                with_website_count += 1
            else:
                without_website_count += 1

            if phone_number:
                with_phone_count += 1

            if email:
                with_email_count += 1

            if latitude is None or longitude is None:
                missing_coords_count += 1

        # Commit transaction to ensure data integrity
        conn.commit()
        print(f"[+] Database transaction committed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"[!] Ingestion failed: {e}. Transaction rolled back.")
        return False
    finally:
        cursor.close()
        conn.close()

    # Query current total count from database
    total_db_records = 0
    try:
        v_conn = get_db_connection()
        v_cur = v_conn.cursor(dictionary=True)
        v_cur.execute("SELECT COUNT(*) AS total FROM centres")
        total_db_records = v_cur.fetchone()['total']
        
        # Query total with website in DB
        v_cur.execute("SELECT COUNT(*) AS total FROM centres WHERE website_url IS NOT NULL AND TRIM(website_url) != ''")
        db_with_website = v_cur.fetchone()['total']
        
        # Query total without website in DB
        v_cur.execute("SELECT COUNT(*) AS total FROM centres WHERE website_url IS NULL OR TRIM(website_url) = ''")
        db_without_website = v_cur.fetchone()['total']
        
        # Query phone, email, coords in DB
        v_cur.execute("SELECT COUNT(*) AS total FROM centres WHERE phone_number IS NOT NULL")
        db_with_phone = v_cur.fetchone()['total']
        
        v_cur.execute("SELECT COUNT(*) AS total FROM centres WHERE email IS NOT NULL")
        db_with_email = v_cur.fetchone()['total']
        
        v_cur.execute("SELECT COUNT(*) AS total FROM centres WHERE latitude IS NULL OR longitude IS NULL")
        db_missing_coords = v_cur.fetchone()['total']

        v_cur.close()
        v_conn.close()
    except Exception as e:
        print(f"[!] Verification query error: {e}")

    # Print Formatted Verification Summary
    print(f"\n=======================================================")
    print(f" CSV Ingestion & Data Verification Summary")
    print(f"=======================================================")
    print(f"  • Total CSV Records in File     : {total_csv_records}")
    print(f"  • Successfully Imported Records : {imported_count}")
    print(f"  • Duplicate / Skipped Records   : {duplicate_count}")
    print(f"  • Failed Records                : {failed_count}")
    print(f"-------------------------------------------------------")
    print(f" Current Database State ('centres' table):")
    print(f"  • Total Facilities in Database  : {total_db_records}")
    print(f"  • Facilities with Website URLs  : {db_with_website}")
    print(f"  • Facilities without Website    : {db_without_website}")
    print(f"  • Facilities with Phone Numbers : {db_with_phone} (NULL - Phase 4 candidate)")
    print(f"  • Facilities with Email Addr.   : {db_with_email} (NULL - Phase 4 candidate)")
    print(f"  • Facilities Missing Coords     : {db_missing_coords} (NULL - Phase 5 GIS)")
    print(f"=======================================================\n")

    return True

def main():
    parser = argparse.ArgumentParser(description="Import CPCB e-waste recycling centres from CSV into MySQL.")
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="Path to ewaste_centres_cpcb_all_websites_researched.csv"
    )
    args = parser.parse_args()

    csv_path = resolve_csv_path(args.file)
    if not csv_path:
        print("[!] Error: Could not locate ewaste_centres_cpcb_all_websites_researched.csv.")
        print("    Please provide the path using: python import_centres.py --file <path>")
        sys.exit(1)

    success = import_centres(csv_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
