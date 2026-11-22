"""
Calibrated Pages 34 to 40 for EcoLocate Academic Report (Chapters 10, 11, Appendix, References)
Ensures EXACTLY 1 page per function, bringing total document count to EXACTLY 40 PAGES.
Student: YOGESH (Roll No. 241306039)
University: SGT UNIVERSITY
"""
import os
import make_report as mr
doc = mr.doc
screen_dir = mr.screen_dir

# ==============================================================================
# PAGE 34: CHAPTER 10: IMPLEMENTATION AND TESTING (10.1 to 10.8)
# ==============================================================================
def build_p34():
    mr.add_chapter_title("CHAPTER 10: IMPLEMENTATION AND TESTING")
    mr.add_sec_heading("10.1 Introduction")
    mr.add_para("This chapter documents the technical implementation and verification of EcoLocate. It describes the runtime development environment, frontend responsive design, Python Flask backend routing, MySQL connection pooling, Leaflet geospatial mapping, and automated testing across 59 unit and integration test cases.")

    mr.add_sec_heading("10.2 Development Environment")
    mr.add_para("The application was developed on Windows 11 using Python 3.13, Flask 3.1.1, and XAMPP MariaDB (port 3307). Code editing and profiling were conducted in Visual Studio Code with Git version control connected to GitHub.")

    mr.add_sec_heading("10.3 Frontend Implementation")
    mr.add_para("The presentation tier utilizes semantic HTML5, custom responsive CSS3, and vanilla JavaScript. Dynamic DOM manipulation handles asynchronous fetch() requests to the backend REST endpoints, updating search results and map markers without page reloads.")

    mr.add_sec_heading("10.4 Backend Implementation")
    mr.add_para("The backend is structured into modular Python components: app.py (public routing, search, rewards, geolocation), admin.py (administrative blueprint), db.py (thread-safe connection pooling and parameterized query execution), and config.py (environment configuration).")

    mr.add_sec_heading("10.5 Database Implementation")
    mr.add_para("MySQL database ewaste_db was constructed with 6 normalized tables (users, admins, centres, devices, rewards_history, user_activity). A thread-safe connection pool (mysql.connector.pooling.MySQLConnectionPool) manages 25 pooled connections with autocommit enabled, eliminating thread contention during concurrent traffic.")

    mr.add_sec_heading("10.6 User Authentication Implementation")
    mr.add_para("User registration validates full name, email uniqueness, and password strength. Password hashing uses Werkzeug's generate_password_hash (scrypt algorithm). Sessions are managed using secure, HTTP-only Flask cookies.")

    mr.add_sec_heading("10.7 Recycling Centre Search Implementation")
    mr.add_para("The /api/centres endpoint executes dynamic SQL lookups supporting state, city, and keyword filtering, returning structured JSON payloads with pagination (10 facilities per page across 87 verified centres).")

    mr.add_sec_heading("10.8 Location and Map Implementation")
    mr.add_para("Client coordinates from the browser Geolocation API are transmitted to /api/centres/nearby. The backend calculates distance using the Haversine formula: d = 2R * arcsin(sqrt(sin^2(dlat/2) + cos(lat1)*cos(lat2)*sin^2(dlon/2))) with Earth radius R = 6371 km, sorting facilities by ascending proximity. Leaflet.js renders these facilities on OpenStreetMap tiles with interactive modal cards.")

    mr.add_page_footer_num("27")

# ==============================================================================
# PAGE 35: CHAPTER 10 continued (10.9 to 10.15, Table 10.1)
# ==============================================================================
def build_p35():
    mr.add_sec_heading("10.9 Reward Calculator Implementation")
    mr.add_para("The /api/rewards/calculate endpoint processes device ID and quantity, computing: Total Points = Quantity x Points Per Unit. Authenticated users persist calculations into rewards_history.")

    mr.add_sec_heading("10.10 Admin Panel Implementation")
    mr.add_para("The admin panel (/admin/*) is guarded by the @admin_required decorator. Administrators can add, edit, verify, and delete recycling centres, view executive Chart.js analytics, and moderate user accounts.")

    mr.add_sec_heading("10.11 CSV Import Implementation")
    mr.add_para("The /admin/centres/import-csv endpoint allows batch ingestion of official CPCB CSV rosters with column schema validation and automatic duplicate skipping.")

    mr.add_sec_heading("10.12 User Activity Tracking Implementation")
    mr.add_para("User actions (logins, searches, facility views, calculations) are logged to user_activity. The /admin/activities dashboard displays KPI counts, filters, and audit trails for regional demand monitoring.")

    mr.add_sec_heading("10.13 Application Testing & 10.14 Test Cases")
    mr.add_para("A comprehensive automated test suite (test_app.py) containing 59 test cases was executed using Python's unittest framework, achieving a 100% pass rate in 1.839 seconds.")
    
    test_data = [
        ["Tests 1–10", "Authentication & Security", "User registration, scrypt hashing, duplicate rejection, session, logout, role separation.", "PASS"],
        ["Tests 11–20", "Directory Search & Filters", "Dynamic states/cities, keyword search, compound filters, pagination (87 centres), contact integrity.", "PASS"],
        ["Tests 21–30", "Geospatial & Proximity", "Haversine algorithm mathematical accuracy (R=6371 km), Leaflet map endpoint, distance formatting.", "PASS"],
        ["Tests 31–40", "Awareness & EcoRewards", "Curriculum cards, hazardous materials, quantity validation, calculation formula, tenant privacy.", "PASS"],
        ["Tests 41–50", "Admin Management", "Admin auth, Chart.js stats, facility CRUD, CSV batch ingestion, user moderation, route blocking.", "PASS"],
        ["Tests 51–59", "User Activity & Live Sync", "user_activity schema, search logging, centre view logging, live DB sync (Admin CRUD -> Search).", "PASS"]
    ]
    mr.add_table_custom(["Test Suite", "Functional Module", "Verification Focus & Key Operational Checks", "Status"], test_data, [1.1, 1.5, 3.3, 0.6], "Table 10.1: Summary of automated test suite results")

    mr.add_sec_heading("10.15 Testing Summary")
    mr.add_para("All 59 test cases executed successfully without errors. A 50-user concurrency test demonstrated a throughput of 203.43 requests/second with 0.0% failure rate, confirming production readiness.")

    mr.add_page_footer_num("28")

# ==============================================================================
# PAGE 36: CHAPTER 11: CONCLUSION AND FUTURE SCOPE (11.1 to 11.3)
# ==============================================================================
def build_p36():
    mr.add_chapter_title("CHAPTER 11: CONCLUSION AND FUTURE SCOPE")
    mr.add_sec_heading("11.1 Project Conclusion")
    mr.add_para("The EcoLocate – E-Waste Facility Locator project successfully resolves the critical information barrier in India's electronic waste management ecosystem. By transforming static government rosters into an interactive, location-aware web platform, EcoLocate empowers citizens, institutions, and regulatory bodies to divert hazardous e-waste into certified formal recycling streams.")
    mr.add_para("Key accomplishments realized across the project life cycle include:")
    mr.add_bullet("Centralized, indexed repository of 87 CPCB-authorized facilities across Indian states with verified contact links.", bold_prefix="Comprehensive Verified Directory: ")
    mr.add_bullet("Integration of the Haversine trigonometric formula with Leaflet.js and OpenStreetMap for accurate proximity discovery.", bold_prefix="Geospatial Proximity Intelligence: ")
    mr.add_bullet("Dynamic points formula estimating CO2 diversion and raw material recovery to incentivize responsible disposal.", bold_prefix="EcoRewards Incentive Framework: ")
    mr.add_bullet("Full facility CRUD, CSV batch ingestion, user moderation, and real-time user activity analytics.", bold_prefix="Executive Administrative Control: ")
    mr.add_bullet("Werkzeug scrypt password hashing, session cookies, CSRF defense, and strict administrative boundary enforcement.", bold_prefix="Production Security Architecture: ")
    mr.add_bullet("Thread-safe connection pooling sustaining 50 concurrent users at 203+ RPS and 59 automated tests passing at 100%.", bold_prefix="Robust Concurrency & Verification: ")

    mr.add_sec_heading("11.2 Future Scope")
    mr.add_bullet("Integration with third-party logistics APIs (e.g., Delhivery, Dunzo) to enable doorstep collection of e-waste.", bold_prefix="Doorstep Courier Logistics: ")
    mr.add_bullet("Integration with UPI, digital wallets, or retail voucher APIs to allow users to redeem EcoPoints for tangible rewards.", bold_prefix="Reward Monetization: ")
    mr.add_bullet("Deployment of deep learning computer vision models to identify device categories automatically from smartphone photos.", bold_prefix="AI-Powered E-Waste Recognition: ")
    mr.add_bullet("Development of cross-platform mobile apps for Android and iOS using Flutter or React Native.", bold_prefix="Native Mobile Applications: ")
    mr.add_bullet("Direct digital data integration with SPCB and CPCB regulatory portals for real-time compliance auditing.", bold_prefix="IoT Smart Bin Telemetry: ")

    mr.add_sec_heading("11.3 Final Conclusion")
    mr.add_para("EcoLocate demonstrates the effective application of modern computer science and software engineering principles to a vital environmental challenge. The platform establishes an accessible, scalable, and secure foundation for sustainable electronic waste management in India.")

    mr.add_page_footer_num("29")

# ==============================================================================
# PAGE 37: APPENDIX (Appendix A & Appendix B Part 1)
# ==============================================================================
def build_p37():
    mr.add_chapter_title("APPENDIX")
    mr.add_sec_heading("Appendix A: Database Tables")
    mr.add_para("The ewaste_db database comprises six core relational entities designed to third normal form (3NF):")
    app_a_data = [
        ["users", "Stores registered citizen account profiles, scrypt password hashes, and active status."],
        ["admins", "Maintains isolated credentials and authentication records for system administrators."],
        ["centres", "Stores CPCB-authorized recycling facilities, capacities, contact channels, and coordinates."],
        ["devices", "Catalogs electronic device categories and associated EcoReward incentive point valuations."],
        ["rewards_history", "Records authenticated user calculation entries, quantities, and cumulative EcoPoints."],
        ["user_activity", "Maintains an anonymous audit trail of search queries, state/city filters, and user logins."]
    ]
    mr.add_table_custom(["Database Entity", "System Purpose & Relational Role"], app_a_data, [1.5, 4.8], "Table 11.1: Database entities and their functional purpose")

    mr.add_sec_heading("Appendix B: Project Screenshots")
    mr.add_para("The following pages present actual screen captures of the running EcoLocate application:")

    img_b1 = os.path.join(screen_dir, 'fig_b1_home.png')
    mr.add_image_figure(img_b1, 4.4, "Figure B.1: EcoLocate home page and hero navigation interface")

    mr.add_page_footer_num("30")

# ==============================================================================
# PAGE 38: APPENDIX B continued (Figure B.2 & Figure B.3)
# ==============================================================================
def build_p38():
    mr.add_sec_heading("Appendix B: Project Screenshots (Continued)")

    img_b4 = os.path.join(screen_dir, 'fig_b4_centres_search.png')
    mr.add_image_figure(img_b4, 4.4, "Figure B.2: Recycling centre directory search, dynamic filters & interactive Leaflet map")

    img_b8 = os.path.join(screen_dir, 'fig_b8_admin_dashboard.png')
    mr.add_image_figure(img_b8, 4.4, "Figure B.3: Administrative executive dashboard with Chart.js analytics & activity logs")

    mr.add_page_footer_num("31")

# ==============================================================================
# PAGE 39: APPENDIX C & APPENDIX D
# ==============================================================================
def build_p39():
    mr.add_sec_heading("Appendix B: Project Screenshots (Continued)")
    img_b10 = os.path.join(screen_dir, 'fig_b10_admin_activities.png')
    mr.add_image_figure(img_b10, 4.2, "Figure B.4: Real-time user activity tracking portal and search audit trail")

    mr.add_sec_heading("Appendix C: Representative Source Code Snippets")
    mr.add_para("Listing 10.1: Haversine Great-Circle Distance Engine (app.py)", bold_prefix="Code Snippet 1: ")
    mr.add_para("def haversine_distance(lat1, lon1, lat2, lon2):\n    R = 6371.0 # Earth radius in km\n    dlat = math.radians(lat2 - lat1); dlon = math.radians(lon2 - lon1)\n    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2\n    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))")

    mr.add_sec_heading("Appendix D: User Manual")
    manual_steps = [
        "1. Open the portal in browser (http://127.0.0.1:5000/ for local execution).",
        "2. Navigate to 'Locate Centres' to view all certified recycling facilities across India.",
        "3. Select State and City or click 'Find Near Me' to detect nearby facilities via GPS.",
        "4. Click on any facility card to view full address, verified phone, email, and Google directions.",
        "5. Visit 'Awareness' to understand toxic heavy metal risks and 4-step recycling guidelines.",
        "6. Open 'Rewards Calculator' to calculate estimated EcoPoints for discarded electronics.",
        "7. For administrators: sign in at /admin/login to manage facilities, CSV rosters, and activity logs."
    ]
    for step in manual_steps:
        mr.add_para(step)

    mr.add_page_footer_num("32")

# ==============================================================================
# PAGE 40: REFERENCES
# ==============================================================================
def build_p40():
    mr.add_chapter_title("REFERENCES")
    refs = [
        "[1] Central Pollution Control Board (CPCB), “List of Registered E-Waste Dismantlers and Recyclers in India,” Ministry of Environment, Forest and Climate Change, Government of India, 2024. [Online]. Available: https://cpcb.nic.in/e-waste/",
        "[2] Ministry of Environment, Forest and Climate Change (MoEFCC), “E-Waste (Management) Rules, 2022,” The Gazette of India, Extraordinary, Part II, Section 3, Sub-section (ii), Nov. 2, 2022.",
        "[3] Ministry of Electronics and Information Technology (MeitY), “National Policy on Electronics,” Government of India, 2019. [Online]. Available: https://www.meity.gov.in/",
        "[4] United Nations Institute for Training and Research (UNITAR), “The Global E-waste Monitor 2024: Electronic Waste Rising, but Recycling Falling Behind,” Geneva, Switzerland, 2024.",
        "[5] R. S. Pressman and B. R. Maxim, Software Engineering: A Practitioner’s Approach, 9th ed. New York, NY, USA: McGraw-Hill Education, 2020.",
        "[6] I. Sommerville, Software Engineering, 10th ed. Boston, MA, USA: Pearson Education, 2016.",
        "[7] R. Elmasri and S. B. Navathe, Fundamentals of Database Systems, 7th ed. Boston, MA, USA: Pearson, 2017.",
        "[8] A. Silberschatz, H. F. Korth, and S. Sudarshan, Database System Concepts, 7th ed. New York, NY, USA: McGraw-Hill, 2019.",
        "[9] P. Jalote, An Integrated Approach to Software Engineering, 3rd ed. New York, NY, USA: Springer, 2005.",
        "[10] B. W. Boehm, “A spiral model of software development and enhancement,” Computer, vol. 21, no. 5, pp. 61–72, May 1988.",
        "[11] M. Grinberg, Flask Web Development: Developing Web Applications with Python, 2nd ed. Sebastopol, CA, USA: O’Reilly Media, 2018.",
        "[12] Pallets Projects, “Flask Documentation (Version 3.1.x),” 2024. [Online]. Available: https://flask.palletsprojects.com/",
        "[13] Oracle Corporation, “MySQL 8.0 Reference Manual: Thread Pooling and InnoDB Architecture,” 2024. [Online]. Available: https://dev.mysql.com/doc/",
        "[14] V. Agafonkin, “Leaflet: An Open-Source JavaScript Library for Mobile-Friendly Interactive Maps,” 2024. [Online]. Available: https://leafletjs.com/",
        "[15] OpenStreetMap Contributors, “OpenStreetMap Collaborative Mapping Data,” OpenStreetMap Foundation, 2024. [Online]. Available: https://www.openstreetmap.org/",
        "[16] R. W. Sinnott, “Virtues of the Haversine,” Sky and Telescope, vol. 68, no. 2, p. 159, 1984.",
        "[17] OWASP Foundation, “OWASP Top 10: The Ten Most Critical Web Application Security Risks,” 2021. [Online]. Available: https://owasp.org/www-project-top-ten/",
        "[18] National Institute of Standards and Technology (NIST), “Framework for Improving Critical Infrastructure Cybersecurity (CSF 2.0),” NIST Special Publication, 2024.",
        "[19] World Health Organization (WHO), “Children and Digital Dumpsites: E-waste Exposure and Child Health,” Geneva, Switzerland: World Health Organization, 2021.",
        "[20] United States Environmental Protection Agency (US EPA), “Cleaning Up Electronic Waste (E-Waste),” 2023. [Online]. Available: https://www.epa.gov/"
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.alignment = mr.WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.11
        p.paragraph_format.space_after = mr.Pt(3)
        p.add_run(r).font.size = mr.Pt(8)

    mr.add_page_footer_num("33")

print('Compiled Calibrated Pages 34 to 40.')
