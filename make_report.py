"""
EcoLocate Comprehensive 40-Page Academic Project Report Builder
Generates EcoLocate_Project_Report.docx and converts to EcoLocate_Project_Report.pdf.
Student: YOGESH (Roll No. 241306039)
Course: BCA (AIML) - 5th Semester, Section A
University: SGT UNIVERSITY, Gurugram, Haryana
"""
import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

base_dir = os.path.dirname(os.path.abspath(__file__))
diag_dir = os.path.join(base_dir, 'report_assets', 'diagrams')
screen_dir = os.path.join(base_dir, 'report_assets', 'screenshots')
sgt_logo = os.path.join(base_dir, 'sgt_logo_banner.png')

doc = Document()

# Set standard A4 margins
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.95)
    section.right_margin = Inches(0.95)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

style_normal = doc.styles['Normal']
style_normal.font.name = 'Times New Roman'
style_normal.font.size = Pt(10)
style_normal.font.color.rgb = RGBColor(0, 0, 0)
style_normal.paragraph_format.line_spacing = 1.13
style_normal.paragraph_format.space_after = Pt(3)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=50, bottom=50, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="A0A0A0", sz="4", val="single"):
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
    p.paragraph_format.space_after = Pt(7)
    add_header_line(p)
    run = p.add_run(title_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13.5)
    run.font.bold = True
    return p

def add_sec_heading(sec_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4.5)
    p.paragraph_format.space_after = Pt(1.5)
    run = p.add_run(sec_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    run.font.bold = True
    return p

def add_para(text, bold_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.13
    p.paragraph_format.space_after = Pt(3)
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
    p.paragraph_format.line_spacing = 1.11
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
        cp.paragraph_format.space_before = Pt(3.5)
        cp.paragraph_format.space_after = Pt(1.5)
        c_run = cp.add_run(caption)
        c_run.font.bold = True
        c_run.font.size = Pt(9)
        c_run.font.name = 'Times New Roman'
        
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "D9E1F2")
        set_cell_margins(hdr_cells[i], top=40, bottom=40, left=70, right=70)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)
        p.runs[0].font.name = 'Times New Roman'
        
    for r_idx, r_data in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        for c_idx, val in enumerate(r_data):
            row_cells[c_idx].text = str(val)
            set_cell_margins(row_cells[c_idx], top=35, bottom=35, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(8)
                p.runs[0].font.name = 'Times New Roman'
                
    if col_widths:
        for row in tbl.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(1.5)
    return tbl

def add_image_figure(img_path, width_in, caption):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2.5)
        p.paragraph_format.space_after = Pt(1)
        p.add_run().add_picture(img_path, width=Inches(width_in))
        
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(1)
        cp.paragraph_format.space_after = Pt(3.5)
        r = cp.add_run(caption)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.name = 'Times New Roman'

def add_page_footer_num(num_str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(num_str)
    r.font.size = Pt(9.5)
    r.font.name = 'Times New Roman'

print('Initialized document builder helpers.')
