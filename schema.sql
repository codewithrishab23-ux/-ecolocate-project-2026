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
