"""
Script to generate the complete 21-slide external viva PowerPoint presentation
for Yogesh (241306039), BCA AI & ML (Section 5A) on EcoLocate - E-Waste Facility Locator.
Outputs:
- EcoLocate_External_Viva_Presentation_Yogesh_241306039.pptx
- EcoLocate_External_Viva_Presentation_Yogesh_241306039.pdf (via PowerPoint COM automation)
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# Color Palette
DARK_GREEN = RGBColor(14, 59, 46)      # #0E3B2E
DARK_EMERALD = RGBColor(6, 78, 59)     # #064E3B
EMERALD = RGBColor(16, 185, 129)       # #10B981
LIGHT_MINT = RGBColor(236, 253, 245)   # #ECFDF5
ACCENT_MINT = RGBColor(52, 211, 153)   # #34D399
BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC
TEXT_DARK = RGBColor(15, 23, 42)       # #0F172A
TEXT_MUTED = RGBColor(71, 85, 105)     # #475569
CARD_BG = RGBColor(255, 255, 255)      # #FFFFFF
CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
GOLD = RGBColor(217, 119, 6)           # #D97706
WHITE = RGBColor(255, 255, 255)

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'report_assets'))

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    def add_header(slide, title_text, category_text, slide_num, dark=False):
        """Standardized presentation slide header."""
        # Top banner background accent
        top_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12)
        )
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = EMERALD
        top_bar.line.color.rgb = EMERALD

        # Header background
        header_bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.12), Inches(13.333), Inches(1.05)
        )
        header_bg.fill.solid()
        header_bg.fill.fore_color.rgb = DARK_GREEN if not dark else DARK_EMERALD
        header_bg.line.color.rgb = DARK_GREEN if not dark else DARK_EMERALD

        # Category pill
        pill = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.24), Inches(3.2), Inches(0.3)
        )
        pill.fill.solid()
        pill.fill.fore_color.rgb = EMERALD
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Title text
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(10.5), Inches(0.55))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = WHITE

        # Slide Number Badge
        num_box = slide.shapes.add_textbox(Inches(11.8), Inches(0.35), Inches(1.0), Inches(0.4))
        tf = num_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"{slide_num:02d} / 21"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_MINT
        p.alignment = PP_ALIGN.RIGHT

        # Footer
        footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.3))
        tf = footer.text_frame
        p = tf.paragraphs[0]
        p.text = "EcoLocate: E-Waste Facility Locator | External Viva | Yogesh (241306039) | BCA AIML 5A"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title="", bg_color=CARD_BG, border_color=CARD_BORDER):
        """Card shape for content framing."""
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
            p = tb.text_frame.paragraphs[0]
            p.text = title
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = DARK_GREEN
        return card

    # ==========================================
    # SLIDE 1: TITLE & CANDIDATE DETAILS
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    # Background full emerald gradient effect
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_GREEN
    bg1.line.fill.background()

    # Decorative accent bars
    bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.2))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = EMERALD
    bar1.line.fill.background()

    # Academic presentation badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.7), Inches(4.5), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = DARK_EMERALD
    badge.line.color.rgb = EMERALD
    badge.line.width = Pt(1.5)
    p = badge.text_frame.paragraphs[0]
    p.text = "MAJOR PROJECT EXTERNAL VIVA VOCE (2026-27)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_MINT
    p.alignment = PP_ALIGN.CENTER

    # Main Project Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.3), Inches(1.6))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EcoLocate – E-Waste Facility Locator"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p2 = tf.add_paragraph()
    p2.text = "A Centralized Geospatial Web Application for Responsible Electronic Waste Management & Campus Recycling"
    p2.font.size = Pt(18)
    p2.font.color.rgb = ACCENT_MINT

    # Two prominent cards: Left = Candidate Details, Right = Technical & Academic Profile
    card_cand = add_card(s1, Inches(1.0), Inches(3.2), Inches(5.4), Inches(3.7), "Student Identification", bg_color=CARD_BG)
    tb = s1.shapes.add_textbox(Inches(1.2), Inches(3.8), Inches(5.0), Inches(2.9))
    tf = tb.text_frame
    tf.word_wrap = True

    cand_info = [
        ("Candidate Name:", "Yogesh"),
        ("Roll Number:", "241306039"),
        ("Course / Degree:", "Bachelor of Computer Applications (BCA)"),
        ("Specialization:", "Artificial Intelligence & Machine Learning"),
        ("Academic Semester:", "5th Semester | Section 5A"),
        ("University:", "SGT University, Gurugram, Haryana"),
        ("Assessment Type:", "External Project Viva & Practical Evaluation")
    ]
    for i, (label, val) in enumerate(cand_info):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{label} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = val
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK

    card_proj = add_card(s1, Inches(6.8), Inches(3.2), Inches(5.5), Inches(3.7), "Project Metadata & Technology", bg_color=CARD_BG)
    tb2 = s1.shapes.add_textbox(Inches(7.0), Inches(3.8), Inches(5.1), Inches(2.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    proj_meta = [
        ("Project Title:", "EcoLocate: E-Waste Facility Locator"),
        ("Project Domain:", "Environmental Sustainability & Clean-Tech"),
        ("Project Nature:", "Web-Based Client-Server Geospatial System"),
        ("Primary Stack:", "Python 3.13, Flask 3.x, MySQL, Leaflet.js"),
        ("Core Algorithm:", "Haversine Geodesic Distance Matrix"),
        ("Security Standard:", "Werkzeug SHA-256, CSRF Tokens, Zero-Leakage"),
        ("Validation Status:", "88/88 Automated Unit Tests Passing (100% OK)")
    ]
    for i, (label, val) in enumerate(proj_meta):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = f"{label} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = val
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 2: PROJECT OVERVIEW
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Project Executive Overview", "1. Executive Summary", 2)

    # 3 Strategic Overview Cards
    card1 = add_card(s2, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.4), "What is EcoLocate?", bg_color=CARD_BG)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(3.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    pts1 = [
        "A full-stack, location-aware web platform designed to streamline electronic waste disposal.",
        "Aggregates government-authorized Central Pollution Control Board (CPCB) recycling facilities across India.",
        "Provides dynamic geospatial filtering, live mapping, and intelligent shortest-path routing.",
        "Eliminates reliance on unauthorized informal dismantlers who cause severe environmental harm."
    ]
    for i, pt in enumerate(pts1):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(12)

    card2 = add_card(s2, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.4), "Target Audience & Users", bg_color=CARD_BG)
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(2.1), Inches(3.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    pts2 = [
        "University Students & Faculty: Specific SGT University campus pickup workflows and credit tracking.",
        "General Citizens & Households: Simple discovery of authorized recyclers for home electronics.",
        "IT Enterprises & SMEs: Safe bulk disposal of outdated servers, laptops, and networking hardware.",
        "Regulatory Administrators: Central monitoring of recycling submissions and facility inventories."
    ]
    for i, pt in enumerate(pts2):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(12)

    card3 = add_card(s2, Inches(8.8), Inches(1.5), Inches(3.7), Inches(5.4), "Key Value Proposition", bg_color=LIGHT_MINT, border_color=EMERALD)
    tb = s2.shapes.add_textbox(Inches(9.0), Inches(2.1), Inches(3.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    pts3 = [
        "Verified Database: Replaces fragmented PDF lists with a clean, structured relational directory.",
        "Real-Time Proximity: Pinpoints the nearest authorized drop-off center in under 1 second.",
        "Incentivized Recycling: Gamified repeat points system credits users for responsible disposal.",
        "Automated Notifications: Dual-category SMTP notifications with verified tracking IDs."
    ]
    for i, pt in enumerate(pts3):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"✔ {pt}"
        p.font.size = Pt(13)
        p.font.bold = (i == 0 or i == 2)
        p.font.color.rgb = DARK_GREEN
        p.space_after = Pt(12)

    # ==========================================
    # SLIDE 3: INTRODUCTION TO E-WASTE
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Understanding Electronic Waste (E-Waste)", "2. Domain Background", 3)

    # Top highlight banner
    top_box = add_card(s3, Inches(0.8), Inches(1.4), Inches(11.733), Inches(1.1), "", bg_color=LIGHT_MINT, border_color=EMERALD)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Electronic Waste (E-Waste) encompasses all discarded electrical or electronic equipment (EEE), including functional, broken, or obsolete devices. India ranks as the world's 3rd largest e-waste generator (3.2+ million metric tonnes annually), yet over 90% is handled by unregulated informal scrapyards."
    p.font.size = Pt(13.5)
    p.font.color.rgb = DARK_GREEN

    # 3 Category cards
    c1 = add_card(s3, Inches(0.8), Inches(2.7), Inches(3.6), Inches(4.2), "Common Consumer E-Waste")
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(3.3), Inches(3.2), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    items1 = [
        "Smartphones, Tablets & Feature Phones",
        "Laptops, Desktops, Keyboards & Mice",
        "Lithium-ion Batteries & Power Banks",
        "Power Adapters, Charging Cables & Hubs",
        "Televisions, CRT Monitors & Displays",
        "Printers, Scanners & Toners"
    ]
    for i, itm in enumerate(items1):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"📱 {itm}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    c2 = add_card(s3, Inches(4.8), Inches(2.7), Inches(3.6), Inches(4.2), "The 'Big Three' Toxic Metals")
    tb = s3.shapes.add_textbox(Inches(5.0), Inches(3.3), Inches(3.2), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    items2 = [
        "Lead (Pb): Found in solder & CRT glass; damages nervous, renal & reproductive systems.",
        "Mercury (Hg): Present in flat-screen backlights & switches; bioaccumulates in aquatic food chains.",
        "Cadmium (Cd): Found in rechargeable Ni-Cd batteries; causes bone brittleness & kidney toxicity.",
        "Brominated Flame Retardants: Releases toxic dioxins upon open combustion."
    ]
    for i, itm in enumerate(items2):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"☣ {itm}"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    c3 = add_card(s3, Inches(8.8), Inches(2.7), Inches(3.7), Inches(4.2), "The Value of Recovery")
    tb = s3.shapes.add_textbox(Inches(9.0), Inches(3.3), Inches(3.3), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    items3 = [
        "Precious Metals: 1 tonne of recycled mobile phones contains up to 300g of pure Gold and 2kg of Silver.",
        "Base Metals: High-grade Copper, Aluminum, and Iron recovered without mining virgin ores.",
        "Circular Economy: Conserves energy, reduces raw material extraction carbon footprints by 80%.",
        "CPCB Mandate: Compliance with E-Waste Management Rules 2022 & EPR targets."
    ]
    for i, itm in enumerate(items3):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"♻ {itm}"
        p.font.size = Pt(11.5)
        p.font.color.rgb = DARK_GREEN
        p.space_after = Pt(6)

    # ==========================================
    # SLIDE 4: PROBLEM STATEMENT
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Problem Statement: The E-Waste Crisis", "3. Problem Definition", 4)

    probs = [
        ("Information Asymmetry & Fragmentation",
         "Government-authorized recyclers are published in static, hard-to-navigate CPCB PDF directories. Citizens cannot readily locate facilities serving their city or state."),
        ("Absence of Geospatial Proximity Tools",
         "Existing portals lack geolocation, interactive mapping, and shortest-path calculation, leaving consumers unsure of where to physically deposit defunct electronics."),
        ("Domination of Informal Scrap Markets",
         "Over 90% of discarded electronics are channeled to informal dismantlers utilizing acid baths, open-air wire burning, and unlined municipal dumping, polluting aquifers."),
        ("Lack of Recycling Incentive & Feedback",
         "Citizens receive no tangible reinforcement, tracking status, or academic recognition for recycling e-waste, resulting in prolonged household hoarding."),
        ("Non-Transparent Verification Workflows",
         "Waste collection lacks centralized tracking, leaving consumers without proof of disposal and administrators without real-time inventory oversight.")
    ]

    for idx, (title, desc) in enumerate(probs):
        top_pos = Inches(1.4 + idx * 1.1)
        add_card(s4, Inches(0.8), top_pos, Inches(11.733), Inches(0.95), bg_color=CARD_BG)
        # Left tag icon
        tag = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_pos, Inches(0.25), Inches(0.95))
        tag.fill.solid()
        tag.fill.fore_color.rgb = GOLD if idx % 2 == 1 else DARK_GREEN
        tag.line.fill.background()

        tb = s4.shapes.add_textbox(Inches(1.2), top_pos + Inches(0.08), Inches(11.1), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"0{idx+1}. {title}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 5: MOTIVATION BEHIND THE PROJECT
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Project Motivation & Rationale", "4. Project Motivation", 5)

    mots = [
        ("Institutional Sustainability at SGT University",
         "Aligning with SGT University's green campus charter and Environmental Cell guidelines to divert campus electronics from landfills through organized student collection drives."),
        ("UN Sustainable Development Goals (SDGs)",
         "Directly addresses SDG 11 (Sustainable Cities and Communities) and SDG 12 (Responsible Consumption and Production) through circular electronic material recovery."),
        ("Bridging Technology & Environmental Science",
         "Applying Computer Applications & AI/ML principles (spatial algorithms, database normalization, asynchronous notifications) to solve urgent real-world ecological challenges."),
        ("Gamified Public Participation",
         "Motivating repeat submissions by replacing apathy with transparent point rewards, tracking codes, and digital certificates of contribution.")
    ]

    for idx, (title, desc) in enumerate(mots):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.5 if idx < 2 else 4.2)
        card = add_card(s5, left_pos, top_pos, Inches(5.7), Inches(2.5), title, bg_color=LIGHT_MINT if idx == 0 else CARD_BG, border_color=EMERALD if idx == 0 else CARD_BORDER)

        tb = s5.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.65), Inches(5.3), Inches(1.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 6: PROJECT OBJECTIVES
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Core Project Objectives", "5. Project Objectives", 6)

    objs = [
        ("Centralized Authorized Facility Repository",
         "Digitize and normalize CPCB-certified recycling facilities into a query-optimized MySQL database with state, city, and accepted-device indexing."),
        ("Intelligent Geospatial Discovery",
         "Implement browser-based GPS reverse geocoding and the Haversine formula to compute geodesic distances and rank facilities by physical proximity."),
        ("Interactive Cartographic Visualization",
         "Integrate Leaflet.js and OpenStreetMap to plot facility clusters, display interactive popup metadata, and offer instant Google Maps turn-by-turn routing."),
        ("Multi-Tier E-Waste Submission Portal",
         "Provide a streamlined, responsive form catering to both SGT University students and general citizens with multi-item logging and image upload verification."),
        ("Repeat Submission Points System",
         "Establish a transparent points engine that evaluates eligible e-waste items per submission and maintains user wallet ledgers without physical inventory overhead."),
        ("Administrative Oversight & Email Management",
         "Equip university administrators with real-time audit tools, CSV bulk ingestion, request confirmation triggers, and template-based Gmail SMTP dispatches.")
    ]

    for idx, (title, desc) in enumerate(objs):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.4 + (idx // 2) * 1.8)
        add_card(s6, left_pos, top_pos, Inches(5.7), Inches(1.65), f"Target 0{idx+1}: {title}")
        tb = s6.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.3), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 7: EXISTING VS PROPOSED SYSTEM
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Comparative Analysis: Existing vs. Proposed System", "6. Comparative Analysis", 7)

    # Professional comparison table
    table_shape = s7.shapes.add_table(7, 3, Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.4))
    table = table_shape.table
    table.columns[0].width = Inches(2.8)
    table.columns[1].width = Inches(4.4)
    table.columns[2].width = Inches(4.533)

    headers = ["Evaluation Criteria", "Existing Traditional System", "Proposed EcoLocate Platform"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_GREEN
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    rows_data = [
        ("Facility Search & Discovery", "Static, unsearchable CPCB PDF tables across dozens of portals.", "Dynamic SQL filtering by State, City, Category & Keyword in real time."),
        ("Geospatial & Map Capabilities", "None; user must manually copy addresses into third-party maps.", "Interactive Leaflet.js map with GPS proximity ranking via Haversine formula."),
        ("Distance Computation", "Completely absent; manual guesswork required by citizens.", "Automatic calculation of geodesic distances in kilometers with nearby radius."),
        ("E-Waste Submission Flow", "Manual phone calls or walk-ins with no digital tracking.", "Structured multi-item submission portal generating unique tracking codes."),
        ("Incentives & Points Engine", "No gamification or reward mechanisms to encourage recycling.", "Dynamic points ledger crediting users per verified submission."),
        ("Notification & Verification", "No feedback loop; high uncertainty of responsible handling.", "Automated Gmail SMTP emails with dual SGT student / General user routing.")
    ]

    for i, (crit, exist, prop) in enumerate(rows_data):
        row_idx = i + 1
        c0 = table.cell(row_idx, 0)
        c0.text = crit
        c0.text_frame.paragraphs[0].font.bold = True
        c0.text_frame.paragraphs[0].font.size = Pt(11.5)
        c0.text_frame.paragraphs[0].font.color.rgb = DARK_GREEN
        c0.fill.solid()
        c0.fill.fore_color.rgb = LIGHT_MINT if i % 2 == 0 else WHITE

        c1 = table.cell(row_idx, 1)
        c1.text = exist
        c1.text_frame.paragraphs[0].font.size = Pt(11)
        c1.text_frame.paragraphs[0].font.color.rgb = TEXT_DARK
        c1.fill.solid()
        c1.fill.fore_color.rgb = WHITE if i % 2 == 0 else BG_LIGHT

        c2 = table.cell(row_idx, 2)
        c2.text = prop
        c2.text_frame.paragraphs[0].font.size = Pt(11)
        c2.text_frame.paragraphs[0].font.bold = True
        c2.text_frame.paragraphs[0].font.color.rgb = DARK_EMERALD
        c2.fill.solid()
        c2.fill.fore_color.rgb = LIGHT_MINT if i % 2 == 0 else WHITE

    # ==========================================
    # SLIDE 8: PROPOSED SOLUTION & WORKFLOW
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Proposed Solution & High-Level Flow", "7. Solution Architecture", 8)

    flow_steps = [
        ("1. User Access", "User visits EcoLocate via desktop/mobile browser; grants GPS permission or selects state/city."),
        ("2. Geodesic Search", "Flask backend executes Haversine calculation against normalized MySQL facility coordinates."),
        ("3. Visual Output", "Leaflet.js dynamically renders facility markers, contact details, and Google Maps directions link."),
        ("4. Submission Form", "User submits defunct items (Mobile, Laptop, Battery) with pickup address & images."),
        ("5. Email Dispatch", "Automated SMTP triggers a 'Submission Received' confirmation email with tracking ID."),
        ("6. Admin Audit", "Administrator confirms request, verifies item count, credits points wallet, and triggers confirmation email.")
    ]

    for i, (step_title, step_desc) in enumerate(flow_steps):
        top_pos = Inches(1.4 + i * 0.95)
        card = add_card(s8, Inches(0.8), top_pos, Inches(11.733), Inches(0.85), bg_color=CARD_BG)

        # Step indicator badge
        badge = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), top_pos + Inches(0.15), Inches(2.2), Inches(0.55))
        badge.fill.solid()
        badge.fill.fore_color.rgb = DARK_GREEN if i < 3 else EMERALD
        badge.line.fill.background()
        p = badge.text_frame.paragraphs[0]
        p.text = step_title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s8.shapes.add_textbox(Inches(3.4), top_pos + Inches(0.12), Inches(8.9), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = step_desc
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 9: KEY FEATURES
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Key Features of EcoLocate", "8. Functional Features", 9)

    features = [
        ("Geospatial Facility Discovery",
         "Search authorized dismantlers across 35+ States & Union Territories; filter by city, facility type, or accepted electronic category."),
        ("Interactive Leaflet Cartography",
         "Interactive mapping with dynamic marker clustering, custom icons, facility popups, and direct Google Maps navigation coordinates."),
        ("Shortest-Path Nearest Centre Algorithm",
         "Real-time mathematical distance sorting ordering centres from closest to furthest based on live browser GPS or manual location inputs."),
        ("E-Waste Submission & Pickup Portal",
         "Dual-path submission architecture distinguishing SGT University campus residences from general citizens with image upload validation."),
        ("Modular Repeat Points Engine",
         "Dynamic calculation awarding points per verified device unit; maintains persistent transaction history and user wallet balances."),
        ("Executive Admin Management Suite",
         "Full CRUD for centres/devices, CSV bulk ingestion, real-time user activity logs, and template-based Gmail SMTP notification manager.")
    ]

    for idx, (title, desc) in enumerate(features):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.4 + (idx // 2) * 1.85)
        add_card(s9, left_pos, top_pos, Inches(5.7), Inches(1.7), f"★ {title}")
        tb = s9.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.3), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 10: TECHNOLOGY STACK
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Comprehensive Technology Stack", "9. Technical Specifications", 10)

    tech_categories = [
        ("Frontend Presentation Layer", [
            ("HTML5 & Jinja2 Templates:", "Semantic markup with server-side block inheritance."),
            ("CSS3 & Custom Stylesheet:", "Responsive modern emerald theme, card components, flexbox & grid."),
            ("JavaScript (ES6+):", "Asynchronous fetch API calls, DOM manipulation, coordinate parsing."),
            ("Leaflet.js 1.9.4:", "Open-source mobile-friendly interactive mapping library."),
            ("OpenStreetMap Carto:", "Tile layers for live street-level and regional navigation.")
        ]),
        ("Backend & Business Logic Layer", [
            ("Python 3.13:", "Core object-oriented backend programming language."),
            ("Flask 3.x Microframework:", "Lightweight WSGI web application framework & RESTful routing."),
            ("Werkzeug Security:", "PBKDF2/SHA-256 cryptographic password hashing."),
            ("Flask-WTF & CSRFProtect:", "Synchronizer token pattern against cross-site request forgery."),
            ("python-dotenv:", "Secure runtime environment variable isolation.")
        ]),
        ("Database & Persistence Layer", [
            ("MySQL / MariaDB 10.4:", "Relational database management system with ACID guarantees."),
            ("mysql-connector-python:", "Official Oracle driver with thread-safe connection pooling."),
            ("Normalized 3NF Schema:", "17 tables with foreign key constraints, indexes, and cascades."),
            ("UTF8MB4 Character Set:", "Full support for multilingual text and symbol storage.")
        ]),
        ("Protocols, APIs & Developer Tools", [
            ("Haversine Distance Engine:", "Spherical trigonometric geodesic distance calculator."),
            ("Gmail SMTP over TLS:", "Port 587 authenticated MIME email notification dispatch."),
            ("Git & GitHub Repository:", "Version control with clean branch tracking & zero secret leakage."),
            ("XAMPP & MariaDB:", "Local development server stack running on dedicated port 3307.")
        ])
    ]

    for idx, (cat_title, items) in enumerate(tech_categories):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.4 if idx < 2 else 4.2)
        card = add_card(s10, left_pos, top_pos, Inches(5.7), Inches(2.6), cat_title)
        tb = s10.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.3), Inches(1.95))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, (label, val) in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"• {label} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = DARK_GREEN
            run = p.add_run()
            run.text = val
            run.font.bold = False
            run.font.color.rgb = TEXT_DARK
            p.space_after = Pt(2)

    # ==========================================
    # SLIDE 11: SYSTEM ARCHITECTURE
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Three-Tier System Architecture", "10. System Architecture", 11)

    arch_img_path = os.path.join(ASSETS_DIR, 'diagrams', 'fig_9_1_architecture.png')
    if os.path.exists(arch_img_path):
        s11.shapes.add_picture(arch_img_path, Inches(0.8), Inches(1.5), width=Inches(6.4))
    else:
        add_card(s11, Inches(0.8), Inches(1.5), Inches(6.4), Inches(5.2), "Architecture Diagram")

    # Right side explanation card
    right_card = add_card(s11, Inches(7.4), Inches(1.5), Inches(5.1), Inches(5.4), "Architectural Breakdown", bg_color=CARD_BG)
    tb = s11.shapes.add_textbox(Inches(7.6), Inches(2.1), Inches(4.7), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    arch_pts = [
        ("Tier 1: Client Presentation Layer",
         "Delivers responsive web views rendered via Jinja2 templates, Leaflet cartography, and asynchronous JavaScript AJAX requests."),
        ("Tier 2: Application / Controller Layer",
         "Powered by Flask; encapsulates authentication filters (@login_required, @admin_required), CSRF protection, Haversine geospatial logic, and MIME email dispatch."),
        ("Tier 3: Database & Persistence Layer",
         "MySQL database managed via thread-safe MySQLConnectionPool (5–32 active sessions) ensuring 100% SQL injection prevention with parameterized queries."),
        ("External Service Integration",
         "Connects seamlessly with OpenStreetMap Tile Servers for vector map tiles and Google SMTP TLS servers for automated notification delivery.")
    ]
    for i, (title, desc) in enumerate(arch_pts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{title}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GREEN
        p.space_after = Pt(2)
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # ==========================================
    # SLIDE 12: APPLICATION WORKFLOW
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "System Execution Flowchart", "11. Process Workflow", 12)

    flow_img_path = os.path.join(ASSETS_DIR, 'diagrams', 'fig_9_6_flowchart.png')
    if os.path.exists(flow_img_path):
        s12.shapes.add_picture(flow_img_path, Inches(0.8), Inches(1.5), width=Inches(6.4))
    else:
        add_card(s12, Inches(0.8), Inches(1.5), Inches(6.4), Inches(5.2), "Workflow Diagram")

    right_card = add_card(s12, Inches(7.4), Inches(1.5), Inches(5.1), Inches(5.4), "Workflow Execution Logic", bg_color=CARD_BG)
    tb = s12.shapes.add_textbox(Inches(7.6), Inches(2.1), Inches(4.7), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    wf_pts = [
        ("1. Discovery & Selection:", "User initiates search by state, city, or current coordinates. System computes nearest facility matrix and renders interactive pins."),
        ("2. Submission Creation:", "User enters waste details (device category, quantity, working condition) and optional image proof."),
        ("3. Submission ID Generation:", "System generates formatted alphanumeric tracking ID (e.g. SUB-2026-XXXXX) and stores records in 3NF MySQL tables."),
        ("4. Notification Dispatch:", "Automated trigger formats HTML email using active template and transmits via Gmail SMTP without blocking user UI."),
        ("5. Administrative Review:", "Admin inspects request on dashboard, confirms or modifies accepted quantities, and awards points to user's wallet ledger.")
    ]
    for i, (title, desc) in enumerate(wf_pts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(10)

    # ==========================================
    # SLIDE 13: LOCATION-BASED FUNCTIONALITY
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Location-Based Proximity & Haversine Formula", "12. Spatial Algorithms", 13)

    c1 = add_card(s13, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4), "The Haversine Mathematical Model")
    tb = s13.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    pts_hav = [
        ("Why Flat Euclidean Distance Fails:", "The Earth is an oblate spheroid. Planar Pythagorean calculations produce massive distortion over real-world distances."),
        ("Haversine Spherical Formulation:", "Computes great-circle distance between two coordinate pairs (lat1, lon1) and (lat2, lon2) across Earth's sphere."),
        ("Mathematical Formula:", "a = sin²(Δφ/2) + cos(φ1) · cos(φ2) · sin²(Δλ/2)\nc = 2 · atan2(√a, √(1−a))\nd = R · c"),
        ("Radius Constant:", "Mean volumetric Earth radius R = 6,371.0 kilometers."),
        ("Trigonometric Radians Conversion:", "All latitude and longitude angles are converted from degrees to radians using math.radians().")
    ]
    for i, (title, desc) in enumerate(pts_hav):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    c2 = add_card(s13, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), "Implementation in EcoLocate Backend")
    tb = s13.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    pts_impl = [
        ("Python Function in app.py:", "def calculate_haversine_distance(lat1, lon1, lat2, lon2)\nReturns distance in kilometers rounded to two decimal places."),
        ("Database Pre-Filtering:", "Bounding box constraints (latitude ± radius, longitude ± radius) prune candidates before detailed trigonometric evaluation, ensuring sub-50ms query times."),
        ("Centres Ordering:", "Matching centres with valid coordinates are sorted in ascending order of calculated distance: min(distance)."),
        ("Browser Geolocation Integration:", "HTML5 navigator.geolocation.getCurrentPosition() passes live coordinates via asynchronous POST /api/centres/nearby."),
        ("Fallback Handling:", "Facilities without geo-coordinates remain 100% searchable via state and city dropdowns, ensuring no data loss.")
    ]
    for i, (title, desc) in enumerate(pts_impl):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"✔ {title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # ==========================================
    # SLIDE 14: DATABASE DESIGN
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Relational Database Schema (MySQL)", "13. Database Architecture", 14)

    er_img_path = os.path.join(ASSETS_DIR, 'diagrams', 'fig_9_5_er_diagram.png')
    if os.path.exists(er_img_path):
        s14.shapes.add_picture(er_img_path, Inches(0.8), Inches(1.5), width=Inches(6.4))
    else:
        add_card(s14, Inches(0.8), Inches(1.5), Inches(6.4), Inches(5.2), "ER Diagram")

    right_card = add_card(s14, Inches(7.4), Inches(1.5), Inches(5.1), Inches(5.4), "Core Database Entities (17 Tables)", bg_color=CARD_BG)
    tb = s14.shapes.add_textbox(Inches(7.6), Inches(2.1), Inches(4.7), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    db_entities = [
        ("centres & devices:", "Stores authorized recycler names, addresses, contacts, coordinates, and supported electronic categories."),
        ("users & admins:", "Stores credentials with Werkzeug SHA-256 hashes, roles, activation flags, and session timestamps."),
        ("ewaste_submissions & items:", "Records multi-item collection requests, roll numbers, student flags, item quantities, and verification status."),
        ("user_points_wallets & transactions:", "Maintains user balances with immutable double-entry style ledger tracking points earned per submission."),
        ("email_templates & email_logs:", "Stores customizable SGT vs General email templates and dispatches with status (Sent, Failed, Pending)."),
        ("user_activity:", "Comprehensive audit log recording logins, searches, and device queries for administrative intelligence.")
    ]
    for i, (title, desc) in enumerate(db_entities):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {title} "
        p.font.bold = True
        p.font.size = Pt(11.5)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # ==========================================
    # SLIDE 15: USER INTERFACE WALKTHROUGH
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "User Interface & Experience", "14. UI Showcase", 15)

    # 4 UI screenshot cards
    screens = [
        ("Homepage & Search Hero", "fig_b1_home.png", "Clean sustainability hero section with quick location jump, value stats & awareness cards."),
        ("Interactive Map & Facility List", "fig_b4_centres_search.png", "Leaflet.js interactive pins, distance badges, contact numbers & Google Maps direction links."),
        ("Rewards Calculator & Points", "fig_b6_rewards.png", "Dynamic device selector calculating potential reward points with persistence history."),
        ("Admin Executive Dashboard", "fig_b8_admin_dashboard.png", "Real-time KPI metrics, submission review queue, user activity logs & template controls.")
    ]

    for idx, (title, img_name, desc) in enumerate(screens):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.5 if idx < 2 else 4.3)
        add_card(s15, left_pos, top_pos, Inches(5.7), Inches(2.6), title)

        img_path = os.path.join(ASSETS_DIR, 'screenshots', img_name)
        if os.path.exists(img_path):
            s15.shapes.add_picture(img_path, left_pos + Inches(0.2), top_pos + Inches(0.5), width=Inches(2.6))
        
        tb = s15.shapes.add_textbox(left_pos + Inches(2.9), top_pos + Inches(0.55), Inches(2.6), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 16: IMPORTANT MODULES
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Core Software Modules Breakdown", "15. Modular Architecture", 16)

    mods = [
        ("1. Authentication & Security (app.py)",
         "Werkzeug password hashing, session lifecycle management, @login_required & @admin_required boundary guards, and CSRF token verification across all forms."),
        ("2. Geospatial Facility Search (app.py)",
         "Executes dynamic SQL queries with multi-criteria filters (State, City, Device Category, Proximity). Implements Haversine distance engine."),
        ("3. Submissions & Collection (submissions.py)",
         "Handles public e-waste submission form with multipart image uploads, student validation, and tracking ID generation."),
        ("4. Repeat Points Engine (submissions.py)",
         "Evaluates accepted device counts per submission against configurable points tiers, managing user wallet ledgers and points audit history."),
        ("5. Email Management Service (email_service.py)",
         "Dynamic placeholder substitution (11 variables), mobile-responsive HTML builder, Gmail SMTP TLS dispatch, and retry dispatcher."),
        ("6. Administrative Portal (admin.py)",
         "Executive statistics, full CPCB centre CRUD, CSV batch ingestion, user activation toggling, and email template customization.")
    ]

    for idx, (title, desc) in enumerate(mods):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.4 + (idx // 2) * 1.85)
        add_card(s16, left_pos, top_pos, Inches(5.7), Inches(1.7), title)
        tb = s16.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.3), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 17: TESTING AND TEST CASES
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    add_header(s17, "Quality Assurance & Test Suite (88/88 Passing)", "16. Verification & Testing", 17)

    # Test Results Banner
    top_box = add_card(s17, Inches(0.8), Inches(1.4), Inches(11.733), Inches(1.0), "", bg_color=LIGHT_MINT, border_color=EMERALD)
    tb = s17.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(11.3), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Automated Test Suite Status: 88 of 88 Tests Passed (100% Passing in 4.436s via test_app.py)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p2 = tf.add_paragraph()
    p2.text = "Unit and integration tests validate database connectivity, authentication isolation, spatial algorithms, points ledger integrity, and zero-leakage security."
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_DARK

    # Test Table
    table_shape = s17.shapes.add_table(6, 4, Inches(0.8), Inches(2.6), Inches(11.733), Inches(4.3))
    table = table_shape.table
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(4.2)
    table.columns[2].width = Inches(3.8)
    table.columns[3].width = Inches(1.233)

    t_headers = ["Test Module", "Test Scenario / Input", "Expected Verification Result", "Status"]
    for j, h in enumerate(t_headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_GREEN
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    test_rows = [
        ("Authentication & Access", "Unauthenticated user accesses /admin/dashboard or /admin/centres", "HTTP 302 redirect to /admin/login with session rejection", "PASSED"),
        ("Haversine Distance", "Compute distance between Delhi (28.61, 77.20) and Visakhapatnam (17.68, 83.21)", "Distance matches spherical great-circle ~1,360 km (±0.5%)", "PASSED"),
        ("Points Calculation", "Submission with 3 Mobile Phones & 2 Laptops verified by admin", "Exact 45 points credited to wallet ledger without duplicate claims", "PASSED"),
        ("Template Routing", "Form submission by SGT University student vs Citizen", "SGT template sub_received_sgt vs General template routed correctly", "PASSED"),
        ("Zero-Leakage Security", "Audit HTML responses, JSON endpoints, and email logs for credentials", "Zero exposure of SMTP_PASSWORD, DB_PASSWORD, or secret keys", "PASSED")
    ]

    for i, (mod, scen, exp, stat) in enumerate(test_rows):
        row_idx = i + 1
        table.cell(row_idx, 0).text = mod
        table.cell(row_idx, 0).text_frame.paragraphs[0].font.bold = True
        table.cell(row_idx, 0).text_frame.paragraphs[0].font.size = Pt(11)
        table.cell(row_idx, 0).text_frame.paragraphs[0].font.color.rgb = DARK_GREEN

        table.cell(row_idx, 1).text = scen
        table.cell(row_idx, 1).text_frame.paragraphs[0].font.size = Pt(10.5)

        table.cell(row_idx, 2).text = exp
        table.cell(row_idx, 2).text_frame.paragraphs[0].font.size = Pt(10.5)

        c_stat = table.cell(row_idx, 3)
        c_stat.text = stat
        c_stat.text_frame.paragraphs[0].font.bold = True
        c_stat.text_frame.paragraphs[0].font.size = Pt(11)
        c_stat.text_frame.paragraphs[0].font.color.rgb = DARK_EMERALD
        c_stat.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        c_stat.fill.solid()
        c_stat.fill.fore_color.rgb = LIGHT_MINT

    # ==========================================
    # SLIDE 18: CHALLENGES FACED & SOLUTIONS
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    add_header(s18, "Challenges Encountered & Engineering Solutions", "17. Technical Problem Solving", 18)

    challenges = [
        ("MySQL Port Conflict (Port 3306 vs 3307)",
         "Windows had an official MySQL80 service occupying port 3306 with password locks, blocking local XAMPP MariaDB initialization.",
         "Reconfigured XAMPP MariaDB to port 3307 in my.ini and isolated the application connection parameters via .env and Config.DB_PORT."),
        ("Missing / Incomplete Geocodes in CPCB Data",
         "Government datasets frequently lacked geographic latitude/longitude coordinates, threatening map marker rendering failures.",
         "Designed graceful two-tier handling: centres with coordinates display on Leaflet with distance badges; unmapped centres remain 100% searchable via textual dropdowns."),
        ("Database Connection Exhaustion under Concurrency",
         "Multiple concurrent users performing spatial queries risked exhausting single-threaded MySQL connections.",
         "Implemented thread-safe MySQLConnectionPool (5–32 pooled connections) with automatic connection reuse, timeout guards, and transaction rollbacks."),
        ("Defensive Asynchronous Email Transmission",
         "Network latency or SMTP outages threatened to block form submission UI and cause user frustration.",
         "Decoupled email dispatch in a non-blocking try-except block; form submission succeeds immediately while failed emails are logged with a one-click admin retry.")
    ]

    for idx, (title, chall, sol) in enumerate(challenges):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.4 if idx < 2 else 4.2)
        card = add_card(s18, left_pos, top_pos, Inches(5.7), Inches(2.6), f"Challenge 0{idx+1}: {title}")
        tb = s18.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.3), Inches(1.95))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = "Problem: "
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = GOLD
        run1 = p1.add_run()
        run1.text = chall
        run1.font.bold = False
        run1.font.color.rgb = TEXT_DARK
        p1.space_after = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = "Solution: "
        p2.font.bold = True
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_GREEN
        run2 = p2.add_run()
        run2.text = sol
        run2.font.bold = False
        run2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 19: FUTURE SCOPE
    # ==========================================
    s19 = prs.slides.add_slide(blank_layout)
    add_header(s19, "Future Scope & Project Roadmap", "18. Future Enhancements", 19)

    futures = [
        ("Native Cross-Platform Mobile App",
         "Develop Flutter or React Native mobile clients providing push notifications, background GPS tracking, and offline facility caching."),
        ("Computer Vision Component Recognition (AI/ML)",
         "Deploy a Convolutional Neural Network (CNN) in PyTorch/TensorFlow to automatically identify device types and estimate e-waste weights from user photos."),
        ("IoT-Enabled Smart E-Waste Drop Bins",
         "Integrate ultrasonic fill-level sensors and RFID scanners on campus collection bins for real-time fill tracking and automated pickup dispatches."),
        ("Doorstep Logistics Route Optimization",
         "Implement Dijkstra or Genetic Algorithms to compute optimal vehicle routing for municipal pickup trucks across multiple collection points."),
        ("Blockchain-Verified Recycling Certificates",
         "Issue tamper-proof digital certificates of responsible disposal minted on a private ledger for institutional CSR compliance."),
        ("EPR Integration with Authorized Recyclers",
         "Direct API integration with authorized dismantlers to automate Extended Producer Responsibility (EPR) credit trading and reporting.")
    ]

    for idx, (title, desc) in enumerate(futures):
        left_pos = Inches(0.8 if idx % 2 == 0 else 6.8)
        top_pos = Inches(1.4 + (idx // 2) * 1.85)
        add_card(s19, left_pos, top_pos, Inches(5.7), Inches(1.7), f"✦ {title}")
        tb = s19.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.55), Inches(5.3), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 20: CONCLUSION & LEARNING OUTCOMES
    # ==========================================
    s20 = prs.slides.add_slide(blank_layout)
    add_header(s20, "Conclusion & Academic Learning Outcomes", "19. Conclusion", 20)

    c1 = add_card(s20, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4), "Project Summary & Societal Impact")
    tb = s20.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    c_pts1 = [
        ("Addressed National Crisis:", "Engineered an accessible digital bridge connecting citizens and SGT University students to authorized e-waste dismantlers."),
        ("Centralized Reliable Data:", "Consolidated scattered government records into a structured, queryable relational database."),
        ("Mathematical Geospatial Utility:", "Applied the Haversine trigonometric formula to solve real-world nearest-facility routing in real time."),
        ("Environmental Stewardship:", "Discourages hazardous informal burning and landfill dumping, safeguarding groundwater from toxic heavy metals."),
        ("Gamified Participation:", "Demonstrated that points tracking and transparent status updates successfully incentivize positive civic recycling behavior.")
    ]
    for i, (title, desc) in enumerate(c_pts1):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"✔ {title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    c2 = add_card(s20, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), "Personal & Technical Learning Outcomes")
    tb = s20.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    c_pts2 = [
        ("Full-Stack Python Web Development:", "Mastered modern Flask architecture, application factories, Jinja2 template inheritance, and RESTful APIs."),
        ("Relational Database Engineering:", "Gained practical experience in 3NF schema normalization, indexing, connection pooling, and transactional integrity."),
        ("Applied Spatial Computation:", "Deepened understanding of spherical geodesy, coordinate transformations, and Leaflet.js cartographic rendering."),
        ("Defensive Security Engineering:", "Implemented robust CSRF protection, secure password hashing (Werkzeug), and complete zero-leakage credential isolation."),
        ("Rigorous Software Testing:", "Constructed an automated 88-test suite covering edge cases, concurrent access, and defensive failure handling.")
    ]
    for i, (title, desc) in enumerate(c_pts2):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"★ {title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # ==========================================
    # SLIDE 21: THANK YOU & Q&A
    # ==========================================
    s21 = prs.slides.add_slide(blank_layout)
    bg21 = s21.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg21.fill.solid()
    bg21.fill.fore_color.rgb = DARK_GREEN
    bg21.line.fill.background()

    top_accent = s21.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.2))
    top_accent.fill.solid()
    top_accent.fill.fore_color.rgb = EMERALD
    top_accent.line.fill.background()

    # Center box
    c_box = s21.shapes.add_textbox(Inches(1.5), Inches(1.3), Inches(10.333), Inches(2.2))
    tf = c_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THANK YOU!"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "QUESTIONS & ANSWERS"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_MINT
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "EcoLocate – E-Waste Facility Locator"
    p3.font.size = Pt(20)
    p3.font.color.rgb = WHITE
    p3.alignment = PP_ALIGN.CENTER

    # Candidate Card
    card_final = add_card(s21, Inches(3.2), Inches(3.8), Inches(6.9), Inches(2.8), "Candidate Presentation Details", bg_color=CARD_BG)
    tb = s21.shapes.add_textbox(Inches(3.5), Inches(4.3), Inches(6.3), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True

    final_details = [
        ("Candidate Name:", "Yogesh"),
        ("Roll Number:", "241306039"),
        ("Academic Degree:", "BCA (Artificial Intelligence & Machine Learning)"),
        ("Section & Semester:", "Section 5A | 5th Semester"),
        ("Department:", "Faculty of Engineering and Technology"),
        ("Institution:", "SGT University, Gurugram, Haryana")
    ]
    for i, (label, val) in enumerate(final_details):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{label} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GREEN
        run = p.add_run()
        run.text = val
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK

    # Save presentation
    output_pptx = os.path.abspath(os.path.join(os.path.dirname(__file__), 'EcoLocate_External_Viva_Presentation_Yogesh_241306039.pptx'))
    prs.save(output_pptx)
    print(f"[SUCCESS] PowerPoint presentation generated: {output_pptx}")
    return output_pptx

def convert_pptx_to_pdf(pptx_path):
    """Convert PPTX to PDF using Windows PowerPoint COM Automation."""
    pdf_path = pptx_path.replace('.pptx', '.pdf')
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        powerpoint = win32com.client.DispatchEx("PowerPoint.Application")
        # 17 = ppSaveAsPDF
        deck = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
        deck.SaveAs(pdf_path, 32)  # 32 = ppSaveAsPDF
        deck.Close()
        powerpoint.Quit()
        pythoncom.CoUninitialize()
        print(f"[SUCCESS] PDF presentation generated: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"[WARNING] Could not convert to PDF via COM: {e}")
        return None

if __name__ == '__main__':
    pptx_file = create_deck()
    pdf_file = convert_pptx_to_pdf(pptx_file)
    print("Process Complete!")
