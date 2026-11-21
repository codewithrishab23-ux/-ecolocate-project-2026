-- ============================================================================
-- EcoLocate (E-Waste Facility Locator) - Database Schema (Phase 8 Production)
-- Database Name: ewaste_db
-- ============================================================================

CREATE DATABASE IF NOT EXISTS ewaste_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ewaste_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_users_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Admins Table
CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Centres Table (CPCB Authorized E-Waste Recyclers & Dismantlers)
CREATE TABLE IF NOT EXISTS centres (
  id INT AUTO_INCREMENT PRIMARY KEY,
  centre_name VARCHAR(200) NOT NULL,
  state VARCHAR(100) NOT NULL,
  city VARCHAR(100) NOT NULL,
  address TEXT NOT NULL,
  capacity_mta VARCHAR(100) DEFAULT NULL,
  centre_type VARCHAR(100) DEFAULT 'Authorised dismantler/recycler',
  source VARCHAR(150) DEFAULT NULL,
  website_url VARCHAR(255) DEFAULT NULL,
  website_verification TEXT DEFAULT NULL,
  website_checked_date VARCHAR(50) DEFAULT NULL,
  phone_number VARCHAR(50) DEFAULT NULL,
  email VARCHAR(150) DEFAULT NULL,
  latitude DECIMAL(10, 8) DEFAULT NULL,
  longitude DECIMAL(11, 8) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_centres_state (state),
  INDEX idx_centres_city (city),
  INDEX idx_centres_state_city (state, city),
  INDEX idx_centres_coords (latitude, longitude),
  INDEX idx_centres_name (centre_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Devices Table
CREATE TABLE IF NOT EXISTS devices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  device_name VARCHAR(150) NOT NULL UNIQUE,
  points_per_unit INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Centre Devices Mapping Table (Verified Device Acceptance)
CREATE TABLE IF NOT EXISTS centre_devices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  centre_id INT NOT NULL,
  device_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_centre_device (centre_id, device_id),
  CONSTRAINT fk_centre FOREIGN KEY (centre_id) REFERENCES centres(id) ON DELETE CASCADE,
  CONSTRAINT fk_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Rewards History Table (User Reward Projections)
CREATE TABLE IF NOT EXISTS rewards_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  device_id INT NOT NULL,
  quantity INT NOT NULL,
  total_points INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_rewards_user_created (user_id, created_at),
  CONSTRAINT fk_rewards_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_rewards_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. User Activity Tracking Table
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

-- Standard Device Categories & Illustrative Points per Unit
INSERT IGNORE INTO devices (id, device_name, points_per_unit) VALUES
(1, 'Mobile Phones & Tablets', 150),
(2, 'Laptops & Computers', 350),
(3, 'Large Home Appliances', 50),
(4, 'Consumer Electronics', 200),
(5, 'Batteries & Accessories', 8),
(6, 'Mobile Phone', 10),
(7, 'Laptop', 25),
(8, 'Tablet', 15),
(9, 'Desktop Computer', 30),
(10, 'Television', 35),
(11, 'Keyboard', 5),
(12, 'Mouse', 5),
(13, 'Charger', 5);

-- ============================================================================
-- Repeat Submission Points System & E-Waste Collection Module Tables
-- ============================================================================

-- 8. Configurable Points Tiers
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

INSERT IGNORE INTO points_tiers (id, tier_name, min_quantity, max_quantity, points_awarded, is_active) VALUES
(1, '1 Item Tier', 1, 1, 5, 1),
(2, '2 Items Tier', 2, 2, 15, 1),
(3, '3-4 Items Tier', 3, 4, 25, 1),
(4, '5-9 Items Tier', 5, 9, 40, 1),
(5, '10+ Items Tier', 10, NULL, 60, 1);

-- 9. Recyclers & Prospective Partners
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

INSERT IGNORE INTO recyclers (id, name, contact_phone, email, accepted_categories, min_pickup_qty, pickup_availability, payment_terms, status, collection_status, notes)
VALUES (1, 'National E-Waste Hotline (Prospective)', '1800 102 9077', 'info@ewaste-prospective.in', 'Mobile phones, Laptops, Desktops, Batteries, Consumer Electronics', 'To be verified upon contact', 'Prospective inquiry', 'Pending terms confirmation', 'prospective', 'Not Contacted', 'Prospective recycler contact only. Not labeled as a verified official partner. Pickup terms, rates, and minimum quantity have not been confirmed.');

-- 10. E-Waste Submissions
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

-- 11. E-Waste Submission Items (Multi-Item Submissions)
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

-- 12. E-Waste Submission Images
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

-- 13. User Points Wallets
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

-- 14. Points Transactions (Ledger)
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

-- 15. Collection Batches
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
