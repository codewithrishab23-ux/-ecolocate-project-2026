"""
Generate full 40-page academic content for EcoLocate Project Report.
Student: YOGESH (Roll No. 241306039)
Course: BCA (AIML) - 5th Semester, Section A
University: SGT UNIVERSITY, Gurugram, Haryana
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

base_dir = os.path.dirname(__file__)
diag_dir = os.path.join(base_dir, 'report_assets', 'diagrams')
screen_dir = os.path.join(base_dir, 'report_assets', 'screenshots')
sgt_logo = os.path.join(base_dir, 'sgt_logo_banner.png')

doc = Document()

# Configure page margins (0.75 top/bottom, 1.0 left/right)
for section in doc.sections:
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.header_distance = Inches(0.4)
    section.footer_distance = Inches(0.4)

# Set base Normal font
style_normal = doc.styles['Normal']
style_normal.font.name = 'Times New Roman'
style_normal.font.size = Pt(10.5)
style_normal.font.color.rgb = RGBColor(0, 0, 0)
style_normal.paragraph_format.line_spacing = 1.15
style_normal.paragraph_format.space_after = Pt(3.5)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_header_line(p):
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:bottom w:val="single" w:sz="6" w:space="4" w:color="808080"/>
        </w:pBdr>
    ''')
    pPr.append(pBdr)

def add_chapter_title(title_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    add_header_line(p)
    run = p.add_run(title_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14.5)
    run.font.bold = True
    return p

def add_sec_heading(sec_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(sec_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    return p

def add_para(text, bold_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.14
    p.paragraph_format.space_after = Pt(3.5)
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.bold = True
        r_b.font.name = 'Times New Roman'
    r_t = p.add_run(text)
    r_t.font.name = 'Times New Roman'
    return p

def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.12
    p.paragraph_format.space_after = Pt(1.5)
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.bold = True
        r_b.font.name = 'Times New Roman'
    r_t = p.add_run(text)
    r_t.font.name = 'Times New Roman'
    return p

def add_table_custom(headers, rows, col_widths=None, caption=None):
    if caption:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cp.paragraph_format.space_before = Pt(4)
        cp.paragraph_format.space_after = Pt(2)
        c_run = cp.add_run(caption)
        c_run.font.bold = True
        c_run.font.size = Pt(9.5)
        c_run.font.name = 'Times New Roman'
        
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "D9E1F2")
        set_cell_margins(hdr_cells[i], top=60, bottom=60, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.name = 'Times New Roman'
        
    for r_idx, r_data in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        for c_idx, val in enumerate(r_data):
            row_cells[c_idx].text = str(val)
            set_cell_margins(row_cells[c_idx], top=50, bottom=50, left=80, right=80)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(8.5)
                p.runs[0].font.name = 'Times New Roman'
                
    if col_widths:
        for row in tbl.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return tbl

def add_image_figure(img_path, width_in, caption):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(1)
        p.add_run().add_picture(img_path, width=Inches(width_in))
        
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(1)
        cp.paragraph_format.space_after = Pt(4)
        r = cp.add_run(caption)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.name = 'Times New Roman'

# ==============================================================================
# PAGE 1: COVER PAGE
# ==============================================================================
def build_page_1():
    # University Logo Banner
    if os.path.exists(sgt_logo):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(10)
        p_logo.paragraph_format.space_after = Pt(18)
        p_logo.add_run().add_picture(sgt_logo, width=Inches(5.0))

    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(12)
    p1.paragraph_format.space_after = Pt(6)
    r1 = p1.add_run("A PROJECT REPORT\non")
    r1.font.bold = True
    r1.font.size = Pt(13)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(12)
    p2.paragraph_format.space_after = Pt(6)
    r2 = p2.add_run("ECOLOCATE – E-WASTE FACILITY LOCATOR")
    r2.font.bold = True
    r2.font.size = Pt(17)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_after = Pt(28)
    r3 = p3.add_run("A Web-Based Geographic Information and Certified Facility Locator System\nusing Python, Flask and MySQL")
    r3.font.size = Pt(11)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p4.paragraph_format.space_before = Pt(24)
    p4.paragraph_format.space_after = Pt(4)
    r4 = p4.add_run("BACHELOR OF COMPUTER APPLICATIONS\n(Artificial Intelligence & Machine Learning)")
    r4.font.bold = True
    r4.font.size = Pt(13)

    p5 = doc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p5.paragraph_format.space_before = Pt(28)
    p5.paragraph_format.space_after = Pt(2)
    r5 = p5.add_run("Submitted by\n")
    r5.font.size = Pt(11)
    r5_name = p5.add_run("YOGESH\n")
    r5_name.font.bold = True
    r5_name.font.size = Pt(13.5)
    r5_roll = p5.add_run("Roll No.: 241306039\nBCA (AIML) – 5th Semester, Section A")
    r5_roll.font.size = Pt(11)

    p6 = doc.add_paragraph()
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p6.paragraph_format.space_before = Pt(20)
    p6.paragraph_format.space_after = Pt(36)
    r6 = p6.add_run("Under the guidance of\n")
    r6.font.size = Pt(11)
    r6_g = p6.add_run("Ms. Sanchita")
    r6_g.font.bold = True
    r6_g.font.size = Pt(12)

    p7 = doc.add_paragraph()
    p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p7.paragraph_format.space_before = Pt(20)
    r7 = p7.add_run("SGT UNIVERSITY\nGurugram, Haryana\nAcademic Year 2026–27")
    r7.font.bold = True
    r7.font.size = Pt(12)

# ==============================================================================
# PAGE 2: CERTIFICATE
# ==============================================================================
def build_page_2():
    add_chapter_title("CERTIFICATE")
    add_para("This is to certify that the project report entitled “ECOLOCATE – E-WASTE FACILITY LOCATOR” is a bonafide record of the work carried out by Yogesh (Roll No. 241306039), a student of Bachelor of Computer Applications (Artificial Intelligence & Machine Learning), 5th Semester, Section A, at SGT University, in partial fulfillment of the requirements for the award of the degree.")
    add_para("The work embodied in this report has been carried out under my guidance and supervision. To the best of my knowledge, the matter presented in this report has not been submitted to any other university or institution for the award of any degree or diploma.")
    
    # Signature blocks
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(180)
    p_sig.paragraph_format.line_spacing = 1.3
    p_sig.add_run("Project Guide\t\t\t\t\t\tHead of Department\n\nName: Ms. Sanchita\t\t\t\t\tName: _______________________\nSignature: __________________\t\t\tSignature: ____________________\n\nDate: ______________________")
    
    # Page footer number 1
    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(120)
    p_num.add_run("1").font.size = Pt(10)

# ==============================================================================
# PAGE 3: DECLARATION
# ==============================================================================
def build_page_3():
    add_chapter_title("DECLARATION")
    add_para("I, Yogesh, hereby declare that the project report entitled “ECOLOCATE – E-WASTE FACILITY LOCATOR”, submitted to SGT University in partial fulfillment of the requirements for the degree of Bachelor of Computer Applications (Artificial Intelligence & Machine Learning), is an original work carried out by me under the guidance of my project guide.")
    add_para("The information, design and implementation described in this report are the result of my own study and effort. Wherever the work of others has been used, it has been duly acknowledged in the references. This report has not been submitted, in part or in full, to any other university or institution for the award of any degree, diploma or certificate.")
    
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(220)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sig.add_run("Yogesh\nRoll No. 241306039\nBCA (AIML), 5th Semester, Section A")
    r.font.bold = True
    
    p_date = doc.add_paragraph()
    p_date.paragraph_format.space_before = Pt(40)
    p_date.add_run("Date: ________________________")

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(120)
    p_num.add_run("2").font.size = Pt(10)

# ==============================================================================
# PAGE 4: ACKNOWLEDGEMENT
# ==============================================================================
def build_page_4():
    add_chapter_title("ACKNOWLEDGEMENT")
    add_para("I express my sincere gratitude to everyone who supported me during the planning, development and documentation of this project, “ECOLOCATE – E-WASTE FACILITY LOCATOR”.")
    add_para("I am thankful to my project guide, Ms. Sanchita, for the valuable direction, constructive suggestions and encouragement provided throughout the work. I also thank the Head of the Department and the faculty members of the Bachelor of Computer Applications (Artificial Intelligence & Machine Learning) programme at SGT University for providing the academic foundation in Python development, relational database systems, web GIS technologies and software engineering that made this project possible.")
    add_para("I am grateful to my classmates and friends for their feedback during testing, and to my family for their constant support and motivation. Finally, I acknowledge the Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change (MoEFCC), and the authors of the open-source libraries and literature listed in the references, whose work guided the technical and environmental aspects of this report.")
    
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(200)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sig.add_run("Yogesh\nRoll No. 241306039")
    r.font.bold = True

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(120)
    p_num.add_run("3").font.size = Pt(10)

# ==============================================================================
# PAGE 5: ABSTRACT
# ==============================================================================
def build_page_5():
    add_chapter_title("ABSTRACT")
    add_para("Electronic waste (e-waste) represents one of the fastest-growing environmental and public health hazards in modern society. When decommissioned electronics such as mobile phones, laptops, monitors, and circuit boards are discarded into regular municipal waste bins or handled by unorganized informal scrap dealers, toxic heavy metals—primarily Lead, Mercury, and Cadmium—leach into agricultural soil and groundwater aquifers, while open crude burning releases carcinogens into the atmosphere. Despite stringent statutory directives issued by the Central Pollution Control Board (CPCB), public recycling participation remains hindered by the lack of an accessible, centralized digital directory connecting consumers with authorized recyclers.")
    add_para("This project presents EcoLocate – E-Waste Facility Locator, an enterprise-grade web application developed using Python, Flask, MySQL, HTML5, CSS3, JavaScript, and Leaflet.js with OpenStreetMap. EcoLocate centralizes verified recycling facilities across India into an indexed MySQL database. Citizens can dynamically search and filter facilities by state, city, and device type, discover nearby authorized recyclers through browser geolocation and Haversine distance calculations, inspect verified contact channels (official websites, phone numbers, email), and calculate estimated recycling incentive points through an interactive EcoRewards calculator.")
    add_para("The report documents the complete engineering life cycle of the application: requirement analysis, environmental significance, gap identification, software and hardware requirements, system objectives, timeline planning, architectural design, implementation, and automated verification across 59 test cases. The platform incorporates a dedicated administrative management portal guarded by role-based session boundaries, facilitating batch CSV ingestion, facility verification auditing, and non-intrusive user activity analytics to monitor regional demand.")
    add_para("E-Waste Management, Facility Locator, Python Flask, MySQL, Leaflet.js, Haversine Distance Formula, OpenStreetMap, Environmental Awareness, EcoRewards, Admin Dashboard.", bold_prefix="Keywords: ")

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(70)
    p_num.add_run("4").font.size = Pt(10)

# ==============================================================================
# PAGE 6: LIST OF ABBREVIATIONS
# ==============================================================================
def build_page_6():
    add_chapter_title("LIST OF ABBREVIATIONS")
    abbr_data = [
        ["CPCB", "Central Pollution Control Board (Government of India)"],
        ["SPCB", "State Pollution Control Board"],
        ["MoEFCC", "Ministry of Environment, Forest and Climate Change"],
        ["WEEE", "Waste Electrical and Electronic Equipment"],
        ["EPR", "Extended Producer Responsibility"],
        ["GIS", "Geographic Information System"],
        ["GPS", "Global Positioning System"],
        ["REST", "Representational State Transfer"],
        ["API", "Application Programming Interface"],
        ["CRUD", "Create, Read, Update, Delete"],
        ["PK / FK", "Primary Key / Foreign Key"],
        ["ER", "Entity-Relationship"],
        ["DFD", "Data Flow Diagram"],
        ["MTA", "Metric Tonnes per Annum (Recycling Capacity)"],
        ["SQL", "Structured Query Language"],
        ["HTML", "HyperText Markup Language"],
        ["CSS", "Cascading Style Sheets"],
        ["CSP", "Content Security Policy"],
        ["CSRF", "Cross-Site Request Forgery"],
        ["XSS", "Cross-Site Scripting"],
        ["OWASP", "Open Worldwide Application Security Project"],
        ["UI / UX", "User Interface / User Experience"]
    ]
    add_table_custom(["Abbreviation", "Full Form"], abbr_data, [1.6, 4.9], "Table 0.1: Abbreviations used in this report")

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(30)
    p_num.add_run("5").font.size = Pt(10)

# ==============================================================================
# PAGE 7: TABLE OF CONTENTS
# ==============================================================================
def build_page_7():
    add_chapter_title("TABLE OF CONTENTS")
    toc_data = [
        ["CHAPTER 1: INTRODUCTION", "1"],
        ["CHAPTER 2: SIGNIFICANCE AND RELEVANCE TO SOCIETY", "4"],
        ["CHAPTER 3: REQUIREMENT ANALYSIS", "7"],
        ["CHAPTER 4: GAP IDENTIFICATION", "10"],
        ["CHAPTER 5: HARDWARE AND SOFTWARE REQUIREMENTS", "13"],
        ["CHAPTER 6: OBJECTIVES", "15"],
        ["CHAPTER 7: EXPECTED OUTCOMES", "17"],
        ["CHAPTER 8: PROJECT TIMELINE", "19"],
        ["CHAPTER 9: SYSTEM DESIGN", "21"],
        ["CHAPTER 10: IMPLEMENTATION AND TESTING", "30"],
        ["CHAPTER 11: CONCLUSION AND FUTURE SCOPE", "35"],
        ["APPENDIX", "37"],
        ["REFERENCES", "41"]
    ]
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.line_spacing = 1.6
    for title, pg in toc_data:
        dots_len = 70 - len(title) - len(pg)
        dots = " ." * (dots_len // 2)
        r1 = p.add_run(f"{title} {dots} ")
        r1.font.bold = True
        r1.font.size = Pt(10)
        r2 = p.add_run(f"{pg}\n")
        r2.font.bold = True
        r2.font.size = Pt(10)

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(100)
    p_num.add_run("6").font.size = Pt(10)

# ==============================================================================
# PAGE 8: CHAPTER 1: INTRODUCTION (1.1, 1.2, 1.3)
# ==============================================================================
def build_page_8():
    add_chapter_title("CHAPTER 1: INTRODUCTION")
    add_sec_heading("1.1 Introduction")
    add_para("The rapid acceleration of consumer electronics manufacturing, shortened product replacement cycles, and widespread adoption of digital technologies have made electronic waste (e-waste) the fastest-growing solid waste stream globally. Electronic waste encompasses all discarded electrical and electronic equipment—ranging from mobile phones, laptops, and computer peripherals to televisions, battery packs, and household appliances. While these devices drive digital transformation and economic productivity, their improper disposal poses severe ecological and toxicological threats.")
    add_para("In India, despite established statutory frameworks formulated by the Central Pollution Control Board (CPCB) and State Pollution Control Boards (SPCBs), a significant percentage of discarded electronic devices ends up in municipal landfills or the unorganized informal recycling sector. The primary obstacle faced by citizens and corporate institutions is not the absence of authorized dismantlers, but the absence of a reliable, user-friendly digital system to locate, verify, and contact authorized facilities.")
    add_para("This project develops EcoLocate – E-Waste Facility Locator, an enterprise-grade geographic web application built using Python, Flask, MySQL, and Leaflet.js with OpenStreetMap. EcoLocate bridges the critical information divide by providing an intuitive, transparent, and verified directory of authorized recycling centres, empowering citizens to divert hazardous heavy metals into circular supply chains.")

    add_sec_heading("1.2 Background")
    add_para("Under the E-Waste (Management) Rules enacted by the Ministry of Environment, Forest and Climate Change (MoEFCC), formal recycling units must possess specialized environmental authorization, certified pollution control measures, and scientific material recovery infrastructure. However, official CPCB rosters are distributed in static tabular formats and PDF files, making it tedious for ordinary citizens to identify nearby facilities, verify working domains, or obtain geographic directions.")
    add_para("EcoLocate transforms static regulatory records into an interactive geospatial platform. By integrating browser geolocation, Haversine proximity calculations, and interactive map visualizations, the application makes authorized recycling accessible to every citizen.")

    add_sec_heading("1.3 Problem Statement")
    add_para("Citizens and institutions lack a centralized, verified, and interactive digital platform to locate authorized electronic waste recycling facilities. Traditional disposal routes rely on informal scrap collectors who employ hazardous acid-leaching and open burning techniques, causing severe soil pollution and toxic human exposure. The core problem addressed by this project is the creation of a dedicated, real-time, location-aware E-Waste Facility Locator and environmental awareness portal.", bold_prefix="Core Problem: ")

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(30)
    p_num.add_run("1").font.size = Pt(10)

# ==============================================================================
# PAGE 9: CHAPTER 1 continued (1.4, 1.5, 1.6, 1.7)
# ==============================================================================
def build_page_9():
    add_sec_heading("1.4 Scope")
    add_para("The scope of EcoLocate encompasses user-facing facility discovery, geospatial distance computation, environmental education, incentive gamification, and back-office administrative management. The project provides an end-to-end web system backed by a robust MySQL relational database.")
    add_bullet("User search by State, City, and Device category; proximity detection via Geolocation API and Haversine formula; interactive Leaflet.js map with facility pins; verified official contact channels; educational curriculum on hazardous heavy metals (Lead, Mercury, Cadmium); dynamic EcoRewards calculator with personal history persistence; and role-separated Admin Dashboard for CRUD management, CSV ingestion, and user activity audit tracking.", bold_prefix="In Scope: ")
    add_bullet("Physical courier pickup logistics, third-party payment gateway disbursement for reward redemption, and direct IoT smart-bin telemetry (identified as future enhancements).", bold_prefix="Out of Scope (Current Version): ")

    add_sec_heading("1.5 Need")
    add_para("Traditional solid waste infrastructure cannot safely process hazardous electronic items. Developing a centralized digital locator eliminates information asymmetry, ensures compliance with national recycling policies, prevents toxic groundwater contamination, and fosters citizen participation through measurable recycling incentives.")

    add_sec_heading("1.6 Advantages")
    add_bullet("Centralized MySQL database of 87 CPCB-verified recycling facilities across Indian states.", bold_prefix="Verified Directory: ")
    add_bullet("Zero-cost OpenStreetMap integration with Haversine distance calculations.", bold_prefix="Geospatial Proximity: ")
    add_bullet("Comprehensive curriculum detailing hazards of Lead, Mercury, and Cadmium.", bold_prefix="Environmental Awareness: ")
    add_bullet("Interactive points formula estimating CO2 diversion and raw material recovery.", bold_prefix="Incentivized Rewards: ")
    add_bullet("Full facility CRUD, CSV batch ingestion, and live user search activity tracking.", bold_prefix="Executive Administration: ")
    add_bullet("Werkzeug password hashing, CSRF defense, and strict admin boundary enforcement.", bold_prefix="Security & Privacy: ")

    add_sec_heading("1.7 Project Overview")
    add_para("EcoLocate is engineered using a three-layer software architecture. The frontend utilizes HTML5, CSS3, vanilla JavaScript, and Leaflet.js for responsive mapping. The application tier runs Python Flask with parameterized SQL routing and session management. The data tier utilizes MySQL (ewaste_db) with thread-safe connection pooling and indexed tables.")

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(25)
    p_num.add_run("2").font.size = Pt(10)

# ==============================================================================
# PAGE 10: CHAPTER 1 continued (1.8, 1.9, 1.10)
# ==============================================================================
def build_page_10():
    add_sec_heading("1.8 Project Context")
    add_para("EcoLocate is designed as an environmental technology and digital governance solution. Rather than operating as an isolated database, it combines principles of spatial analysis, public health awareness, circular economic modeling, and administrative oversight. The platform aligns with the broader objectives of the Digital India programme, Smart Cities Mission, and Extended Producer Responsibility (EPR) guidelines issued by the MoEFCC.")

    add_sec_heading("1.9 Organization of the Report")
    add_para("The remainder of this report is organized as follows:")
    add_bullet("Details environmental hazards, public health risks, circular recovery, and academic relevance.", bold_prefix="Chapter 2 (Significance): ")
    add_bullet("Presents functional, non-functional, hardware, software, and security requirements.", bold_prefix="Chapter 3 (Requirement Analysis): ")
    add_bullet("Evaluates traditional disposal limitations and establishes the proposed system's advantages.", bold_prefix="Chapter 4 (Gap Identification): ")
    add_bullet("Specifies hardware specifications, runtime technologies, and software libraries.", bold_prefix="Chapter 5 (Technical Requirements): ")
    add_bullet("Defines primary, functional, geospatial, administrative, and academic goals.", bold_prefix="Chapter 6 (Objectives): ")
    add_bullet("Outlines deliverables, verification metrics, and tangible community benefits.", bold_prefix="Chapter 7 (Expected Outcomes): ")
    add_bullet("Presents the 5-week development methodology and Gantt scheduling chart.", bold_prefix="Chapter 8 (Project Timeline): ")
    add_bullet("Covers 3-layer architecture, Use-Case diagrams, DFDs, ER schema, and Data Dictionary.", bold_prefix="Chapter 9 (System Design): ")
    add_bullet("Documents module implementation details and 59 automated test case executions.", bold_prefix="Chapter 10 (Implementation & Testing): ")
    add_bullet("Summarizes project accomplishments and identifies future enhancement paths.", bold_prefix="Chapter 11 (Conclusion & Future Scope): ")
    add_bullet("Includes database tables, system screenshots, code snippets, manual, and references.", bold_prefix="Appendix & References: ")

    add_sec_heading("1.10 Chapter Summary")
    add_para("This chapter introduced EcoLocate, its statutory background, problem statement, technical scope, practical advantages, and structural organization. By combining Python Flask backend logic, Leaflet geospatial mapping, and MySQL data management, the platform directly resolves the critical challenge of locating authorized electronic waste facilities across India.")

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(30)
    p_num.add_run("3").font.size = Pt(10)

print('Compiled Chapter 1.')
