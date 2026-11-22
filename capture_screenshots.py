"""
Capture high-resolution authentic screenshots of EcoLocate application for academic project report.
"""
import os
import time
from playwright.sync_api import sync_playwright

output_dir = os.path.join(os.path.dirname(__file__), 'report_assets', 'screenshots')
os.makedirs(output_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()

    # 1. Home Page
    page.goto('http://127.0.0.1:5000/')
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(output_dir, 'fig_b1_home.png'))
    print('Captured fig_b1_home.png')

    # 2. Registration Page
    page.goto('http://127.0.0.1:5000/register')
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(output_dir, 'fig_b2_register.png'))
    print('Captured fig_b2_register.png')

    # 3. Login Page
    page.goto('http://127.0.0.1:5000/login')
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(output_dir, 'fig_b3_login.png'))
    print('Captured fig_b3_login.png')

    # 4. Centres Search & Map Page
    page.goto('http://127.0.0.1:5000/centres')
    page.wait_for_timeout(2000)
    page.screenshot(path=os.path.join(output_dir, 'fig_b4_centres_search.png'))
    print('Captured fig_b4_centres_search.png')

    # 5. Awareness Curriculum Page
    page.goto('http://127.0.0.1:5000/awareness')
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(output_dir, 'fig_b5_awareness.png'))
    print('Captured fig_b5_awareness.png')

    # 6. Rewards Calculator Page
    page.goto('http://127.0.0.1:5000/rewards')
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(output_dir, 'fig_b6_rewards.png'))
    print('Captured fig_b6_rewards.png')

    # 7. Admin Login
    page.goto('http://127.0.0.1:5000/admin/login')
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(output_dir, 'fig_b7_admin_login.png'))
    print('Captured fig_b7_admin_login.png')

    # Sign in to Admin
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "AdminSecure2026!")
    page.click("button[type='submit']")
    page.wait_for_timeout(2000)

    # 8. Admin Dashboard
    page.screenshot(path=os.path.join(output_dir, 'fig_b8_admin_dashboard.png'))
    print('Captured fig_b8_admin_dashboard.png')

    # 9. Admin Centres Management
    page.goto('http://127.0.0.1:5000/admin/centres')
    page.wait_for_timeout(1500)
    page.screenshot(path=os.path.join(output_dir, 'fig_b9_admin_centres.png'))
    print('Captured fig_b9_admin_centres.png')

    # 10. Admin User Activity Tracking
    page.goto('http://127.0.0.1:5000/admin/activities')
    page.wait_for_timeout(1500)
    page.screenshot(path=os.path.join(output_dir, 'fig_b10_admin_activities.png'))
    print('Captured fig_b10_admin_activities.png')

    # 11. Admin CSV Ingestion
    page.goto('http://127.0.0.1:5000/admin/centres/import-csv')
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(output_dir, 'fig_b11_admin_csv_import.png'))
    print('Captured fig_b11_admin_csv_import.png')

    # 12. Admin Users Moderation
    page.goto('http://127.0.0.1:5000/admin/users')
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(output_dir, 'fig_b12_admin_users.png'))
    print('Captured fig_b12_admin_users.png')

    browser.close()

print('All 12 screenshots captured successfully!')
