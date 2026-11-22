"""
Full 40-Page Content Definition for EcoLocate Academic Report
Student: YOGESH (Roll No. 241306039)
Course: BCA (AIML) - 5th Semester, Section A
University: SGT UNIVERSITY
"""
import os
import make_report as mr

doc = mr.doc
diag_dir = mr.diag_dir
screen_dir = mr.screen_dir
sgt_logo = mr.sgt_logo

# ==============================================================================
# PAGE 1: COVER PAGE
# ==============================================================================
def build_p1():
    if os.path.exists(sgt_logo):
        p_logo = doc.add_paragraph()
        p_logo.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = mr.Pt(10)
        p_logo.paragraph_format.space_after = mr.Pt(16)
        p_logo.add_run().add_picture(sgt_logo, width=mr.Inches(4.8))

    p1 = doc.add_paragraph()
    p1.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = mr.Pt(10)
    p1.paragraph_format.space_after = mr.Pt(6)
    r1 = p1.add_run("A PROJECT REPORT\non")
    r1.font.bold = True
    r1.font.size = mr.Pt(13)

    p2 = doc.add_paragraph()
    p2.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = mr.Pt(12)
    p2.paragraph_format.space_after = mr.Pt(6)
    r2 = p2.add_run("ECOLOCATE – E-WASTE FACILITY LOCATOR")
    r2.font.bold = True
    r2.font.size = mr.Pt(16.5)

    p3 = doc.add_paragraph()
    p3.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_after = mr.Pt(24)
    r3 = p3.add_run("A Web-Based Geographic Information and Certified Facility Locator System\nusing Python, Flask and MySQL")
    r3.font.size = mr.Pt(11)

    p4 = doc.add_paragraph()
    p4.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p4.paragraph_format.space_before = mr.Pt(20)
    p4.paragraph_format.space_after = mr.Pt(4)
    r4 = p4.add_run("BACHELOR OF COMPUTER APPLICATIONS\n(Artificial Intelligence & Machine Learning)")
    r4.font.bold = True
    r4.font.size = mr.Pt(12.5)

    p5 = doc.add_paragraph()
    p5.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p5.paragraph_format.space_before = mr.Pt(24)
    p5.paragraph_format.space_after = mr.Pt(2)
    r5 = p5.add_run("Submitted by\n")
    r5.font.size = mr.Pt(10.5)
    r5_name = p5.add_run("YOGESH\n")
    r5_name.font.bold = True
    r5_name.font.size = mr.Pt(13)
    r5_roll = p5.add_run("Roll No.: 241306039\nBCA (AIML) – 5th Semester, Section A")
    r5_roll.font.size = mr.Pt(10.5)

    p6 = doc.add_paragraph()
    p6.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p6.paragraph_format.space_before = mr.Pt(18)
    p6.paragraph_format.space_after = mr.Pt(30)
    r6 = p6.add_run("Under the guidance of\n")
    r6.font.size = mr.Pt(10.5)
    r6_g = p6.add_run("Ms. Sanchita")
    r6_g.font.bold = True
    r6_g.font.size = mr.Pt(11.5)

    p7 = doc.add_paragraph()
    p7.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p7.paragraph_format.space_before = mr.Pt(18)
    r7 = p7.add_run("SGT UNIVERSITY\nGurugram, Haryana\nAcademic Year 2026–27")
    r7.font.bold = True
    r7.font.size = mr.Pt(11.5)

# ==============================================================================
# PAGE 2: CERTIFICATE
# ==============================================================================
def build_p2():
    mr.add_chapter_title("CERTIFICATE")
    mr.add_para("This is to certify that the project report entitled “ECOLOCATE – E-WASTE FACILITY LOCATOR” is a bonafide record of the work carried out by Yogesh (Roll No. 241306039), a student of Bachelor of Computer Applications (Artificial Intelligence & Machine Learning), 5th Semester, Section A, at SGT University, in partial fulfillment of the requirements for the award of the degree.")
    mr.add_para("The work embodied in this report has been carried out under my guidance and supervision. To the best of my knowledge, the matter presented in this report has not been submitted to any other university or institution for the award of any degree or diploma.")
    
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = mr.Pt(180)
    p_sig.paragraph_format.line_spacing = 1.3
    p_sig.add_run("Project Guide\t\t\t\t\t\tHead of Department\n\nName: Ms. Sanchita\t\t\t\t\tName: _______________________\nSignature: __________________\t\t\tSignature: ____________________\n\nDate: ______________________")
    
    p_num = doc.add_paragraph()
    p_num.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = mr.Pt(120)
    p_num.add_run("1").font.size = mr.Pt(10)

# ==============================================================================
# PAGE 3: DECLARATION
# ==============================================================================
def build_p3():
    mr.add_chapter_title("DECLARATION")
    mr.add_para("I, Yogesh, hereby declare that the project report entitled “ECOLOCATE – E-WASTE FACILITY LOCATOR”, submitted to SGT University in partial fulfillment of the requirements for the degree of Bachelor of Computer Applications (Artificial Intelligence & Machine Learning), is an original work carried out by me under the guidance of my project guide.")
    mr.add_para("The information, design and implementation described in this report are the result of my own study and effort. Wherever the work of others has been used, it has been duly acknowledged in the references. This report has not been submitted, in part or in full, to any other university or institution for the award of any degree, diploma or certificate.")
    
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = mr.Pt(220)
    p_sig.alignment = mr.WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sig.add_run("Yogesh\nRoll No. 241306039\nBCA (AIML), 5th Semester, Section A")
    r.font.bold = True
    
    p_date = doc.add_paragraph()
    p_date.paragraph_format.space_before = mr.Pt(40)
    p_date.add_run("Date: ________________________")

    p_num = doc.add_paragraph()
    p_num.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = mr.Pt(120)
    p_num.add_run("2").font.size = mr.Pt(10)

# ==============================================================================
# PAGE 4: ACKNOWLEDGEMENT
# ==============================================================================
def build_p4():
    mr.add_chapter_title("ACKNOWLEDGEMENT")
    mr.add_para("I express my sincere gratitude to everyone who supported me during the planning, development and documentation of this project, “ECOLOCATE – E-WASTE FACILITY LOCATOR”.")
    mr.add_para("I am thankful to my project guide, Ms. Sanchita, for the valuable direction, constructive suggestions and encouragement provided throughout the work. I also thank the Head of the Department and the faculty members of the Bachelor of Computer Applications (Artificial Intelligence & Machine Learning) programme at SGT University for providing the academic foundation in Python development, relational database systems, web GIS technologies and software engineering that made this project possible.")
    mr.add_para("I am grateful to my classmates and friends for their feedback during testing, and to my family for their constant support and motivation. Finally, I acknowledge the Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change (MoEFCC), and the authors of the open-source libraries and literature listed in the references, whose work guided the technical and environmental aspects of this report.")
    
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = mr.Pt(200)
    p_sig.alignment = mr.WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sig.add_run("Yogesh\nRoll No. 241306039")
    r.font.bold = True

    p_num = doc.add_paragraph()
    p_num.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = mr.Pt(120)
    p_num.add_run("3").font.size = mr.Pt(10)

# ==============================================================================
# PAGE 5: ABSTRACT
# ==============================================================================
def build_p5():
    mr.add_chapter_title("ABSTRACT")
    mr.add_para("Electronic waste (e-waste) represents one of the fastest-growing environmental and public health hazards in modern society. When decommissioned electronics such as mobile phones, laptops, monitors, and circuit boards are discarded into regular municipal waste bins or handled by unorganized informal scrap dealers, toxic heavy metals—primarily Lead, Mercury, and Cadmium—leach into agricultural soil and groundwater aquifers, while open crude burning releases carcinogens into the atmosphere. Despite stringent statutory directives issued by the Central Pollution Control Board (CPCB), public recycling participation remains hindered by the lack of an accessible, centralized digital directory connecting consumers with authorized recyclers.")
    mr.add_para("This project presents EcoLocate – E-Waste Facility Locator, an enterprise-grade web application developed using Python, Flask, MySQL, HTML5, CSS3, JavaScript, and Leaflet.js with OpenStreetMap. EcoLocate centralizes verified recycling facilities across India into an indexed MySQL database. Citizens can dynamically search and filter facilities by state, city, and device type, discover nearby authorized recyclers through browser geolocation and Haversine distance calculations, inspect verified contact channels (official websites, phone numbers, email), and calculate estimated recycling incentive points through an interactive EcoRewards calculator.")
    mr.add_para("The report documents the complete engineering life cycle of the application: requirement analysis, environmental significance, gap identification, software and hardware requirements, system objectives, timeline planning, architectural design, implementation, and automated verification across 59 test cases. The platform incorporates a dedicated administrative management portal guarded by role-based session boundaries, facilitating batch CSV ingestion, facility verification auditing, and non-intrusive user activity analytics to monitor regional demand.")
    mr.add_para("E-Waste Management, Facility Locator, Python Flask, MySQL, Leaflet.js, Haversine Distance Formula, OpenStreetMap, Environmental Awareness, EcoRewards, Admin Dashboard.", bold_prefix="Keywords: ")

    p_num = doc.add_paragraph()
    p_num.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = mr.Pt(70)
    p_num.add_run("4").font.size = mr.Pt(10)

# ==============================================================================
# PAGE 6: LIST OF ABBREVIATIONS
# ==============================================================================
def build_p6():
    mr.add_chapter_title("LIST OF ABBREVIATIONS")
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
    mr.add_table_custom(["Abbreviation", "Full Form"], abbr_data, [1.5, 4.8], "Table 0.1: Abbreviations used in this report")

    p_num = doc.add_paragraph()
    p_num.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = mr.Pt(30)
    p_num.add_run("5").font.size = mr.Pt(10)

# ==============================================================================
# PAGE 7: TABLE OF CONTENTS
# ==============================================================================
def build_p7():
    mr.add_chapter_title("TABLE OF CONTENTS")
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
    p.paragraph_format.space_before = mr.Pt(12)
    p.paragraph_format.line_spacing = 1.6
    for title, pg in toc_data:
        dots_len = 70 - len(title) - len(pg)
        dots = " ." * (dots_len // 2)
        r1 = p.add_run(f"{title} {dots} ")
        r1.font.bold = True
        r1.font.size = mr.Pt(10)
        r2 = p.add_run(f"{pg}\n")
        r2.font.bold = True
        r2.font.size = mr.Pt(10)

    p_num = doc.add_paragraph()
    p_num.alignment = mr.WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = mr.Pt(100)
    p_num.add_run("6").font.size = mr.Pt(10)

print('Compiled Pages 1 to 7.')
