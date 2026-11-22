"""
Database Migration Script for EcoLocate Email Management System
Creates email_templates and email_logs tables, adds confirmation columns
to ewaste_submissions, and seeds initial professional templates for
SGT University students and general users.
"""

from db import execute_query

def run_email_migration():
    print("[1/4] Ensuring ewaste_submissions has confirmed_at and confirmed_by columns...")
    try:
        # Check if confirmed_at exists
        cols = execute_query("DESCRIBE ewaste_submissions", fetchall=True) or []
        col_names = [c['Field'] for c in cols]
        
        if 'confirmed_at' not in col_names:
            print("  -> Adding confirmed_at column...")
            execute_query("ALTER TABLE ewaste_submissions ADD COLUMN confirmed_at DATETIME NULL AFTER points_approved_by", commit=True)
            
        if 'confirmed_by' not in col_names:
            print("  -> Adding confirmed_by column...")
            execute_query("""
            ALTER TABLE ewaste_submissions 
            ADD COLUMN confirmed_by INT NULL AFTER confirmed_at,
            ADD CONSTRAINT fk_sub_confirmed_by FOREIGN KEY (confirmed_by) REFERENCES admins (id) ON DELETE SET NULL
            """, commit=True)
    except Exception as e:
        print(f"  Note on column addition: {e}")

    print("[2/4] Creating table 'email_templates'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS email_templates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        template_key VARCHAR(100) NOT NULL UNIQUE,
        template_name VARCHAR(150) NOT NULL,
        user_category VARCHAR(50) NOT NULL,
        email_type VARCHAR(50) NOT NULL,
        subject VARCHAR(255) NOT NULL,
        heading VARCHAR(255) NOT NULL,
        greeting VARCHAR(255) NOT NULL,
        confirmation_message TEXT NOT NULL,
        body TEXT NOT NULL,
        additional_instructions TEXT NULL,
        closing_message TEXT NOT NULL,
        sender_display_name VARCHAR(150) NOT NULL DEFAULT 'EcoLocate Team',
        is_active TINYINT(1) NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_tpl_cat_type (user_category, email_type),
        INDEX idx_tpl_key (template_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    print("[3/4] Creating table 'email_logs'...")
    execute_query("""
    CREATE TABLE IF NOT EXISTS email_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_id INT NULL,
        recipient_email VARCHAR(150) NOT NULL,
        recipient_name VARCHAR(150) NULL,
        user_category VARCHAR(50) NOT NULL,
        email_type VARCHAR(50) NOT NULL,
        template_id INT NULL,
        subject VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'Pending',
        error_message TEXT NULL,
        attempt_count INT NOT NULL DEFAULT 1,
        sent_at DATETIME NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_elog_sub (submission_id),
        INDEX idx_elog_status (status),
        INDEX idx_elog_type (email_type),
        INDEX idx_elog_cat (user_category),
        INDEX idx_elog_created (created_at),
        CONSTRAINT fk_elog_sub FOREIGN KEY (submission_id) REFERENCES ewaste_submissions (id) ON DELETE SET NULL,
        CONSTRAINT fk_elog_tpl FOREIGN KEY (template_id) REFERENCES email_templates (id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """, commit=True)

    print("[4/4] Seeding initial default email templates...")
    DEFAULT_TEMPLATES = [
        # Template 1: SGT Student - Submission Received
        {
            'template_key': 'sub_received_sgt',
            'template_name': 'SGT University Student - Submission Received',
            'user_category': 'sgt_student',
            'email_type': 'submission_received',
            'subject': 'EcoLocate: E-Waste Submission Received [{{submission_id}}] - SGT University',
            'heading': 'E-Waste Collection Request Received',
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'Thank you for submitting your e-waste collection request through EcoLocate. Your request has been successfully received. Our team will review your submission and notify you once your request is confirmed.',
            'body': 'We appreciate your dedication to sustainable campus operations at SGT University! Your e-waste submission has been registered with reference ID {{submission_id}}. Our verification team will review your item list ({{waste_category}}, total quantity: {{total_quantity}} items) and arrange safe collection at your campus address.',
            'additional_instructions': 'Please keep your items boxed or securely gathered in your room/hostel. If security gate clearance is needed, our coordinator will contact {{phone_number}} before visiting.',
            'closing_message': 'Warm regards,\nEcoLocate Green Campus Initiative\nSGT University Environmental Cell',
            'sender_display_name': 'EcoLocate (SGT Campus Support)'
        },
        # Template 2: General User - Submission Received
        {
            'template_key': 'sub_received_general',
            'template_name': 'General User - Submission Received',
            'user_category': 'general_user',
            'email_type': 'submission_received',
            'subject': 'EcoLocate: E-Waste Collection Request Received [{{submission_id}}]',
            'heading': 'Thank You for Choosing Responsible E-Waste Recycling',
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'Thank you for submitting your e-waste collection request through EcoLocate. Your request has been successfully received. Our team will review your submission and notify you once your request is confirmed.',
            'body': 'Your e-waste collection request has been recorded in the EcoLocate directory under reference ID {{submission_id}}. Submitted items: {{waste_category}} ({{total_quantity}} items). Diverting electronic waste from municipal landfills protects groundwater from heavy metal contamination.',
            'additional_instructions': 'Ensure all personal accounts and storage data have been wiped from electronic devices prior to collection.',
            'closing_message': 'Best regards,\nThe EcoLocate Logistics Team',
            'sender_display_name': 'EcoLocate Support'
        },
        # Template 3: SGT Student - Request Confirmed
        {
            'template_key': 'req_confirmed_sgt',
            'template_name': 'SGT University Student - Request Confirmed',
            'user_category': 'sgt_student',
            'email_type': 'request_confirmed',
            'subject': 'EcoLocate: E-Waste Collection Request Confirmed [{{submission_id}}] - SGT University',
            'heading': 'Your E-Waste Collection Request is Confirmed!',
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'Your e-waste collection request has been reviewed and confirmed by the EcoLocate team. Thank you for contributing towards responsible e-waste management. Our team will contact you regarding the next steps.',
            'body': 'Your e-waste collection request {{submission_id}} (Roll No: {{roll_number}}) has been approved by administrator {{admin_name}}. Total verified items: {{total_quantity}}. Eligible EcoLocate points will be credited to your student points wallet upon physical collection.',
            'additional_instructions': 'Our on-campus collection representative will contact your phone number ({{phone_number}}) to schedule the exact handoff time.',
            'closing_message': 'Warm regards,\nEcoLocate Team & SGT University Campus Administration',
            'sender_display_name': 'EcoLocate Operations'
        },
        # Template 4: General User - Request Confirmed
        {
            'template_key': 'req_confirmed_general',
            'template_name': 'General User - Request Confirmed',
            'user_category': 'general_user',
            'email_type': 'request_confirmed',
            'subject': 'EcoLocate: Collection Request Confirmed [{{submission_id}}]',
            'heading': 'Your E-Waste Collection Request is Confirmed!',
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'Your e-waste collection request has been reviewed and confirmed by the EcoLocate team. Thank you for contributing towards responsible e-waste management. Our team will contact you regarding the next steps.',
            'body': 'Your collection request {{submission_id}} has been reviewed and confirmed by our logistics administrator {{admin_name}}. A certified recycling partner has been assigned to coordinate pickup for {{total_quantity}} item(s) from your provided address.',
            'additional_instructions': 'Please ensure your items are ready for collection. Our logistics driver will call {{phone_number}} before arrival.',
            'closing_message': 'Best regards,\nThe EcoLocate Operations Team',
            'sender_display_name': 'EcoLocate Operations'
        }
    ]

    for tpl in DEFAULT_TEMPLATES:
        existing = execute_query("SELECT id FROM email_templates WHERE template_key = %s", (tpl['template_key'],), fetchone=True)
        if not existing:
            print(f"  -> Seeding template '{tpl['template_key']}' ({tpl['template_name']})...")
            execute_query("""
            INSERT INTO email_templates (
                template_key, template_name, user_category, email_type,
                subject, heading, greeting, confirmation_message,
                body, additional_instructions, closing_message, sender_display_name, is_active
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, 1
            )
            """, (
                tpl['template_key'], tpl['template_name'], tpl['user_category'], tpl['email_type'],
                tpl['subject'], tpl['heading'], tpl['greeting'], tpl['confirmation_message'],
                tpl['body'], tpl['additional_instructions'], tpl['closing_message'], tpl['sender_display_name']
            ), commit=True)
        else:
            print(f"  -> Template '{tpl['template_key']}' already exists.")

    print("\n[SUCCESS] Email notification system database setup completed successfully.")

if __name__ == '__main__':
    run_email_migration()
