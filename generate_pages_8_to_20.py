"""
Pages 8 to 20 for EcoLocate Academic Report (Chapters 1 to 5)
Student: YOGESH (Roll No. 241306039)
University: SGT UNIVERSITY
"""
import make_report as mr
doc = mr.doc

# ==============================================================================
# PAGE 8: CHAPTER 1: INTRODUCTION (1.1, 1.2, 1.3)
# ==============================================================================
def build_p8():
    mr.add_chapter_title("CHAPTER 1: INTRODUCTION")
    mr.add_sec_heading("1.1 Introduction")
    mr.add_para("The rapid acceleration of consumer electronics manufacturing, shortened product replacement cycles, and widespread adoption of digital technologies have made electronic waste (e-waste) the fastest-growing solid waste stream globally. Electronic waste encompasses all discarded electrical and electronic equipment—ranging from mobile phones, laptops, and computer peripherals to televisions, battery packs, and household appliances. While these devices drive digital transformation and economic productivity, their improper disposal poses severe ecological and toxicological threats.")
    mr.add_para("In India, despite established statutory frameworks formulated by the Central Pollution Control Board (CPCB) and State Pollution Control Boards (SPCBs), a significant percentage of discarded electronic devices ends up in municipal landfills or the unorganized informal recycling sector. The primary obstacle faced by citizens and corporate institutions is not the absence of authorized dismantlers, but the absence of a reliable, user-friendly digital system to locate, verify, and contact authorized facilities.")
    mr.add_para("This project develops EcoLocate – E-Waste Facility Locator, an enterprise-grade geographic web application built using Python, Flask, MySQL, and Leaflet.js with OpenStreetMap. EcoLocate bridges the critical information divide by providing an intuitive, transparent, and verified directory of authorized recycling centres, empowering citizens to divert hazardous heavy metals into circular supply chains.")

    mr.add_sec_heading("1.2 Background")
    mr.add_para("Under the E-Waste (Management) Rules enacted by the Ministry of Environment, Forest and Climate Change (MoEFCC), formal recycling units must possess specialized environmental authorization, certified pollution control measures, and scientific material recovery infrastructure. However, official CPCB rosters are distributed in static tabular formats and PDF files, making it tedious for ordinary citizens to identify nearby facilities, verify working domains, or obtain geographic directions.")
    mr.add_para("EcoLocate transforms static regulatory records into an interactive geospatial platform. By integrating browser geolocation, Haversine proximity calculations, and interactive map visualizations, the application makes authorized recycling accessible to every citizen.")

    mr.add_sec_heading("1.3 Problem Statement")
    mr.add_para("Citizens and institutions lack a centralized, verified, and interactive digital platform to locate authorized electronic waste recycling facilities. Traditional disposal routes rely on informal scrap collectors who employ hazardous acid-leaching and open burning techniques, causing severe soil pollution and toxic human exposure. The core problem addressed by this project is the creation of a dedicated, real-time, location-aware E-Waste Facility Locator and environmental awareness portal.", bold_prefix="Core Problem: ")

    mr.add_page_footer_num("1")

# ==============================================================================
# PAGE 9: CHAPTER 1 continued (1.4, 1.5, 1.6, 1.7)
# ==============================================================================
def build_p9():
    mr.add_sec_heading("1.4 Scope")
    mr.add_para("The scope of EcoLocate encompasses user-facing facility discovery, geospatial distance computation, environmental education, incentive gamification, and back-office administrative management. The project provides an end-to-end web system backed by a robust MySQL relational database.")
    mr.add_bullet("User search by State, City, and Device category; proximity detection via Geolocation API and Haversine formula; interactive Leaflet.js map with facility pins; verified official contact channels; educational curriculum on hazardous heavy metals (Lead, Mercury, Cadmium); dynamic EcoRewards calculator with personal history persistence; and role-separated Admin Dashboard for CRUD management, CSV ingestion, and user activity audit tracking.", bold_prefix="In Scope: ")
    mr.add_bullet("Physical courier pickup logistics, third-party payment gateway disbursement for reward redemption, and direct IoT smart-bin telemetry (identified as future enhancements).", bold_prefix="Out of Scope (Current Version): ")

    mr.add_sec_heading("1.5 Need")
    mr.add_para("Traditional solid waste infrastructure cannot safely process hazardous electronic items. Developing a centralized digital locator eliminates information asymmetry, ensures compliance with national recycling policies, prevents toxic groundwater contamination, and fosters citizen participation through measurable recycling incentives.")

    mr.add_sec_heading("1.6 Advantages")
    mr.add_bullet("Centralized MySQL database of 87 CPCB-verified recycling facilities across Indian states.", bold_prefix="Verified Directory: ")
    mr.add_bullet("Zero-cost OpenStreetMap integration with Haversine distance calculations.", bold_prefix="Geospatial Proximity: ")
    mr.add_bullet("Comprehensive curriculum detailing hazards of Lead, Mercury, and Cadmium.", bold_prefix="Environmental Awareness: ")
    mr.add_bullet("Interactive points formula estimating CO2 diversion and raw material recovery.", bold_prefix="Incentivized Rewards: ")
    mr.add_bullet("Full facility CRUD, CSV batch ingestion, and live user search activity tracking.", bold_prefix="Executive Administration: ")
    mr.add_bullet("Werkzeug password hashing, CSRF defense, and strict admin boundary enforcement.", bold_prefix="Security & Privacy: ")

    mr.add_sec_heading("1.7 Project Overview")
    mr.add_para("EcoLocate is engineered using a three-layer software architecture. The frontend utilizes HTML5, CSS3, vanilla JavaScript, and Leaflet.js for responsive mapping. The application tier runs Python Flask with parameterized SQL routing and session management. The data tier utilizes MySQL (ewaste_db) with thread-safe connection pooling and indexed tables.")

    mr.add_page_footer_num("2")

# ==============================================================================
# PAGE 10: CHAPTER 1 continued (1.8, 1.9, 1.10)
# ==============================================================================
def build_p10():
    mr.add_sec_heading("1.8 Project Context")
    mr.add_para("EcoLocate is designed as an environmental technology and digital governance solution. Rather than operating as an isolated database, it combines principles of spatial analysis, public health awareness, circular economic modeling, and administrative oversight. The platform aligns with the broader objectives of the Digital India programme, Smart Cities Mission, and Extended Producer Responsibility (EPR) guidelines issued by the MoEFCC.")

    mr.add_sec_heading("1.9 Organization of the Report")
    mr.add_para("The remainder of this report is organized as follows:")
    mr.add_bullet("Details environmental hazards, public health risks, circular recovery, and academic relevance.", bold_prefix="Chapter 2 (Significance): ")
    mr.add_bullet("Presents functional, non-functional, hardware, software, and security requirements.", bold_prefix="Chapter 3 (Requirement Analysis): ")
    mr.add_bullet("Evaluates traditional disposal limitations and establishes the proposed system's advantages.", bold_prefix="Chapter 4 (Gap Identification): ")
    mr.add_bullet("Specifies hardware specifications, runtime technologies, and software libraries.", bold_prefix="Chapter 5 (Technical Requirements): ")
    mr.add_bullet("Defines primary, functional, geospatial, administrative, and academic goals.", bold_prefix="Chapter 6 (Objectives): ")
    mr.add_bullet("Outlines deliverables, verification metrics, and tangible community benefits.", bold_prefix="Chapter 7 (Expected Outcomes): ")
    mr.add_bullet("Presents the 5-week development methodology and Gantt scheduling chart.", bold_prefix="Chapter 8 (Project Timeline): ")
    mr.add_bullet("Covers 3-layer architecture, Use-Case diagrams, DFDs, ER schema, and Data Dictionary.", bold_prefix="Chapter 9 (System Design): ")
    mr.add_bullet("Documents module implementation details and 59 automated test case executions.", bold_prefix="Chapter 10 (Implementation & Testing): ")
    mr.add_bullet("Summarizes project accomplishments and identifies future enhancement paths.", bold_prefix="Chapter 11 (Conclusion & Future Scope): ")
    mr.add_bullet("Includes database tables, system screenshots, code snippets, manual, and references.", bold_prefix="Appendix & References: ")

    mr.add_sec_heading("1.10 Chapter Summary")
    mr.add_para("This chapter introduced EcoLocate, its statutory background, problem statement, technical scope, practical advantages, and structural organization. By combining Python Flask backend logic, Leaflet geospatial mapping, and MySQL data management, the platform directly resolves the critical challenge of locating authorized electronic waste facilities across India.")

    mr.add_page_footer_num("3")

# ==============================================================================
# PAGE 11: CHAPTER 2: SIGNIFICANCE AND RELEVANCE TO SOCIETY (2.1 to 2.5)
# ==============================================================================
def build_p11():
    mr.add_chapter_title("CHAPTER 2: SIGNIFICANCE AND RELEVANCE TO SOCIETY")
    mr.add_sec_heading("2.1 Introduction")
    mr.add_para("The exponential surge in electronic device consumption has created an urgent societal imperative for scientific waste management. Unlike organic or inert solid waste, electrical and electronic equipment contains an intricate mixture of valuable precious metals (gold, silver, copper, platinum) and highly toxic heavy elements (lead, mercury, cadmium). When electronic waste is discarded carelessly, these hazardous constituents disperse into biosphere ecosystems, causing irreversible environmental contamination and chronic human illnesses.")

    mr.add_sec_heading("2.2 Environmental Significance")
    mr.add_para("Formal, CPCB-authorized recycling facilities employ state-of-the-art automated shredding, magnetic cross-belt separation, optical sorting, and hydrometallurgical leaching processes designed to recover over 95% of constituent materials while capturing toxic gases. Connecting the general public with these certified facilities prevents unscientific landfill dumping and supports ecological preservation.")

    mr.add_sec_heading("2.3 Importance of E-Waste Management")
    mr.add_para("Systematic e-waste diversion directly supports national resource conservation by reintegrating recovered metals back into manufacturing supply chains, substantially decreasing the ecological footprint of virgin mining operations.")

    mr.add_sec_heading("2.4 Environmental and Health Hazards")
    mr.add_bullet("Commonly found in cathode ray tube (CRT) monitors, glass funnels, and printed circuit board soldering alloys. Exposure causes severe neurological disorders, acute kidney impairment, and cognitive deficits in young children.", bold_prefix="Lead (Pb): ")
    mr.add_bullet("Present in fluorescent backlights, flat-panel liquid crystal displays, and medical relays. Inhalation or waterborne ingestion produces central nervous system damage, respiratory collapse, and congenital birth defects.", bold_prefix="Mercury (Hg): ")
    mr.add_bullet("Utilized extensively in rechargeable nickel-cadmium batteries, surface-mount chip resistors, and semiconductor coatings. Bioaccumulates in soils, causing severe renal tubular failure and osteomalacia (Itai-Itai disease).", bold_prefix="Cadmium (Cd): ")

    mr.add_sec_heading("2.5 Benefits of Recycling")
    mr.add_para("Responsible e-waste recycling yields dual advantages: it neutralizes toxic hazards and unlocks circular economic value by recapturing critical raw materials, reducing national import dependence, and curbing carbon emissions.")

    mr.add_page_footer_num("4")

# ==============================================================================
# PAGE 12: CHAPTER 2 continued (2.6 to 2.10)
# ==============================================================================
def build_p12():
    mr.add_sec_heading("2.6 Digital Governance")
    mr.add_para("EcoLocate champions digital governance by translating static government regulatory registries into an interactive, real-time spatial platform. It empowers citizens with accessible data, aligns with the Smart Cities Mission, and operationalizes Extended Producer Responsibility (EPR) mandates through transparent information distribution.")

    mr.add_sec_heading("2.7 Social Impact")
    mr.add_para("By providing a transparent directory, EcoLocate protects vulnerable communities from toxic exposure, promotes certified green jobs within the formal dismantling sector, and shifts consumer mindsets from disposable consumption toward environmental stewardship.")

    stake_data = [
        ["General Citizens", "Locate verified recycling facilities, calculate incentive points, avoid toxic health hazards."],
        ["Authorised Recyclers", "Gain verified public visibility, receive structured e-waste volumes, improve capacity utilization."],
        ["Regulatory Bodies (CPCB)", "Promote formal channel adoption, reduce informal scrap burning, monitor regional compliance."],
        ["Municipal Bodies", "Divert hazardous electronic fractions from municipal landfills, reducing leachate contamination."],
        ["System Administrators", "Centralized facility auditing, user activity intelligence, and streamlined batch data imports."]
    ]
    mr.add_table_custom(["Stakeholder", "Relevance / Tangible Benefit"], stake_data, [1.8, 4.5], "Table 2.1: Stakeholders and their benefits")

    mr.add_sec_heading("2.8 Relevance to the Problem Statement")
    mr.add_para("The project directly resolves the core problem: connecting consumers with authorized recyclers. By organizing facilities with verified domains, direct telephone channels, and OpenStreetMap coordinates, the application removes the logistical friction that historically drove consumers toward the informal waste sector.")

    mr.add_sec_heading("2.9 Academic Significance")
    mr.add_para("Academically, EcoLocate synthesizes key computing disciplines: relational database design (3NF schema, indexing, pooling), geospatial algorithms (Haversine great-circle trigonometry), RESTful API design, front-end responsive mapping, and secure web engineering (cryptographic hashing, CSRF defense, role-based session control).")

    mr.add_sec_heading("2.10 Chapter Summary")
    mr.add_para("This chapter detailed the societal, toxicological, and governance imperative of e-waste recycling, established stakeholder benefits, and highlighted the academic integration of computing principles with environmental sustainability.")

    mr.add_page_footer_num("5")

# ==============================================================================
# PAGE 13: CHAPTER 3: REQUIREMENT ANALYSIS (3.1 to 3.4)
# ==============================================================================
def build_p13():
    mr.add_chapter_title("CHAPTER 3: REQUIREMENT ANALYSIS")
    mr.add_sec_heading("3.1 Introduction")
    mr.add_para("Requirement analysis establishes the complete operational blueprint for EcoLocate. It delineates the functional capabilities expected by users and administrators, specifies non-functional benchmarks for security, performance, and reliability, and defines the hardware, software, and database constraints.")

    mr.add_sec_heading("3.2 Stakeholder Analysis")
    mr.add_para("The primary stakeholders include public citizens (requiring intuitive search, mapping, and rewards estimation), registered users (maintaining saved calculation records), and platform administrators (managing facility registries, user access, and tracking activity metrics).")

    mr.add_sec_heading("3.3 Functional Requirements")
    mr.add_bullet("Users must be able to search facilities using state and city cascading dropdowns and free-text queries.", bold_prefix="FR1 (Facility Search): ")
    mr.add_bullet("The system must detect client coordinates via browser Geolocation API and sort facilities by ascending Haversine distance.", bold_prefix="FR2 (Nearby Discovery): ")
    mr.add_bullet("The system must render facilities on an interactive Leaflet.js map with custom color-coded map pins.", bold_prefix="FR3 (Interactive Mapping): ")
    mr.add_bullet("Users must be able to view verified contact details, official websites, and direct dial links.", bold_prefix="FR4 (Facility Contact): ")
    mr.add_bullet("The platform must provide structured educational curricula regarding hazardous heavy metals (Lead, Mercury, Cadmium).", bold_prefix="FR5 (E-Waste Awareness): ")
    mr.add_bullet("The system must calculate reward points based on device category and quantity, estimating carbon diversion.", bold_prefix="FR6 (Rewards Calculator): ")
    mr.add_bullet("Users must be able to register, log in, and securely persist reward calculations.", bold_prefix="FR7 (User Authentication): ")
    mr.add_bullet("Administrators must authenticate via isolated credentials to access executive controls.", bold_prefix="FR8 (Admin Portal): ")
    mr.add_bullet("Administrators must be able to create, edit, verify, and delete recycling centre records.", bold_prefix="FR9 (Centre Management): ")
    mr.add_bullet("Administrators must be able to ingest batch CPCB facility rosters via validated CSV file uploads.", bold_prefix="FR10 (CSV Ingestion): ")
    mr.add_bullet("The system must record user searches and logins into MySQL user_activity table for regional analytics.", bold_prefix="FR11 (Activity Tracking): ")
    mr.add_bullet("Administrators must be able to moderate user accounts (activate/deactivate access).", bold_prefix="FR12 (User Moderation): ")

    mr.add_sec_heading("3.4 Non-Functional Requirements")
    nfr_data = [
        ["Security", "Werkzeug scrypt password hashing, session cookies (HttpOnly, SameSite), CSRF defense, CSP headers."],
        ["Performance", "API response latency under 300 ms; indexed MySQL queries; thread-safe connection pooling (pool_size=25)."],
        ["Usability", "Responsive layout across mobile, tablet, and desktop devices; intuitive touch-friendly search controls."]
    ]
    mr.add_table_custom(["Requirement", "Specification & Architectural Benchmark"], nfr_data, [1.5, 4.8], "Table 3.1: Non-functional requirements (Part 1)")

    mr.add_page_footer_num("6")

# ==============================================================================
# PAGE 14: CHAPTER 3 continued (3.5 to 3.9)
# ==============================================================================
def build_p14():
    nfr_data2 = [
        ["Reliability", "MySQL InnoDB relational engine with foreign key cascades, transaction atomicity, and point-in-time JSON backups."],
        ["Maintainability", "Modular Python Flask blueprints (admin.py, app.py, db.py); centralized configuration in config.py."],
        ["Scalability", "Capable of sustaining 50 concurrent user sessions executing 200+ requests per second without memory degradation."]
    ]
    mr.add_table_custom(["Requirement", "Specification & Architectural Benchmark"], nfr_data2, [1.5, 4.8], "Table 3.1: Non-functional requirements (Part 2)")

    mr.add_sec_heading("3.5 Hardware Requirements")
    mr.add_para("Development environment requires a minimum of an Intel/AMD dual-core x86-64 processor, 4 GB RAM (8 GB recommended for concurrent testing), and 20 GB available storage. Production hosting operates on cloud virtual machines with 1 vCPU, 512 MB to 1 GB RAM, and persistent network storage.")

    mr.add_sec_heading("3.6 Software Requirements")
    mr.add_para("Operating system support includes Windows 10/11, Ubuntu 22.04 LTS, and macOS. The backend requires Python 3.10+ with Flask, Werkzeug, and mysql-connector-python. Frontend execution requires HTML5, CSS3, JavaScript (ES6+), Leaflet 1.9.4, and OpenStreetMap tile servers.")

    mr.add_sec_heading("3.7 Database Requirements")
    mr.add_para("MySQL 8.0 or MariaDB 10.4+ serves as the relational database engine. Primary entities include users, admins, centres, devices, rewards_history, and user_activity. Relational integrity is enforced using foreign key constraints and B-tree performance indexing.")

    mr.add_sec_heading("3.8 User Interface Requirements")
    mr.add_para("The UI must adhere to modern SaaS visual guidelines: consistent emerald and forest-green color palettes, accessible WCAG contrast standards, sticky navigation headers, responsive hamburger mobile drawers, and Leaflet interactive map containers with dynamic popup pins.")

    mr.add_sec_heading("3.9 Security Requirements")
    mr.add_para("Sensitive credentials must never be stored in plain text. Werkzeug cryptographic salting and hashing protect user passwords. Administrative routes must be strictly segregated using session decorators to eliminate unauthorized vertical privilege escalation.")

    mr.add_page_footer_num("7")

# ==============================================================================
# PAGE 15: CHAPTER 3 continued (3.9 cont, 3.10, 3.11)
# ==============================================================================
def build_p15():
    mr.add_sec_heading("3.9 Security Requirements (Continued)")
    mr.add_bullet("100% of database queries must utilize parameterized SQL binding (cursor.execute(sql, params)), eliminating SQL injection vulnerabilities.", bold_prefix="SQL Injection Defense: ")
    mr.add_bullet("Flask-WTF CSRF tokens validate state-changing POST requests across all forms and JSON endpoints.", bold_prefix="CSRF Protection: ")
    mr.add_bullet("Content-Security-Policy (CSP), X-Content-Type-Options: nosniff, and X-Frame-Options: SAMEORIGIN headers prevent XSS and clickjacking.", bold_prefix="HTTP Defense Headers: ")
    mr.add_bullet("User activity audit logs record search terms and regional filters anonymously, strictly omitting passwords, tokens, or GPS coordinates.", bold_prefix="Data Privacy Compliance: ")

    mr.add_sec_heading("3.10 System Constraints")
    mr.add_bullet("Geospatial proximity detection relies on client browser permission; users declining geolocation gracefully fall back to manual state/city filtering.", bold_prefix="Client Geolocation: ")
    mr.add_bullet("Free-tier OpenStreetMap tile servers impose acceptable usage policies, accommodated by local client tile caching.", bold_prefix="Map Tile Quotas: ")
    mr.add_bullet("Facility contact channels depend on official CPCB registry accuracy; unverified facilities provide fallback Google search discovery.", bold_prefix="Registry Verification: ")
    mr.add_bullet("The academic prototype operates on local XAMPP MySQL and local Flask server, with planned hosting configured for Render and cloud MySQL.", bold_prefix="Hosting Deployment: ")

    mr.add_sec_heading("3.11 Requirement Summary")
    mr.add_para("The requirement analysis confirms the technical and architectural feasibility of EcoLocate. By balancing rich geospatial discovery, environmental gamification, and robust administrative oversight with strict security protocols, the application provides a resilient digital framework for national electronic waste management.")

    mr.add_page_footer_num("8")

# ==============================================================================
# PAGE 16: CHAPTER 4: GAP IDENTIFICATION (4.1 to 4.5)
# ==============================================================================
def build_p16():
    mr.add_chapter_title("CHAPTER 4: GAP IDENTIFICATION")
    mr.add_sec_heading("4.1 Introduction")
    mr.add_para("Gap identification examines traditional and conventional mechanisms for electronic waste disposal and regulatory record management, identifying systemic bottlenecks, accessibility limitations, and security deficiencies that necessitate the development of EcoLocate.")

    mr.add_sec_heading("4.2 Existing System")
    mr.add_para("In the conventional framework, e-waste recyclers are cataloged in static PDF bulletins published intermittently by the CPCB and SPCBs. Ordinary citizens searching for recycling options must navigate government portals, download cumbersome multi-page tables, and cross-reference alphanumeric addresses without geographic context or verification of operational status.")

    mr.add_sec_heading("4.3 Problems in the Existing System")
    mr.add_bullet("Official PDF records lack search, dynamic filtering, or spatial distance calculations.", bold_prefix="Static Data Fragmentation: ")
    mr.add_bullet("Citizens have no automated mechanism to determine proximity or obtain navigational directions.", bold_prefix="Absence of Geospatial Mapping: ")
    mr.add_bullet("Listed phone numbers and domains are frequently obsolete, unverified, or broken.", bold_prefix="Outdated Contact Channels: ")
    mr.add_bullet("Consumers receive zero tangible incentives, encouraging disposal through uncertified kabadiwalas.", bold_prefix="Lack of Incentive Framework: ")
    mr.add_bullet("Municipal authorities have no digital oversight into citizen search volume or regional facility demand.", bold_prefix="No Administrative Intelligence: ")

    mr.add_sec_heading("4.4 Identified Gaps")
    mr.add_para("The critical gap is the absence of an accessible, interactive, and incentivized digital bridge between the consumer and the certified recycling facility, directly driving electronic waste into informal and hazardous channels.")

    mr.add_sec_heading("4.5 Proposed System")
    mr.add_para("EcoLocate resolves these deficiencies through an integrated web ecosystem: dynamic MySQL facility lookups, Leaflet.js interactive maps, Haversine proximity detection, audited contact links, an EcoRewards gamification engine, and a live administrative audit dashboard.")

    mr.add_page_footer_num("9")

# ==============================================================================
# PAGE 17: CHAPTER 4 continued (4.6 to 4.10)
# ==============================================================================
def build_p17():
    mr.add_sec_heading("4.6 Gap-Filling Approach")
    gap_data = [
        ["Static regulatory PDF rosters", "Centralized, searchable MySQL relational database with dynamic cascading filters."],
        ["No spatial proximity awareness", "Client Geolocation API integration with mathematical Haversine distance sorting."],
        ["Lack of interactive visual context", "Interactive Leaflet.js map with OpenStreetMap tiles and facility popup cards."],
        ["Outdated or broken contact links", "Verified official websites, direct phone links, and fallback Google search lookups."],
        ["No citizen motivation or incentives", "Gamified EcoRewards calculator estimating EcoPoints and CO2 emissions saved."],
        ["Zero administrative demand tracking", "Live User Activity Tracking portal recording search queries, states, and cities."]
    ]
    mr.add_table_custom(["Identified Gap in Traditional System", "EcoLocate Proposed Engineering Solution"], gap_data, [2.2, 4.1], "Table 4.1: How each gap is addressed")

    mr.add_sec_heading("4.7 Benefits of Bridging the Gaps")
    mr.add_para("Bridging these gaps delivers immediate benefits: it diverts hazardous heavy metals from landfills, empowers citizens with instant proximity discovery, improves operational capacity for formal dismantlers, and equips administrators with data-driven insights into regional recycling demand.")

    mr.add_sec_heading("4.8 Limitations of the Proposed Solution")
    mr.add_para("The application currently relies on user-initiated drop-offs at physical centres rather than automated courier pickups. In addition, coordinate plotting is verified for 20 primary hubs, while remaining regional facilities utilize automated city/state centroid fallbacks pending manual GPS auditing.")

    mr.add_sec_heading("4.9 Future Gap Reduction")
    mr.add_para("Future iterations will incorporate door-to-door courier dispatch APIs, direct integration with SPCB regulatory servers, and AI-powered computer vision models to identify e-waste hardware categories automatically from user photos.")

    mr.add_sec_heading("4.10 Existing System vs Proposed System")
    mr.add_para("Table 4.2 presents a comprehensive architectural comparison between traditional manual e-waste lookup methods and the EcoLocate digital platform.")

    mr.add_page_footer_num("10")

# ==============================================================================
# PAGE 18: CHAPTER 4 continued (Table 4.2 cont, 4.11)
# ==============================================================================
def build_p18():
    mr.add_sec_heading("4.10 Comparison: Existing vs. Proposed System (Continued)")
    comp_data = [
        ["Data Storage", "Static PDF bulletins & paper files", "Centralized, indexed MySQL database"],
        ["Search Capability", "Manual scanning of multi-page tables", "Instant dynamic state/city/keyword filtering"],
        ["Geospatial Discovery", "Completely unavailable", "Automated Haversine proximity & Leaflet map"],
        ["Contact Verification", "Unverified, often dead numbers", "Audited domains, verified emails & phone links"],
        ["Incentive Framework", "None (informal scrap sale only)", "Gamified EcoRewards calculator with history"],
        ["Administrative Control", "No digital management interface", "Full CRUD, CSV batch ingestion & dashboard"],
        ["Activity Analytics", "Zero tracking of public interest", "Real-time user search & activity tracking"],
        ["Security Architecture", "Unprotected public documents", "Werkzeug hashing, CSRF tokens & CSP headers"]
    ]
    mr.add_table_custom(["Evaluation Feature", "Traditional / Conventional Approach", "EcoLocate Proposed Platform"], comp_data, [1.4, 2.4, 2.5], "Table 4.2: Comparison of existing and proposed systems")

    mr.add_sec_heading("4.11 Chapter Summary")
    mr.add_para("This chapter systematically identified the limitations of traditional, static e-waste directories and established the targeted solutions provided by EcoLocate. By substituting static documents with a location-aware, verified, and secure web platform, EcoLocate provides an efficient and scalable technological response to India's electronic waste challenges.")

    mr.add_page_footer_num("11")

# ==============================================================================
# PAGE 19: CHAPTER 5: HARDWARE AND SOFTWARE REQUIREMENTS (5.1 to 5.3)
# ==============================================================================
def build_p19():
    mr.add_chapter_title("CHAPTER 5: HARDWARE AND SOFTWARE REQUIREMENTS")
    mr.add_sec_heading("5.1 Introduction")
    mr.add_para("This chapter details the technical specifications, development environment, programming libraries, database management engine, and client operating platforms required to build, execute, test, and host the EcoLocate web application.")

    mr.add_sec_heading("5.2 Hardware Requirements")
    mr.add_para("EcoLocate is designed to operate efficiently on standard commodity hardware during development while scaling seamlessly in cloud virtualized environments.")
    hw_data = [
        ["Processor (CPU)", "Dual-Core x86-64 (Intel Core i3 or AMD equivalent)", "Quad-Core or higher (Intel Core i5/i7/Ryzen)"],
        ["System Memory (RAM)", "4 GB RAM", "8 GB RAM (supports concurrent test harnesses)"],
        ["Storage Space", "10 GB available HDD/SSD storage", "50 GB NVMe SSD for fast query caching"],
        ["Display Resolution", "1280 x 720 HD display", "1920 x 1080 Full HD (responsive profiling)"],
        ["Network Interface", "Standard broadband connection (1 Mbps)", "High-speed broadband (10 Mbps+ for tile loading)"],
        ["Hosting VM Tier", "Render Free Tier (512 MB RAM, 0.5 CPU)", "Standard Production VM (1-2 GB RAM, 1 vCPU)"]
    ]
    mr.add_table_custom(["Hardware Component", "Minimum Required Specification", "Recommended Production Specification"], hw_data, [1.5, 2.4, 2.4], "Table 5.1: Hardware requirements")

    mr.add_sec_heading("5.3 Software Requirements")
    mr.add_para("The software runtime combines robust open-source technologies across operating system, web server, runtime language, and database layers.")
    sw_data = [
        ["Operating System", "Microsoft Windows 10/11, Ubuntu Linux 22.04 LTS, or macOS"],
        ["Backend Runtime", "Python 3.10, 3.11, or 3.12 (standard 64-bit CPython)"],
        ["Web Framework", "Flask 3.1.1 (WSGI micro-framework) with Werkzeug 3.1.3"],
        ["Database Server", "MySQL 8.0 or MariaDB 10.4+ (InnoDB engine on port 3307/3306)"],
        ["Database Pool Connector", "mysql-connector-python 26.7.0 (thread-safe connection pool)"]
    ]
    mr.add_table_custom(["Software Category", "Environment / Version Specification"], sw_data, [1.8, 4.5], "Table 5.2: Software environment (Part 1)")

    mr.add_page_footer_num("12")

# ==============================================================================
# PAGE 20: CHAPTER 5 continued (Table 5.2 cont, 5.4 to 5.7)
# ==============================================================================
def build_p20():
    sw_data2 = [
        ["Frontend UI Layer", "HTML5, CSS3, Vanilla ES6+ JavaScript (zero heavy JS dependencies)"],
        ["Mapping Engine", "Leaflet.js 1.9.4 with OpenStreetMap tile layer (zero-cost GIS)"],
        ["Security Middleware", "Flask-WTF 1.3.0 (CSRF protection) and Werkzeug Password Security"],
        ["Testing & Automation", "Python unittest, Playwright, Locust (load testing), and Multi-threader"]
    ]
    mr.add_table_custom(["Software Category", "Environment / Version Specification"], sw_data2, [1.8, 4.5], "Table 5.2: Software environment (Part 2)")

    mr.add_sec_heading("5.4 Programming Technologies")
    tech_data = [
        ["Python 3.13", "Core backend logic, Haversine geospatial calculations, and routing."],
        ["Flask Framework", "RESTful routing, Jinja2 template rendering, session management."],
        ["MySQL Database", "Persistent storage for facilities, users, devices, activity audit logs."],
        ["Leaflet.js & OSM", "Client-side interactive map rendering, marker plotting, and popups."],
        ["HTML5 & CSS3", "Semantic document structure, Emerald/Forest SaaS responsive styling."],
        ["Vanilla JavaScript", "Asynchronous fetch() calls, geolocation queries, dynamic dropdowns."]
    ]
    mr.add_table_custom(["Technology", "Role & Engineering Responsibility within EcoLocate"], tech_data, [1.6, 4.7], "Table 5.3: Programming technologies and their roles")

    mr.add_sec_heading("5.5 Database Management System")
    mr.add_para("MySQL (ewaste_db) is configured with the InnoDB storage engine, ensuring ACID compliance, foreign key cascade enforcement, and thread-safe connection pooling to handle concurrent database operations without deadlock.")

    mr.add_sec_heading("5.6 Web Server and Development Tools")
    mr.add_para("Local development utilizes Flask's internal WSGI server with XAMPP MariaDB on port 3307. Production deployment utilizes Gunicorn WSGI workers behind WhiteNoise static asset serving, configured via Procfile and render.yaml.")

    mr.add_sec_heading("5.7 Browser and Operating System")
    mr.add_para("The web portal is engineered to run seamlessly on Google Chrome, Mozilla Firefox, Microsoft Edge, and Apple Safari across Windows, Android, iOS, and Linux platforms.")

    mr.add_page_footer_num("13")

print('Compiled Pages 8 to 20.')
