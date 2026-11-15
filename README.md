# EcoLocate - E-Waste Facility Locator

> **EcoLocate** is a modern, enterprise-grade environmental technology web platform connecting citizens, institutions, and businesses with authorized electronic waste recycling and dismantling facilities across India. The platform diverts hazardous heavy metals from municipal landfills, promotes circular resource recovery, provides an incentivized EcoRewards framework, and empowers administrators with an executive management suite.

---

## 🌟 Executive Summary & Phase Status

| Phase | Milestone | Key Features | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | Frontend Architecture | HTML5, CSS3, Vanilla JS, Forest/Emerald SaaS design system, responsive UI | **Completed** |
| **Phase 2** | Backend & Database Foundation | Python Flask, MySQL (`ewaste_db`), Werkzeug password hashing, session management | **Completed** |
| **Phase 3** | CPCB Data Ingestion | 87 CPCB-authorized facilities ingested, verified domains, audited contact channels | **Completed** |
| **Phase 4** | Search, Filters & Contact System | Dynamic cascade dropdowns (State/City/Device), keyword search, fallback search actions | **Completed** |
| **Phase 5** | Leaflet Geospatial Intelligence | Zero-cost OpenStreetMap mapping, Geolocation API, Haversine proximity calculations | **Completed** |
| **Phase 6** | Environmental Awareness & Rewards | Heavy metals curriculum (Pb, Hg, Cd), dynamic EcoRewards calculator & history logs | **Completed** |
| **Phase 7** | Administrative Dashboard Suite | Executive KPI dashboard, Chart.js analytics, centre CRUD, CSV batch ingestion, user moderation | **Completed** |
| **Phase 8** | Testing, Security & Cloud Deployment | 50-user concurrency test (203+ RPS), 50 automated tests, CSP headers, connection pool, Render deployment | **Completed** |
| **Phase 9** | User Activity Tracking & Live Sync | Non-intrusive activity logging (MySQL `user_activity`), live DB synchronization, Admin Activity Dashboard, Privacy notices | **Completed** |

---

## 🛡️ Phase 8 Architecture (Testing, Security, Performance & Free Hosting)

Phase 8 elevates EcoLocate into a battle-tested, secure, and production-ready application:

### 1. Multi-User Concurrency & Performance Testing
- **50 Concurrent Users Simulated:** Tested using a multi-threaded load test engine (`load_test_50_users.py`) simulating 50 simultaneous user sessions performing complete user journeys (Registration, Login, Map API browsing, State/City filters, Detail views, and Rewards calculation).
- **Zero Failures:** 500 completed requests with **0.0% error rate**.
- **High Throughput:** **203.43 requests per second** on local development server.
- **Low Latency:** Average latency of **230.52 ms** (Median: **152.65 ms**).
- **Headless Locust Suite:** Provided standard `locustfile.py` benchmark for continuous load profiling.

### 2. Database Connection Pooling & Performance Indexing
- **Thread-Safe Connection Pooling:** Refactored `db.py` to use `mysql.connector.pooling.MySQLConnectionPool` with a configurable pool size (`DB_POOL_SIZE=25`), eliminating thread-contention bottlenecks.
- **Production Indexing (`optimize_db.py`):** Added 7 targeted B-tree indexes to MySQL:
  - `idx_centres_state` on `centres(state)`
  - `idx_centres_city` on `centres(city)`
  - `idx_centres_state_city` on `centres(state, city)`
  - `idx_centres_coords` on `centres(latitude, longitude)`
  - `idx_centres_name` on `centres(centre_name)`
  - `idx_users_is_active` on `users(is_active)`
  - `idx_rewards_user_created` on `rewards_history(user_id, created_at)`
- **Backup & Disaster Recovery (`backup_restore_db.py`):** Automated utility to create point-in-time JSON snapshots of all database tables (centres, users, devices, admins, rewards) and restore with single-command integrity checks.

### 3. Production Security Hardening
- **HTTP Security Defensive Headers:** Implemented via `@app.after_request` middleware:
  - `Content-Security-Policy`: Strict script, style, image, and font sources allowing OpenStreetMap and Leaflet tiles.
  - `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing exploits.
  - `X-Frame-Options: SAMEORIGIN`: Complete clickjacking protection.
  - `X-XSS-Protection: 1; mode=block`: Browser reflected XSS defense.
  - `Referrer-Policy: strict-origin-when-cross-origin`: Sensitive data leakage prevention.
- **CSRF Protection:** Integrated Flask-WTF CSRF protection across all forms and asynchronous requests.
- **SQL Injection Prevention:** 100% of SQL queries executed through parameterized queries (`cursor.execute(sql, params)`).
- **Authentication & Password Security:** Werkzeug password hashing (scrypt / pbkdf2:sha256). User passwords and password hashes are never exposed in admin interfaces or API responses.
- **Upload Guards:** Enforced `MAX_CONTENT_LENGTH = 16MB` to eliminate Denial of Service via oversized file uploads.

### 4. Free Hosting Deployment Package
- **Render Ready:** Includes `Procfile`, `wsgi.py`, and `render.yaml` for automatic deployment to Render's free Python web service tier.
- **WhiteNoise Integration:** High-performance static asset serving for production Gunicorn environments.
- **External MySQL Support:** Full SSL and CA-certificate support in `db.py` for cloud-hosted MySQL providers (Aiven MySQL Free Tier, TiDB Serverless, or Railway).

---

## 📊 Phase 9 Architecture (User Activity Tracking & Live Database Synchronisation)

Phase 9 establishes continuous behavioral intelligence, instantaneous multi-tenant data synchronization, and privacy-compliant administrative oversight:

### 1. Separate User and Admin Panels with Strict Boundary Controls
- **User Interface (`/`, `/centres`, `/awareness`, `/rewards`):** Clean, consumer-oriented public workflows with personalized calculation history, interactive OpenStreetMap Leaflet maps, and certified facility searches.
- **Admin Interface (`/admin/*`):** Isolated administrative operations suite guarded by the `@admin_required` session decorator.
- **Strict Role Boundaries:** Verified by automated tests — normal users and guests are strictly blocked from accessing `/admin/*` or administrative activity audit logs with automatic redirection to `/admin/login`.

### 2. Live Database Synchronisation
- **Single Source of Truth:** Both user-facing search APIs and administrative management interfaces query the exact same MySQL database (`ewaste_db`).
- **Zero Hardcoded Facilities:** All search queries, filters, and geospatial lookups execute dynamic SQL directly against the `centres` table.
- **Instantaneous CRUD Reflection:** When an administrator adds, modifies, or de-lists a recycling centre via the admin dashboard, the update immediately appears or updates in user searches with zero cache lag or restart requirements.

### 3. User Activity Tracking Engine (`user_activity`)
- **Schema & Indexes:**
  - `activity_id` (BIGINT AUTO_INCREMENT PRIMARY KEY)
  - `user_id` (INT NULL, FOREIGN KEY REFERENCES `users(id)` ON DELETE SET NULL)
  - `activity_type` (VARCHAR(50): `login`, `logout`, `search`, `centre_view`, `rewards_calc`)
  - `search_query` (VARCHAR(255) NULL)
  - `city` (VARCHAR(100) NULL)
  - `state` (VARCHAR(100) NULL)
  - `centre_id` (INT NULL, FOREIGN KEY REFERENCES `centres(id)` ON DELETE SET NULL)
  - `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - Targeted composite and foreign-key performance indexes for instant aggregation.
- **Events Tracked:**
  - `login` & `logout`: Tracks session creation and termination.
  - `search`: Records search keywords, selected state, and selected city.
  - `centre_view`: Logs facility inspection with facility ID, city, and state.
  - `rewards_calc`: Records device category and quantity calculated.
- **Strict Privacy Safeguards:** Passwords, password hashes, auth tokens, session IDs, and precise GPS lat/lng are **never** logged to `user_activity`.

### 4. Admin User Activity Dashboard (`/admin/activities`)
- **Executive Analytics:** Displays 5 high-impact KPI cards: Registered Users, User Logins, Facility Searches, Facility Views, and Rewards Calculations.
- **Live Audit Trail:** Paginated audit log showing user identity (or Guest), activity type with color-coded status badges, search query context, geographic filters (state/city), and exact timestamps.
- **Multi-Parameter Search & Filtering:** Filter activities by activity type dropdown, state filter, or keyword search.

### 5. Transparent User Privacy Compliance
- Clear, respectful privacy notices integrated across user touchpoints:
  - Facility search toolbar (`centres.html`): Notifies users that queries and filters are recorded anonymously to improve regional coverage.
  - Rewards calculator (`rewards.html`): Informs users that calculations are recorded for environmental impact statistics.
  - Global footer (`base.html`): Transparency disclosure stating activity records are restricted exclusively to authorized administrators.

---

## 📁 Project Folder Structure

```text
ewaste_locator/
│
├── app.py                     # Flask application routes, REST APIs, Haversine logic, security headers
├── admin.py                   # Modular Admin blueprint: KPI metrics, CRUD, user moderation, CSV ingest
├── config.py                  # Environment-driven configuration, pool size & session settings
├── db.py                      # Thread-safe MySQL connection pool & parameterized query execution
├── schema.sql                 # Production MySQL schema with all tables, constraints & 7 performance indexes
├── wsgi.py                    # Production WSGI entry point with WhiteNoise static asset serving
├── Procfile                   # Process configuration for Gunicorn WSGI workers on cloud platforms
├── render.yaml                # Render Infrastructure-as-Code Blueprint configuration
│
├── backup_restore_db.py       # Point-in-time database backup and restoration utility
├── optimize_db.py             # Database indexing migration script
├── setup_user_activity.py     # User activity tracking table initialization & indexes
├── load_test_50_users.py      # Multi-threaded 50-user concurrency test harness
├── locustfile.py              # Locust load-testing script for benchmarking
├── test_app.py                # Comprehensive 59-test automated verification suite
│
├── import_centres.py          # Data ingestion script for CPCB recycling centre records
├── update_coordinates.py      # Geospatial coordinator for verified CPCB facilities
├── init_admin.py              # CLI utility to securely provision administrator accounts
│
├── requirements.txt           # Production Python dependency requirements
├── .env.example               # Template for environment variables (local vs cloud MySQL)
├── .env                       # Local environment variables & secrets (git-ignored)
├── .gitignore                 # Git ignore file for secrets, pycache, and logs
├── README.md                  # Comprehensive documentation and deployment guide
│
├── data/                      # Data assets & backups directory
│   ├── ewaste_centres_cpcb_all_websites_researched.csv # 87 CPCB facility records
│   └── backups/               # Point-in-time database backups (JSON format)
│
├── static/                    # Production static assets served via Flask / WhiteNoise
│   ├── css/
│   │   └── style.css          # EcoLocate styling, Leaflet pins, admin dashboard & responsive grids
│   ├── js/
│   │   ├── main.js            # Leaflet map manager, Geolocation, Haversine cards & live filters
│   │   └── rewards.js         # EcoRewards dynamic calculation algorithm
│   └── images/
│       ├── hero-illustration.svg # Vector illustration depicting circular tech & recycling loop
│       └── logo.svg           # EcoLocate brand mark
│
└── templates/                 # Jinja2 production templates extending base.html / admin_base.html
    ├── base.html              # Core public layout: responsive navigation, notifications, footer
    ├── index.html             # Home page: hero section, statistics, how it works, and impact cards
    ├── centres.html           # Find Centres: Leaflet map, GPS button, search & filter sidebar, cards
    ├── awareness.html         # Why E-Waste Matters: Heavy metals (Pb, Hg, Cd), impacts & 4-step guide
    ├── rewards.html           # EcoRewards calculator: dynamic device points & user calculation history
    ├── login.html             # User authentication interface with CSRF token
    ├── register.html          # User registration interface with input validation & CSRF token
    ├── profile.html           # Authenticated user account profile
    ├── admin_login.html       # Isolated administrator sign-in portal
    ├── admin_base.html        # Admin layout: sidebar navigation, KPI header, notification bar
    ├── admin_dashboard.html   # Executive dashboard: 6 live KPIs, Chart.js analytics & recent activity
    ├── admin_centres.html     # Centre directory management with search, filters & pagination
    ├── admin_centre_form.html # Add / Edit facility form with coordinate validation
    ├── admin_centre_detail.html # Comprehensive facility profile with verification audit & directions
    ├── admin_csv_import.html  # Batch CSV ingestion with dry-run preview and duplicate detection
    ├── admin_users.html       # Community moderation directory with status toggling
    ├── admin_user_detail.html # User audit view with calculation statistics
    ├── admin_devices.html     # Electronic device catalog management (Add/Edit/Delete)
    └── admin_profile.html     # Administrator credential and password change portal
```

---

## 🧪 Comprehensive Testing Report (50 / 50 Passing)

Run the full automated test suite covering all application features:

```bash
python -m unittest discover -s ewaste_locator -p "test_app.py"
```

### Complete Test Results Breakdown:

```text
...........................................................
Ran 59 tests in 1.839s

OK
```

- **Authentication & Security Suite (Tests 1–10):**
  - `Test 1:` Database connectivity, pool initialization & health endpoint verification.
  - `Test 2:` User registration with Werkzeug password hashing.
  - `Test 3:` Duplicate email rejection and HTTP 400 enforcement.
  - `Test 4:` Invalid password rejection with error feedback.
  - `Test 5:` Successful user login, session generation, and cookie security.
  - `Test 6:` User logout and complete session invalidation.
  - `Test 7:` Route protection via `@login_required` decorator redirecting to login.
  - `Test 8:` Administrator authentication and isolated admin session creation.
  - `Test 9:` Strict role isolation between standard users and administrators.
  - `Test 10:` Multi-user concurrent session separation and privacy.

- **Directory, Search & Filtering Suite (Tests 11–20):**
  - `Test 11:` Dynamic state retrieval from MySQL `centres` table.
  - `Test 12:` Dynamic state-to-city cascading filter without page reload.
  - `Test 13:` Integration with dynamic `devices` database table.
  - `Test 14:` Filter facilities by state (verified 6 in Delhi).
  - `Test 15:` Filter facilities by city (verified 3 in Visakhapatnam).
  - `Test 16:` Compound search filters (State + City + Keyword).
  - `Test 17:` Empty search results handling with user guidance.
  - `Test 18:` Directory pagination (87 centres across 9 pages).
  - `Test 19:` Single facility detail lookup with verified CPCB data.
  - `Test 20:` Contact information integrity (verified links, no fake placeholders).

- **Geospatial & Nearest Centre Suite (Tests 21–30):**
  - `Test 21:` Mathematical validation of Haversine great-circle distance algorithm ($R=6371\text{ km}$).
  - `Test 22:` Leaflet map API endpoint (`/api/centres/map`) returning valid coordinates.
  - `Test 23:` Nearest centre calculation and ascending proximity sorting.
  - `Test 24:` Distance formatted in kilometres to two decimal places.
  - `Test 25:` Latitude/Longitude bounds validation (-90 to +90, -180 to +180).
  - `Test 26:` Facilities without coordinates remain 100% searchable in directory.
  - `Test 27:` Radial spatial filtering (`radius_km`).
  - `Test 28:` Interactive Leaflet.js and OpenStreetMap template integration.
  - `Test 29:` POST Geolocation endpoint with JSON coordinate payload.
  - `Test 30:` Database coordinate statistics transparency (20 verified, 67 pending).

- **Awareness & Rewards Suite (Tests 31–40):**
  - `Test 31:` Educational Awareness curriculum with common e-waste equipment categories.
  - `Test 32:` Toxic heavy metals information cards (Lead, Mercury, Cadmium).
  - `Test 33:` Environmental degradation impacts (soil, water, air, biodiversity).
  - `Test 34:` Responsible recycling principles and 4-step consumer disposal guide.
  - `Test 35:` Dynamic rewards device loading from MySQL with illustrative disclaimer.
  - `Test 36:` Reward points calculation formula ($\text{Points} = \text{Qty} \times \text{Unit Points}$).
  - `Test 37:` Quantity input validation rejecting negative, zero, non-numeric, or $>1000$ values.
  - `Test 38:` Authenticated calculation persistence into MySQL `rewards_history`.
  - `Test 39:` Multi-tenant rewards isolation (users cannot see other users' calculations).
  - `Test 40:` User rewards history purge endpoint.

- **Admin Management Suite (Tests 41–50):**
  - `Test 41:` Admin login, session isolation, and logout.
  - `Test 42:` Admin dashboard metrics calculation and Chart.js configuration.
  - `Test 43:` Full centre CRUD with duplicate detection against normalized names.
  - `Test 44:` Admin centre directory search and dynamic state/city filtering.
  - `Test 45:` Admin CSV batch ingestion with preview mode and duplicate skipping.
  - `Test 46:` User accounts directory with strict password hash privacy.
  - `Test 47:` Account activation/deactivation toggle and login access guard.
  - `Test 48:` Device catalog CRUD with name uniqueness checks.
  - `Test 49:` Non-admin boundary protection rejecting unauthorized access to all `/admin/*` routes.
  - `Test 50:` Public interface regression check ensuring admin changes don't affect public portal.

- **User Activity Tracking & Live Synchronisation Suite (Tests 51–59):**
  - `Test 51:` User activity table existence and complete relational schema verification.
  - `Test 52:` User login and logout event automatic recording in `user_activity`.
  - `Test 53:` Centre search and filtering activity tracking with query, state, and city context.
  - `Test 54:` Centre details view activity tracking with `centre_id`, city, and state.
  - `Test 55:` Rewards calculator activity tracking with device name and quantity details.
  - `Test 56:` Live database synchronisation verifying Admin CRUD immediately updates User searches without cache lag.
  - `Test 57:` Admin activity dashboard (`/admin/activities`) rendering with KPI metrics, filters, and audit trail.
  - `Test 58:` Strict non-admin boundary protection preventing users or guests from viewing activity logs.
  - `Test 59:` Concurrent multi-user activity isolation with simultaneous independent searches.

---

## ⚡ Concurrency & Load Testing (50 Concurrent Users)

We executed an empirical load test using 50 simultaneous threads simulating concurrent user sessions:

```bash
python load_test_50_users.py
```

### Empirical Results Summary:

| Metric | Result | Benchmark Target | Status |
| :--- | :--- | :--- | :---: |
| **Simulated Concurrent Users** | **50 Users** | 50 Users | **Met** |
| **Total Requests Completed** | **500 Requests** | 500 Requests | **Met** |
| **Successful Requests** | **500** | 500 | **Met** |
| **Failed Requests** | **0** | 0 | **Met** |
| **Error Rate** | **0.0%** | < 1.0% | **Met** |
| **Total Wall-Clock Time** | **2.46 seconds** | < 10.0s | **Met** |
| **Throughput (RPS)** | **203.43 req/sec** | > 50 req/sec | **Met** |
| **Average Latency** | **230.52 ms** | < 500 ms | **Met** |
| **Median Latency** | **152.65 ms** | < 300 ms | **Met** |
| **95th Percentile Latency** | **921.23 ms** | < 1500 ms | **Met** |
| **99th Percentile Latency** | **945.22 ms** | < 2000 ms | **Met** |

---

## 🔒 Security Audit & Hardening Summary

| Security Layer | Implementation Details | Verification |
| :--- | :--- | :--- |
| **Password Storage** | Werkzeug `generate_password_hash` with scrypt / pbkdf2 salts. | Hashes never stored or printed in plaintext; verified in Test 2. |
| **Password Privacy** | Passwords and hashes are completely omitted from admin views and API JSON responses. | Verified in Test 46. |
| **SQL Injection** | 100% of queries use MySQL parameter binding (`cursor.execute(sql, params)`). | Zero raw SQL string interpolation across all queries. |
| **CSRF Defense** | Flask-WTF CSRF tokens validated on all state-changing POST requests. | Enabled globally; tokens embedded in all forms. |
| **Session Security** | Flask secure cookies with `HttpOnly=True`, `SameSite='Lax'`, and conditional `Secure=True`. | Prevents client-side script cookie theft. |
| **Defense Headers** | Strict CSP, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`. | Verified in production middleware headers. |
| **Upload Protection** | `MAX_CONTENT_LENGTH = 16MB` limits max payload size. | Prevents DoS memory overflow on CSV imports. |
| **Role Separation** | Independent `@login_required` and `@admin_required` decorators. | Non-admins strictly blocked from admin routes (Test 49). |

---

## 🗄️ Database Setup & Optimization Guide

### 1. Database Configuration
EcoLocate uses MySQL (`ewaste_db`). Ensure MySQL is running locally or in the cloud.

### 2. Apply Schema & Performance Indexes
Execute `schema.sql` to initialize the database:
```bash
mysql -u root -p ewaste_db < schema.sql
```
Or run the Python database optimization script:
```bash
python optimize_db.py
```

### 3. Database Backup & Disaster Recovery
To create a complete backup snapshot of all tables:
```bash
python backup_restore_db.py backup
```
*Backups are saved to `data/backups/ewaste_db_backup_<timestamp>.json`.*

To restore the database from a backup snapshot:
```bash
python backup_restore_db.py restore data/backups/ewaste_db_backup_20261115_123416.json
```

---

## 🌐 Free Hosting Deployment Guide (Render + Free MySQL)

Deploying EcoLocate completely free using **GitHub + Render + Aiven Free MySQL** (or TiDB Serverless):

### Step 1: Push Code to GitHub
1. Open terminal in the `ewaste_locator` directory:
   ```bash
   git init
   git add .
   git commit -m "EcoLocate Phase 8 Production Release"
   ```
2. Create a new repository on [GitHub](https://github.com): e.g. `ecolocate`.
3. Link and push your repository:
   ```bash
   git remote add origin https://github.com/your-username/ecolocate.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Set Up a Free Cloud MySQL Database
Choose any free MySQL provider:
- **Aiven Cloud MySQL (Free Tier):** Sign up at [aiven.io](https://aiven.io). Create a free MySQL database. Download the SSL CA certificate if prompted. Note your Host, Port, User, and Password.
- **TiDB Serverless (Free Forever):** Sign up at [pingcap.com](https://pingcap.com). Create a serverless MySQL cluster. Note your connection details.
- **Import Database Schema:** Connect using MySQL Workbench or CLI and run `schema.sql`, then run `import_centres.py` to populate the 87 facilities.

### Step 3: Deploy Web Service to Render
1. Sign up / Log in to [Render](https://render.com).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository `ecolocate`.
4. Configure the service settings:
   - **Name:** `ecolocate`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app --workers 4 --threads 2 --timeout 120`
   - **Plan:** Free
5. In **Environment Variables**, add:
   - `SECRET_KEY`: *(Click "Generate" or provide a random 32-character string)*
   - `FLASK_APP`: `app.py`
   - `FLASK_ENV`: `production`
   - `DB_HOST`: `your-cloud-mysql-host.com`
   - `DB_PORT`: `3306` (or your cloud port, e.g. `14884` on Aiven)
   - `DB_USER`: `your-db-user`
   - `DB_PASSWORD`: `your-db-password`
   - `DB_NAME`: `ewaste_db`
   - `DB_POOL_SIZE`: `10`
   - `SESSION_COOKIE_SECURE`: `True`
6. Click **Deploy Web Service**. Render will install dependencies and start your WSGI server with Gunicorn.

---

## 💻 Local Running & Quickstart Instructions

### 1. Prerequisites
- Python 3.10+
- MySQL Server / MariaDB (e.g. XAMPP)

### 2. Environment Setup
1. Clone or navigate to the project folder:
   ```bash
   cd ewaste_locator
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your `.env` file (refer to `.env.example`):
   ```env
   SECRET_KEY=ecolocate_phase8_secret_key
   DB_HOST=127.0.0.1
   DB_PORT=3307
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=ewaste_db
   DB_POOL_SIZE=25
   SESSION_COOKIE_SECURE=False
   ```

### 3. Initialize & Populate Database
```bash
# Apply schema and initial seed devices
mysql -u root -p ewaste_db < schema.sql

# Ingest 87 CPCB recycling centres
python import_centres.py

# Create administrator account
python init_admin.py --username admin --password "admin123"

# Apply performance indexes
python optimize_db.py
```

### 4. Start the Application
```bash
python app.py
```
Open your browser at:
- **Public Website:** `http://127.0.0.1:5000`
- **Find Centres & Map:** `http://127.0.0.1:5000/centres`
- **Awareness Curriculum:** `http://127.0.0.1:5000/awareness`
- **Rewards Calculator:** `http://127.0.0.1:5000/rewards`
- **Admin Dashboard:** `http://127.0.0.1:5000/admin/login` *(Default: `admin` / `admin123`)*
