"""
Assemble and verify complete 40-page EcoLocate Academic Report.
Converts EcoLocate_Project_Report.docx to EcoLocate_Project_Report.pdf.
"""
import os
import sys
import docx
import make_report as mr

import generate_all_pages as p1_7
import generate_pages_8_to_20 as p8_20
import generate_pages_21_to_33 as p21_33
import generate_pages_34_to_40 as p34_40

doc = mr.doc

pages = [
    p1_7.build_p1, p1_7.build_p2, p1_7.build_p3, p1_7.build_p4, p1_7.build_p5, p1_7.build_p6, p1_7.build_p7,
    p8_20.build_p8, p8_20.build_p9, p8_20.build_p10, p8_20.build_p11, p8_20.build_p12, p8_20.build_p13,
    p8_20.build_p14, p8_20.build_p15, p8_20.build_p16, p8_20.build_p17, p8_20.build_p18, p8_20.build_p19, p8_20.build_p20,
    p21_33.build_p21, p21_33.build_p22, p21_33.build_p23, p21_33.build_p24, p21_33.build_p25, p21_33.build_p26,
    p21_33.build_p27, p21_33.build_p28, p21_33.build_p29, p21_33.build_p30, p21_33.build_p31, p21_33.build_p32, p21_33.build_p33,
    p34_40.build_p34, p34_40.build_p35, p34_40.build_p36, p34_40.build_p37, p34_40.build_p38, p34_40.build_p39, p34_40.build_p40
]

print(f"Total pages defined in manifest: {len(pages)}")

for idx, page_func in enumerate(pages):
    page_func()
    if idx < len(pages) - 1:
        doc.add_page_break()

docx_path = os.path.join(mr.base_dir, "EcoLocate_Project_Report.docx")
pdf_path = os.path.join(mr.base_dir, "EcoLocate_Project_Report.pdf")

doc.save(docx_path)
print(f"Saved DOCX: {docx_path} ({os.path.getsize(docx_path)} bytes)")

# Convert to PDF via Word
import win32com.client
word = None
try:
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    wb = word.Documents.Open(os.path.abspath(docx_path))
    # Wait for pagination
    wb.Repaginate()
    page_count = wb.ComputeStatistics(2) # wdStatisticPages
    print(f"Microsoft Word computed page count: {page_count}")
    
    wb.SaveAs(os.path.abspath(pdf_path), FileFormat=17) # wdFormatPDF
    wb.Close(SaveChanges=False)
    print(f"Saved PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
except Exception as e:
    print(f"Word automation error: {e}")
finally:
    if word:
        try:
            word.Quit()
        except Exception:
            pass

# Check PDF page count via pypdfium2
if os.path.exists(pdf_path):
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(pdf_path)
    print(f"pypdfium2 verified PDF page count: {len(pdf)}")
else:
    print("PDF was not created.")
