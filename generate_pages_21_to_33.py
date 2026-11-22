"""
Pages 21 to 33 for EcoLocate Academic Report (Chapters 6 to 9)
Student: YOGESH (Roll No. 241306039)
University: SGT UNIVERSITY
"""
import os
import make_report as mr
doc = mr.doc
diag_dir = mr.diag_dir

# ==============================================================================
# PAGE 21: CHAPTER 6: OBJECTIVES (6.1 to 6.7)
# ==============================================================================
def build_p21():
    mr.add_chapter_title("CHAPTER 6: OBJECTIVES")
    mr.add_sec_heading("6.1 Introduction")
    mr.add_para("The objectives of EcoLocate – E-Waste Facility Locator establish the technical, functional, environmental, and academic goals that the system is engineered to fulfill. The platform transforms fragmented e-waste registries into an integrated, interactive digital service.")

    mr.add_sec_heading("6.2 Primary Objective")
    mr.add_para("The primary objective is to design, develop, test, and deploy a secure, web-based geographic information platform that allows citizens and corporate institutions across India to discover, verify, contact, and navigate to authorized electronic waste dismantling and recycling facilities.")

    mr.add_sec_heading("6.3 User Management Objectives")
    mr.add_bullet("Provide secure, validated citizen user registration and authentication utilizing Werkzeug scrypt cryptographic password hashing.", bold_prefix="Secure Authentication: ")
    mr.add_bullet("Maintain session isolation, allowing users to save and review personal EcoRewards calculation records privately.", bold_prefix="User Session Isolation: ")

    mr.add_sec_heading("6.4 Recycling Centre Search Objectives")
    mr.add_bullet("Implement dynamic, asynchronous state and city cascading dropdown filters populated directly from the live MySQL database.", bold_prefix="Cascading Filters: ")
    mr.add_bullet("Support compound keyword queries against facility names, authorized capacities, and device categories without page reload.", bold_prefix="Compound Keyword Search: ")

    mr.add_sec_heading("6.5 Location-Based Search Objectives")
    mr.add_bullet("Acquire real-time client latitude and longitude coordinates through browser Geolocation API.", bold_prefix="Client Geolocation: ")
    mr.add_bullet("Execute spherical trigonometric Haversine distance computations to calculate exact great-circle distance in kilometres.", bold_prefix="Haversine Computation: ")
    mr.add_bullet("Sort search results dynamically in ascending proximity order to surface the nearest recycling facilities immediately.", bold_prefix="Proximity Sorting: ")

    mr.add_sec_heading("6.6 Interactive Map Objectives")
    mr.add_bullet("Embed an interactive Leaflet.js map rendered with zero-cost OpenStreetMap tile servers.", bold_prefix="Interactive Mapping: ")
    mr.add_bullet("Plot verified facility coordinates with dynamic popup cards containing facility name, capacity, address, and Google Maps directions.", bold_prefix="Marker Visualization: ")

    mr.add_sec_heading("6.7 E-Waste Awareness Objectives")
    mr.add_para("Deliver an educational curriculum explaining the toxicological mechanisms of Lead, Mercury, and Cadmium, detailing why electronic items must never be mixed with regular municipal solid waste, and presenting actionable four-step disposal guidelines.")

    mr.add_page_footer_num("14")

# ==============================================================================
# PAGE 22: CHAPTER 6 continued (6.8 to 6.11)
# ==============================================================================
def build_p22():
    mr.add_sec_heading("6.8 Reward Calculator Objectives")
    mr.add_bullet("Implement a formula-driven rewards engine: Total EcoPoints = Quantity x Points Per Unit, validating input boundaries.", bold_prefix="Dynamic Calculation: ")
    mr.add_bullet("Provide illustrative environmental metrics estimating kilograms of CO2 diverted and grams of precious metals recovered.", bold_prefix="Impact Metrics: ")
    mr.add_bullet("Enable authenticated users to persist calculations into rewards_history for continuous recycling engagement.", bold_prefix="History Tracking: ")

    mr.add_sec_heading("6.9 Admin Dashboard Objectives")
    mr.add_bullet("Provide an executive operations dashboard displaying verified facility counts, registered users, and active device categories.", bold_prefix="Executive KPI Analytics: ")
    mr.add_bullet("Render interactive Chart.js visualizations illustrating facility verification status and state-wise capacity distributions.", bold_prefix="Chart.js Visualizations: ")
    mr.add_bullet("Equip administrators with complete CRUD capabilities (Create, Read, Update, Delete) for facilities, users, and device point values.", bold_prefix="Administrative CRUD: ")
    mr.add_bullet("Enable batch CSV ingestion of official CPCB rosters with schema validation and automatic duplicate skipping.", bold_prefix="Batch CSV Pipeline: ")
    mr.add_bullet("Incorporate a live User Activity Tracking dashboard monitoring search queries, regional filters, and user logins in real time.", bold_prefix="Activity Intelligence: ")

    mr.add_sec_heading("6.10 Data Management and Security")
    mr.add_para("Enforce 100% parameterized SQL query execution, thread-safe database pooling, CSRF token validation, strict Content-Security-Policy headers, and robust session boundaries segregating administrative operations from standard user interfaces.")

    mr.add_sec_heading("6.11 Technical and Academic Objectives")
    mr.add_para("Demonstrate practical mastery of full-stack software engineering: Python Flask web architecture, relational database normalization (3NF), spatial algorithms, automated testing (achieving 100% pass rate across 59 unit tests), and empirical multi-user load profiling.")

    mr.add_page_footer_num("15")

# ==============================================================================
# PAGE 23: CHAPTER 7: EXPECTED OUTCOMES (7.1 to 7.7)
# ==============================================================================
def build_p23():
    mr.add_chapter_title("CHAPTER 7: EXPECTED OUTCOMES")
    mr.add_sec_heading("7.1 Introduction")
    mr.add_para("The expected outcomes define the functional deliverables, performance benchmarks, and tangible environmental advantages achieved upon the successful completion and deployment of EcoLocate.")

    mr.add_sec_heading("7.2 Centralised Recycling Centre Information")
    mr.add_para("A fully structured, indexed MySQL relational repository containing 87 CPCB-authorized recycling and dismantling facilities across India. Users obtain complete facility transparency, including authorized dismantling capacity (MTA), state regulatory authorization, official verified websites, telephone links, and direct email contacts.")

    mr.add_sec_heading("7.3 User-Friendly Search")
    mr.add_para("A high-performance search interface providing instant cascading state-to-city dropdowns, compound keyword matching, and device category filters. Search queries execute within sub-100 ms database latencies without page reloads.")

    mr.add_sec_heading("7.4 Nearby Centre Discovery")
    mr.add_para("Automated proximity detection that retrieves client GPS coordinates via the browser Geolocation API, applies the mathematical Haversine formula against verified facility coordinates, and presents an ascending distance-sorted list of nearby recycling centres.")

    mr.add_sec_heading("7.5 Interactive Map")
    mr.add_para("A fully responsive Leaflet.js interactive map container utilizing OpenStreetMap raster tiles. Facilities are visualized with distinct, color-coded map pins that display interactive modal cards with facility details and direct routing links to Google Maps upon user selection.")

    mr.add_sec_heading("7.6 E-Waste Awareness")
    mr.add_para("A dedicated public educational portal detailing toxic heavy metal hazards (Lead, Mercury, Cadmium), environmental bioaccumulation risks in soil and groundwater, and a step-by-step consumer guide on data sanitization and authorized recycling.")

    mr.add_sec_heading("7.7 Recycling Reward Calculator")
    mr.add_para("An interactive calculation widget that dynamically computes EcoReward incentive points, provides estimated CO2 diversion metrics, and allows authenticated users to log and monitor personal disposal histories over time.")

    mr.add_page_footer_num("16")

# ==============================================================================
# PAGE 24: CHAPTER 7 continued (7.8 to 7.10)
# ==============================================================================
def build_p24():
    mr.add_sec_heading("7.8 Admin Management")
    mr.add_para("A complete administrative management portal accessible exclusively via isolated admin credentials. Administrators can create, update, verify, and delete facilities; ingest official CPCB CSV rosters with duplicate detection; manage device point valuations; activate or deactivate user accounts; and review real-time user search queries and regional activity patterns through the User Activity Tracking dashboard.")

    mr.add_sec_heading("7.9 Additional Expected Outcomes")
    mr.add_bullet("Thread-safe MySQL connection pool (pool_size=25) capable of sustaining 50 concurrent users with 0.0% failure rate.", bold_prefix="Concurrency Performance: ")
    mr.add_bullet("Comprehensive automated test suite containing 59 unit and integration tests covering 100% of core modules.", bold_prefix="Automated Verification: ")
    mr.add_bullet("Automated backup utility (backup_restore_db.py) enabling point-in-time JSON database snapshots and restoration.", bold_prefix="Disaster Recovery: ")
    mr.add_bullet("Defensive security headers (CSP, nosniff, SAMEORIGIN, CSRF tokens) protecting against OWASP Top 10 web vulnerabilities.", bold_prefix="Production Security: ")
    mr.add_bullet("Production-ready configuration files (Procfile, wsgi.py, render.yaml, .env.example) for cloud hosting on Render.", bold_prefix="Cloud Readiness: ")

    mr.add_sec_heading("7.10 Success Indicators")
    mr.add_bullet("Database contains 87 verified CPCB recycling facilities with audited contact links.", bold_prefix="Indicator 1 (Data Integrity): ")
    mr.add_bullet("Haversine formula calculates distances accurately matching mathematical benchmarks within 0.01 km.", bold_prefix="Indicator 2 (Geospatial Precision): ")
    mr.add_bullet("All 59 automated test cases pass with zero errors in under 2 seconds.", bold_prefix="Indicator 3 (Test Verification): ")
    mr.add_bullet("Multi-user concurrency test achieves 203.43 requests/second with 0.0% error rate.", bold_prefix="Indicator 4 (Throughput): ")
    mr.add_bullet("Non-admin users are strictly blocked from accessing administrative routes (HTTP 302 redirect).", bold_prefix="Indicator 5 (Security Isolation): ")
    mr.add_bullet("Admin changes (add, edit, delete facility) reflect in user search results in real time with zero cache lag.", bold_prefix="Indicator 6 (Live Sync): ")

    mr.add_page_footer_num("17")

# ==============================================================================
# PAGE 25: CHAPTER 8: PROJECT TIMELINE (8.1, 8.2)
# ==============================================================================
def build_p25():
    mr.add_chapter_title("CHAPTER 8: PROJECT TIMELINE")
    mr.add_sec_heading("8.1 Major Development Activities")
    mr.add_para("The development of EcoLocate was structured across five continuous, sequential phases spanning a five-week engineering cycle. Key developmental milestones included:")
    mr.add_bullet("Formulation of problem statement, CPCB statutory review, stakeholder analysis, and technical requirement specification.", bold_prefix="Activity 1: ")
    mr.add_bullet("Architecture specification, ER modeling, MySQL 3NF database schema design, and performance index creation.", bold_prefix="Activity 2: ")
    mr.add_bullet("Frontend responsive UI design, Flask routing, Werkzeug password authentication, and Leaflet.js mapping integration.", bold_prefix="Activity 3: ")
    mr.add_bullet("Haversine proximity engine, EcoRewards calculator, Admin dashboard, CSV ingestion, and User Activity tracking.", bold_prefix="Activity 4: ")
    mr.add_bullet("Automated test suite creation (59 tests), 50-user concurrency profiling, security hardening, and documentation.", bold_prefix="Activity 5: ")

    mr.add_sec_heading("8.2 Phase-wise Plan")
    mr.add_para("Table 8.1 outlines the phase-wise schedule, developmental activities, and allocated duration across the project life cycle.")
    time_data = [
        ["Phase 1", "Problem Identification & Requirement Analysis", "1 Week"],
        ["Phase 2", "System Planning, Architecture & Database Design", "1 Week"],
        ["Phase 3", "Frontend Development, Backend APIs & Mapping", "1 Week"],
        ["Phase 4", "Module Integration, Admin Suite & Activity Tracking", "1 Week"],
        ["Phase 5", "Testing, Security Hardening, Review & Documentation", "1 Week"]
    ]
    mr.add_table_custom(["Phase", "Development Activity Description", "Allocated Duration"], time_data, [1.4, 3.8, 1.2], "Table 8.1: Project phases and duration")
    mr.add_para("Total estimated engineering duration: 5 Weeks (executed systematically from initial concept to deployment verification).")

    mr.add_page_footer_num("18")

# ==============================================================================
# PAGE 26: CHAPTER 8 continued (Figure 8.1, 8.3, 8.4, 8.5)
# ==============================================================================
def build_p26():
    # Insert Gantt chart
    gantt_img = os.path.join(diag_dir, 'fig_8_1_timeline.png')
    mr.add_image_figure(gantt_img, 6.2, "Figure 8.1: Project timeline schedule (Gantt chart representation)")

    mr.add_sec_heading("8.3 Weekly Deliverables")
    week_data = [
        ["Week 1", "Problem Identification & Requirements", "SRS document, CPCB data analysis, stakeholder requirements."],
        ["Week 2", "Architecture & Database Design", "3NF relational schema, ER diagrams, DFDs, indexing plan."],
        ["Week 3", "Frontend & Backend Development", "Responsive UI, Flask REST APIs, Leaflet mapping, authentication."],
        ["Week 4", "Module Integration & Admin Suite", "Haversine engine, rewards calculator, admin CRUD, activity logs."],
        ["Week 5", "Testing, Security & Documentation", "59 automated tests, concurrency test (203 RPS), project report."]
    ]
    mr.add_table_custom(["Week", "Phase Activity", "Major Technical Deliverable Produced"], week_data, [1.1, 2.2, 3.1], "Table 8.2: Week-wise activities and deliverables")

    mr.add_sec_heading("8.4 Completion Criteria")
    mr.add_para("Project completion criteria required that: (a) MySQL database connects reliably with connection pooling; (b) 87 CPCB facilities are searchable; (c) Leaflet map plots coordinates accurately; (d) Haversine distance matches mathematical benchmarks; (e) all 59 automated test cases pass with 0 errors; and (f) admin changes reflect in user search results in real time.")

    mr.add_sec_heading("8.5 Development Methodology")
    mr.add_para("The project adopted an Agile Spiral software engineering methodology, combining iterative module delivery with rigorous verification gates at the conclusion of each phase.")

    mr.add_page_footer_num("19")

# ==============================================================================
# PAGE 27: CHAPTER 9: SYSTEM DESIGN (9.1, 9.2, Figure 9.1)
# ==============================================================================
def build_p27():
    mr.add_chapter_title("CHAPTER 9: SYSTEM DESIGN")
    mr.add_sec_heading("9.1 Introduction")
    mr.add_para("System design converts the functional and architectural requirements established in previous chapters into an engineering blueprint. It defines the multi-tier software architecture, user roles, use-case models, data flow diagrams, entity-relationship models, relational database schemas, module interactions, and security protocols.")

    mr.add_sec_heading("9.2 System Architecture")
    mr.add_para("EcoLocate is structured upon an enterprise three-layer software architecture, segregating presentation, application logic, and data storage into decoupled, maintainable tiers:")
    mr.add_bullet("Runs within the client web browser. Built with HTML5, CSS3, vanilla ES6+ JavaScript, and Leaflet.js with OpenStreetMap. Handles responsive rendering, touch-friendly interactions, client geolocation retrieval, and asynchronous AJAX/JSON communications.", bold_prefix="Presentation Layer (Client): ")
    mr.add_bullet("Hosted on the Python Flask WSGI server. Contains routing logic, Werkzeug session management, the Haversine trigonometric distance engine, administrative controllers, and the user activity tracking logger.", bold_prefix="Application Layer (Server): ")
    mr.add_bullet("Utilizes MySQL (ewaste_db) with InnoDB engine. Manages persistent entities (users, admins, centres, devices, rewards_history, user_activity) through thread-safe connection pooling and parameterized query execution.", bold_prefix="Data Layer (Database): ")

    arch_img = os.path.join(diag_dir, 'fig_9_1_architecture.png')
    mr.add_image_figure(arch_img, 5.8, "Figure 9.1: Three-layer software architecture of EcoLocate")

    mr.add_page_footer_num("20")

# ==============================================================================
# PAGE 28: CHAPTER 9 continued (9.3 Table 9.1, 9.4 Figure 9.2)
# ==============================================================================
def build_p28():
    mr.add_sec_heading("9.3 Users and Roles")
    mr.add_para("The platform defines three distinct user personas, each granted strictly demarcated permissions:")
    roles_data = [
        ["Public Citizen (Guest)", "Search centres, view map pins, detect nearby facilities, read awareness curriculum, calculate reward points anonymously."],
        ["Registered User", "All guest privileges plus secure session sign-in, profile viewing, and persisting calculation history into personal rewards ledger."],
        ["Platform Administrator", "Exclusive access to /admin/* portal: create/edit/delete facilities, CSV batch import, user moderation, and live activity audit tracking."]
    ]
    mr.add_table_custom(["User Role", "Privileges, Responsibilities & Operational Scope"], roles_data, [1.8, 4.6], "Table 9.1: User roles and responsibilities")

    mr.add_sec_heading("9.4 Use-Case Diagram")
    mr.add_para("Figure 9.2 illustrates the primary system actors and the complete taxonomy of functional use cases supported across citizen and administrative interfaces.")

    uc_img = os.path.join(diag_dir, 'fig_9_2_use_case.png')
    mr.add_image_figure(uc_img, 5.8, "Figure 9.2: Use-case diagram of EcoLocate portal")

    mr.add_page_footer_num("21")

# ==============================================================================
# PAGE 29: CHAPTER 9 continued (9.5 DFD, Figure 9.3, Figure 9.4)
# ==============================================================================
def build_p29():
    mr.add_sec_heading("9.5 Data Flow Diagrams")
    mr.add_para("Data Flow Diagrams (DFDs) model the transmission, processing, and transformation of information across external entities, software processes, and database repositories.")
    mr.add_para("Figure 9.3 presents the Context-Level Diagram (Level 0), portraying EcoLocate as a single integrated process interacting with citizen users, registered accounts, and administrators.")

    dfd0_img = os.path.join(diag_dir, 'fig_9_3_dfd_level0.png')
    mr.add_image_figure(dfd0_img, 5.2, "Figure 9.3: Level-0 data flow diagram (context diagram)")

    mr.add_para("Figure 9.4 decomposes the system into five core functional sub-processes: 1.0 User Authentication, 2.0 Facility Search & Maps, 3.0 EcoRewards Calculation, 4.0 Facility Management, and 5.0 User Activity Tracking.")

    dfd1_img = os.path.join(diag_dir, 'fig_9_4_dfd_level1.png')
    mr.add_image_figure(dfd1_img, 5.2, "Figure 9.4: Level-1 data flow diagram of functional subsystems")

    mr.add_page_footer_num("22")

# ==============================================================================
# PAGE 30: CHAPTER 9 continued (9.6 Figure 9.5, 9.7 Table 9.2)
# ==============================================================================
def build_p30():
    mr.add_sec_heading("9.6 Entity-Relationship Design")
    mr.add_para("The relational database schema is modeled around five core business entities: users, admins, centres, devices, rewards_history, and user_activity. Relational integrity is enforced using foreign key constraints with ON DELETE SET NULL cascades.")

    er_img = os.path.join(diag_dir, 'fig_9_5_er_diagram.png')
    mr.add_image_figure(er_img, 5.4, "Figure 9.5: Entity-relationship diagram of EcoLocate relational schema")

    mr.add_sec_heading("9.7 Database Design and Data Dictionary")
    mr.add_para("The following data dictionary tables define the structural schema, data types, constraints, and operational descriptions for each database table in ewaste_db.")
    
    users_data = [
        ["id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique internal user identifier"],
        ["full_name", "VARCHAR(100)", "NOT NULL", "Full legal name of registered user"],
        ["email", "VARCHAR(120)", "NOT NULL, UNIQUE", "User email address (login credential)"],
        ["password_hash", "VARCHAR(255)", "NOT NULL", "Werkzeug scrypt cryptographic password hash"],
        ["is_active", "TINYINT(1)", "DEFAULT 1", "Account status flag (1=Active, 0=Deactivated)"],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Account registration timestamp"]
    ]
    mr.add_table_custom(["Field Name", "Data Type", "Constraints / Key", "Field Purpose & Description"], users_data, [1.4, 1.4, 1.8, 1.8], "Table 9.2: Data dictionary – Table: users")

    mr.add_page_footer_num("23")

# ==============================================================================
# PAGE 31: CHAPTER 9 continued (Table 9.3, Table 9.4, Table 9.5)
# ==============================================================================
def build_p31():
    centres_data = [
        ["id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique recycling facility identifier"],
        ["centre_name", "VARCHAR(255)", "NOT NULL", "Registered corporate name of recycling centre"],
        ["state", "VARCHAR(100)", "NOT NULL, INDEXED", "Indian State / Union Territory"],
        ["city", "VARCHAR(100)", "NOT NULL, INDEXED", "City / District municipality"],
        ["address", "TEXT", "NOT NULL", "Complete physical postal street address"],
        ["capacity_mta", "VARCHAR(100)", "NULL", "Licensed recycling capacity in Metric Tonnes/Annum"],
        ["website_url", "VARCHAR(255)", "NULL", "Audited official website or verified domain"],
        ["phone_number", "VARCHAR(100)", "NULL", "Verified operational telephone contact channel"],
        ["latitude", "DECIMAL(10,8)", "NULL, INDEXED", "WGS84 decimal latitude coordinate"],
        ["longitude", "DECIMAL(11,8)", "NULL, INDEXED", "WGS84 decimal longitude coordinate"]
    ]
    mr.add_table_custom(["Field Name", "Data Type", "Constraints", "Field Purpose & Description"], centres_data, [1.4, 1.3, 1.6, 2.1], "Table 9.3: Data dictionary – Table: centres")

    devices_data = [
        ["id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique electronic device category identifier"],
        ["device_name", "VARCHAR(100)", "NOT NULL, UNIQUE", "Category name (Mobile Phone, Laptop, etc.)"],
        ["points_per_unit", "INT", "NOT NULL", "EcoReward incentive points awarded per unit"]
    ]
    mr.add_table_custom(["Field Name", "Data Type", "Constraints", "Field Purpose & Description"], devices_data, [1.4, 1.4, 1.8, 1.8], "Table 9.4: Data dictionary – Table: devices")

    act_data = [
        ["activity_id", "BIGINT", "PRIMARY KEY, AUTO_INC", "Unique audit activity record identifier"],
        ["user_id", "INT", "FOREIGN KEY, NULL", "FK referencing users(id) ON DELETE SET NULL"],
        ["activity_type", "VARCHAR(50)", "NOT NULL, INDEXED", "Event type: login, logout, search, centre_view, rewards_calc"],
        ["search_query", "VARCHAR(255)", "NULL", "Keyword query or calculation detail"],
        ["state / city", "VARCHAR(100)", "NULL, INDEXED", "Regional geographic filter parameters"],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT", "Timestamp of event occurrence"]
    ]
    mr.add_table_custom(["Field Name", "Data Type", "Constraints", "Field Purpose & Description"], act_data, [1.4, 1.3, 1.6, 2.1], "Table 9.5: Data dictionary – Table: user_activity")

    mr.add_page_footer_num("24")

# ==============================================================================
# PAGE 32: CHAPTER 9 continued (9.8 Module Design, 9.9 Figure 9.6)
# ==============================================================================
def build_p32():
    mr.add_sec_heading("9.8 Module Design")
    mr.add_para("The system is partitioned into discrete, high-cohesion, low-coupling modules:")
    mr.add_bullet("Validates user credentials against scrypt password hashes, issues secure HTTP session cookies, and handles logout.", bold_prefix="Authentication Module: ")
    mr.add_bullet("Executes parameterized SQL queries with cascading state/city filters and keyword searches against the indexed centres table.", bold_prefix="Search & Filtering Module: ")
    mr.add_bullet("Applies the Haversine formula to compute great-circle distances between client GPS coordinates and facility locations.", bold_prefix="Haversine Geolocation Module: ")
    mr.add_bullet("Renders the Leaflet.js map canvas, clusters markers, and binds interactive facility popup cards.", bold_prefix="Interactive Map Module: ")
    mr.add_bullet("Calculates reward points (Quantity x Points Per Unit), estimates CO2 savings, and persists history.", bold_prefix="EcoRewards Module: ")
    mr.add_bullet("Provides facility CRUD operations, CSV batch ingestion, and live User Activity analytics for authorized admins.", bold_prefix="Admin Management Module: ")

    mr.add_sec_heading("9.9 Process Flow")
    mr.add_para("Figure 9.6 illustrates the end-to-end execution flow of a typical user session across search, map discovery, calculation, and activity logging.")

    flow_img = os.path.join(diag_dir, 'fig_9_6_flowchart.png')
    mr.add_image_figure(flow_img, 4.4, "Figure 9.6: Flowchart of a typical user interaction session")

    mr.add_page_footer_num("25")

# ==============================================================================
# PAGE 33: CHAPTER 9 continued (9.10, 9.11, 9.12)
# ==============================================================================
def build_p33():
    mr.add_sec_heading("9.10 User Interface Design")
    mr.add_para("The visual interface follows a modern Emerald and Forest Green environmental SaaS design language. Top-level sticky navigation provides access to Directory, Map, Awareness, Rewards, and Sign-In. Responsive CSS media queries ensure optimal rendering across mobile viewports (with an off-canvas drawer navigation), tablets, and high-resolution desktop displays. Form fields feature real-time client validation, touch-friendly tap targets, and accessible ARIA attributes.")

    mr.add_sec_heading("9.11 Security Design")
    mr.add_bullet("Passwords are protected using Werkzeug's generate_password_hash function with scrypt key derivation. Plaintext passwords and password hashes are never exposed in administrative templates or API responses.", bold_prefix="Cryptographic Password Security: ")
    mr.add_bullet("All routes under /admin/* are guarded by the custom @admin_required decorator. Unauthorized requests are intercepted and redirected to /admin/login.", bold_prefix="Role-Based Boundary Protection: ")
    mr.add_bullet("Every SQL query in the application is executed through parameterized statements (cursor.execute(sql, params)), preventing SQL injection.", bold_prefix="Parameterized Query Execution: ")
    mr.add_bullet("Flask-WTF validates unique cryptographic tokens on all POST requests, mitigating Cross-Site Request Forgery.", bold_prefix="CSRF Defense: ")
    mr.add_bullet("Custom middleware injects strict Content-Security-Policy (CSP), X-Frame-Options: SAMEORIGIN, and X-Content-Type-Options: nosniff headers on every HTTP response.", bold_prefix="Defensive HTTP Headers: ")
    mr.add_bullet("User activity audit logs record search queries and regional filters without collecting personally identifying credentials or raw GPS coordinates.", bold_prefix="Privacy Preservation: ")

    mr.add_sec_heading("9.12 Chapter Summary")
    mr.add_para("This chapter detailed the comprehensive system design of EcoLocate, including its three-layer architecture, user roles, use-case models, DFDs, ER design, relational schemas, module interactions, process workflows, and security safeguards, establishing the technical foundation for implementation.")

    mr.add_page_footer_num("26")

print('Compiled Pages 21 to 33.')
