"""
EcoLocate - Database Migration for E-Waste Submission, Collection & Points System
Creates tables:
1. points_tiers
2. recyclers
3. ewaste_submissions
4. ewaste_submission_items
5. ewaste_submission_images
6. user_points_wallets
7. points_transactions
8. collection_batches
"""
import sys
from db import execute_query, check_db_health

def run_migration():
    print("[1/9] Checking database health...")
    healthy, msg = check_db_health()
    if not healthy:
        print(f"[Error] Database is not accessible: {msg}")
        sys.exit(1)
    print("Database connection healthy.")

    # 1. points_tiers
    print("[2/9] Creating table 'points_tiers'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS points_tiers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tier_name VARCHAR(100) NOT NULL,
        min_quantity INT NOT NULL,
        max_quantity INT NULL,
        points_awarded INT NOT NULL,
        is_active TINYINT(1) NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_tier_active (is_active),
        INDEX idx_tier_qty (min_quantity, max_quantity)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # Seed initial points tiers if empty
    tiers_cnt = execute_query("SELECT COUNT(*) AS cnt FROM points_tiers", fetchone=True)
    if not tiers_cnt or tiers_cnt['cnt'] == 0:
        print("  -> Seeding default points tiers (1 item = 5pts, 2 items = 15pts, 3-4 = 25pts, 5-9 = 40pts, 10+ = 60pts)...")
        tiers_data = [
            ("1 Item Tier", 1, 1, 5),
            ("2 Items Tier", 2, 2, 15),
            ("3-4 Items Tier", 3, 4, 25),
            ("5-9 Items Tier", 5, 9, 40),
            ("10+ Items Tier", 10, None, 60),
        ]
        for name, min_q, max_q, pts in tiers_data:
            execute_query("""
            INSERT INTO points_tiers (tier_name, min_quantity, max_quantity, points_awarded, is_active)
            VALUES (%s, %s, %s, %s, 1)
            """, (name, min_q, max_q, pts), commit=True)

    # 2. recyclers
    print("[3/9] Creating table 'recyclers'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS recyclers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        contact_phone VARCHAR(100) NOT NULL,
        email VARCHAR(150) NULL,
        accepted_categories TEXT NULL,
        registration_details TEXT NULL,
        min_pickup_qty VARCHAR(100) NULL,
        pickup_availability VARCHAR(100) NULL,
        payment_terms VARCHAR(255) NULL,
        status VARCHAR(50) DEFAULT 'prospective',
        contact_history TEXT NULL,
        collection_status VARCHAR(100) DEFAULT 'Not Contacted',
        notes TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_recycler_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # Seed initial prospective recycler (1800 102 9077) if empty
    rec_check = execute_query("SELECT id FROM recyclers WHERE contact_phone = '1800 102 9077'", fetchone=True)
    if not rec_check:
        print("  -> Seeding prospective recycler contact 1800 102 9077...")
        execute_query("""
        INSERT INTO recyclers (
            name, contact_phone, email, accepted_categories,
            min_pickup_qty, pickup_availability, payment_terms,
            status, collection_status, notes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """, (
            "National E-Waste Hotline (Prospective)",
            "1800 102 9077",
            "info@ewaste-prospective.in",
            "Mobile phones, Laptops, Desktops, Batteries, Consumer Electronics",
            "To be verified upon contact",
            "Prospective inquiry",
            "Pending terms confirmation",
            "prospective",
            "Not Contacted",
            "Prospective recycler contact only. Not labeled as a verified official partner. Pickup terms, rates, and minimum quantity have not been confirmed."
        ), commit=True)

    # 3. ewaste_submissions
    print("[4/9] Creating table 'ewaste_submissions'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS ewaste_submissions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_code VARCHAR(50) NOT NULL UNIQUE,
        user_id INT NULL,
        is_student TINYINT(1) NOT NULL DEFAULT 0,
        student_name VARCHAR(150) NULL,
        university_type VARCHAR(50) NULL,
        university_name VARCHAR(200) NULL,
        roll_number VARCHAR(100) NULL,
        course_dept VARCHAR(150) NULL,
        full_name VARCHAR(150) NOT NULL,
        phone_number VARCHAR(50) NOT NULL,
        email VARCHAR(150) NULL,
        address TEXT NOT NULL,
        city VARCHAR(100) NOT NULL,
        state VARCHAR(100) NOT NULL,
        pincode VARCHAR(20) NOT NULL,
        additional_message TEXT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        total_submitted_items INT NOT NULL DEFAULT 0,
        total_accepted_items INT NOT NULL DEFAULT 0,
        estimated_weight_kg DECIMAL(8,2) NULL,
        verified_weight_kg DECIMAL(8,2) NULL,
        points_calculated INT NOT NULL DEFAULT 0,
        points_awarded INT NOT NULL DEFAULT 0,
        points_approved TINYINT(1) NOT NULL DEFAULT 0,
        points_approved_at DATETIME NULL,
        points_approved_by INT NULL,
        admin_notes TEXT NULL,
        rejection_reason TEXT NULL,
        manual_adjustment_reason TEXT NULL,
        recycler_id INT NULL,
        scheduled_pickup_date DATE NULL,
        collected_at DATETIME NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_sub_user (user_id),
        INDEX idx_sub_status (status),
        INDEX idx_sub_code (submission_code),
        INDEX idx_sub_created (created_at),
        INDEX idx_sub_city_state (state, city),
        CONSTRAINT fk_sub_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        CONSTRAINT fk_sub_admin FOREIGN KEY (points_approved_by) REFERENCES admins (id) ON DELETE SET NULL,
        CONSTRAINT fk_sub_recycler FOREIGN KEY (recycler_id) REFERENCES recyclers (id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # 4. ewaste_submission_items
    print("[5/9] Creating table 'ewaste_submission_items'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS ewaste_submission_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_id INT NOT NULL,
        category VARCHAR(100) NOT NULL,
        item_name VARCHAR(200) NOT NULL,
        submitted_quantity INT NOT NULL DEFAULT 1,
        accepted_quantity INT NOT NULL DEFAULT 0,
        weight_kg DECIMAL(8,2) NULL,
        condition_state VARCHAR(50) NOT NULL DEFAULT 'Unknown',
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        rejection_reason VARCHAR(255) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_sub_items_sub (submission_id),
        INDEX idx_sub_items_cat (category),
        CONSTRAINT fk_item_sub FOREIGN KEY (submission_id) REFERENCES ewaste_submissions (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # 5. ewaste_submission_images
    print("[6/9] Creating table 'ewaste_submission_images'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS ewaste_submission_images (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_id INT NOT NULL,
        item_id INT NULL,
        file_path VARCHAR(255) NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        file_size INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_img_sub (submission_id),
        CONSTRAINT fk_img_sub FOREIGN KEY (submission_id) REFERENCES ewaste_submissions (id) ON DELETE CASCADE,
        CONSTRAINT fk_img_item FOREIGN KEY (item_id) REFERENCES ewaste_submission_items (id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # 6. user_points_wallets
    print("[7/9] Creating table 'user_points_wallets'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS user_points_wallets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL UNIQUE,
        total_earned INT NOT NULL DEFAULT 0,
        total_redeemed INT NOT NULL DEFAULT 0,
        current_balance INT NOT NULL DEFAULT 0,
        pending_points INT NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_wallet_user (user_id),
        CONSTRAINT fk_wallet_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # 7. points_transactions
    print("[8/9] Creating table 'points_transactions'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS points_transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        wallet_id INT NOT NULL,
        user_id INT NOT NULL,
        submission_id INT NULL,
        transaction_type VARCHAR(50) NOT NULL,
        points_amount INT NOT NULL,
        balance_after INT NOT NULL,
        reason TEXT NOT NULL,
        created_by_admin_id INT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_tx_wallet (wallet_id),
        INDEX idx_tx_user (user_id),
        INDEX idx_tx_sub (submission_id),
        INDEX idx_tx_created (created_at),
        CONSTRAINT fk_tx_wallet FOREIGN KEY (wallet_id) REFERENCES user_points_wallets (id) ON DELETE CASCADE,
        CONSTRAINT fk_tx_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        CONSTRAINT fk_tx_sub FOREIGN KEY (submission_id) REFERENCES ewaste_submissions (id) ON DELETE SET NULL,
        CONSTRAINT fk_tx_admin FOREIGN KEY (created_by_admin_id) REFERENCES admins (id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    # 8. collection_batches
    print("[9/9] Creating table 'collection_batches'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS collection_batches (
        id INT AUTO_INCREMENT PRIMARY KEY,
        batch_code VARCHAR(50) NOT NULL UNIQUE,
        recycler_id INT NULL,
        scheduled_date DATE NULL,
        completed_date DATE NULL,
        status VARCHAR(50) DEFAULT 'scheduled',
        total_items INT DEFAULT 0,
        total_weight_kg DECIMAL(10,2) DEFAULT 0,
        notes TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_batch_status (status),
        CONSTRAINT fk_batch_recycler FOREIGN KEY (recycler_id) REFERENCES recyclers (id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    print("\n[SUCCESS] All 8 tables and indexes created successfully.")

if __name__ == '__main__':
    run_migration()
