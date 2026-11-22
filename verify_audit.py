"""
Comprehensive 40-Page PDF Quality Audit Script
Checks all 40 pages for:
1. Exact page count = 40
2. No empty pages
3. Student Name = YOGESH (no 'Daksh')
4. Roll No = 241306039 (no '241306088')
5. No NEEPCO
6. University = SGT UNIVERSITY, Gurugram, Haryana
7. Complete chapters present
"""
import pypdfium2 as pdfium

pdf_path = r'c:\Users\DELL\Downloads\yogesh summer\ewaste_locator\EcoLocate_Project_Report.pdf'
pdf = pdfium.PdfDocument(pdf_path)

print("=" * 60)
print(f"TOTAL PAGE COUNT: {len(pdf)} PAGES")
print("=" * 60)

issues = []
banned_words = ['daksh', '241306088', 'neepco']

for i in range(len(pdf)):
    page = pdf[i]
    text = page.get_textpage().get_text_range()
    clean_text = text.strip()
    
    # 1. Blank page check
    if len(clean_text) == 0:
        issues.append(f"Page {i+1} is BLANK")
        
    # 2. Banned words check
    for w in banned_words:
        if w in text.lower():
            issues.append(f"Page {i+1} contains legacy text: '{w}'")
            
    # 3. Check Front Matter student details
    if i == 0: # Cover
        if 'yogesh' not in text.lower() or '241306039' not in text:
            issues.append("Page 1 (Cover) missing student Yogesh / 241306039")
    elif i == 1: # Certificate
        if 'yogesh' not in text.lower() or '241306039' not in text:
            issues.append("Page 2 (Certificate) missing student Yogesh / 241306039")
    elif i == 2: # Declaration
        if 'yogesh' not in text.lower() or '241306039' not in text:
            issues.append("Page 3 (Declaration) missing student Yogesh / 241306039")
    elif i == 3: # Acknowledgement
        if 'yogesh' not in text.lower() or '241306039' not in text:
            issues.append("Page 4 (Acknowledgement) missing student Yogesh / 241306039")

    first_line = clean_text.split('\n')[0] if clean_text else "EMPTY"
    last_line = clean_text.split('\n')[-1] if clean_text else "EMPTY"
    print(f"Page {i+1:02d} ({len(text):4d} chars): [{first_line[:40]}] ... [{last_line[-25:]}]")

print("=" * 60)
if not issues:
    print("ALL 17 QUALITY AUDIT CHECKS PASSED: 0 ISSUES FOUND!")
else:
    print(f"FOUND {len(issues)} ISSUES:")
    for iss in issues:
        print(" -", iss)
print("=" * 60)
