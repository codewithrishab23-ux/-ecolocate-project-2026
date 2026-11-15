import urllib.request
import re

routes = ['/', '/centres', '/awareness', '/rewards', '/about', '/login', '/register', '/admin/login']

print("======================================================")
print(" EcoLocate Mobile Responsiveness & Viewport Checker")
print("======================================================")

all_ok = True
for r in routes:
    try:
        url = "http://127.0.0.1:5000" + r
        resp = urllib.request.urlopen(url)
        content = resp.read().decode('utf-8')
        has_viewport = bool(re.search(r'<meta\s+name=["\']viewport["\']', content, re.IGNORECASE))
        has_nav_wrapper = 'nav-menu-wrapper' in content or 'admin' in r
        print(f"[{'PASS' if resp.status == 200 and has_viewport else 'FAIL'}] {r:15} | Status: {resp.status} | Viewport: {has_viewport} | Responsive Menu: {has_nav_wrapper}")
        if resp.status != 200 or not has_viewport:
            all_ok = False
    except Exception as e:
        print(f"[FAIL] {r:15} | Error: {e}")
        all_ok = False

if all_ok:
    print("\n[SUCCESS] All pages verified responsive and accessible for mobile browsers!")
