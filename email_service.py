"""
Email Notification & Template Management Service for EcoLocate
Handles template retrieval, dynamic variable substitution, mobile-responsive
HTML email rendering, SMTP delivery with defensive error handling,
email logging, and failed email retries.
"""

import os
import smtplib
import re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from flask import current_app
from config import Config
from db import execute_query

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# Canonical default template definitions for restoration
DEFAULT_TEMPLATE_DEFINITIONS = {
    'sub_received_sgt': {
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
    'sub_received_general': {
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
    'req_confirmed_sgt': {
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
    'req_confirmed_general': {
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
}


def substitute_variables(text, context):
    """
    Replace dynamic placeholders like {{user_name}}, {{submission_id}}, etc.
    with corresponding values from context dictionary.
    """
    if not text:
        return ""
    result = str(text)
    for key, value in context.items():
        val_str = str(value) if value is not None else ""
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, val_str)
    return result


def build_full_email_html(fields, context):
    """
    Assemble a responsive, professional HTML email layout with EcoLocate branding.
    fields dict contains: heading, greeting, confirmation_message, body,
    additional_instructions, closing_message, sender_display_name.
    """
    heading = fields.get('heading', 'EcoLocate Notification')
    greeting = fields.get('greeting', '')
    confirmation_msg = fields.get('confirmation_message', '')
    body = fields.get('body', '')
    instructions = fields.get('additional_instructions', '')
    closing = fields.get('closing_message', 'Best regards,\nEcoLocate Team')
    submission_id = context.get('submission_id', 'N/A')
    submission_date = context.get('submission_date', '')
    waste_category = context.get('waste_category', 'E-Waste Items')
    total_quantity = context.get('total_quantity', '1')

    # Convert newlines to HTML breaks in body and closing
    body_html = body.replace('\n', '<br>')
    closing_html = closing.replace('\n', '<br>')
    instructions_html = instructions.replace('\n', '<br>') if instructions else ''

    instructions_section = ""
    if instructions_html.strip():
        instructions_section = f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 20px 0; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px;">
          <tr>
            <td style="padding: 16px;">
              <strong style="color: #065f46; font-size: 14px;">Important Instructions:</strong>
              <div style="color: #047857; font-size: 13px; line-height: 1.6; margin-top: 6px;">
                {instructions_html}
              </div>
            </td>
          </tr>
        </table>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{heading}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 24px 12px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
          
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0e3b2e 0%, #155e46 100%); padding: 28px 24px; text-align: center;">
              <table role="presentation" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                <tr>
                  <td style="vertical-align: middle; padding-right: 10px;">
                    <span style="display: inline-block; background-color: #10b981; color: #ffffff; font-weight: 800; font-size: 18px; width: 34px; height: 34px; line-height: 34px; text-align: center; border-radius: 8px;">♻</span>
                  </td>
                  <td style="vertical-align: middle;">
                    <span style="color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: -0.02em;">Eco<span style="color: #34d399;">Locate</span></span>
                  </td>
                </tr>
              </table>
              <div style="color: #d1fae5; font-size: 13px; margin-top: 6px; letter-spacing: 0.02em;">
                Responsible Electronic Waste Recycling Initiative
              </div>
            </td>
          </tr>

          <!-- Heading Block -->
          <tr>
            <td style="padding: 24px 28px 12px 28px;">
              <h1 style="color: #0e3b2e; font-size: 20px; font-weight: 800; margin: 0 0 12px 0; line-height: 1.4;">
                {heading}
              </h1>
              <p style="color: #374151; font-size: 15px; margin: 0 0 14px 0; font-weight: 600;">
                {greeting}
              </p>
              <div style="background-color: #f8fafc; border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 0 6px 6px 0; color: #1e293b; font-size: 14px; line-height: 1.6; margin-bottom: 18px;">
                {confirmation_msg}
              </div>
            </td>
          </tr>

          <!-- Summary Pill Table -->
          <tr>
            <td style="padding: 0 28px 16px 28px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px;">
                <tr>
                  <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; color: #6b7280; width: 40%;"><strong>Reference ID:</strong></td>
                  <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; color: #047857; font-weight: 700;">{submission_id}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; color: #6b7280;"><strong>Item Categories:</strong></td>
                  <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; color: #111827;">{waste_category}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; color: #6b7280;"><strong>Total Items:</strong></td>
                  <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; color: #111827; font-weight: 600;">{total_quantity} item(s)</td>
                </tr>
                <tr>
                  <td style="padding: 10px 14px; color: #6b7280;"><strong>Submission Date:</strong></td>
                  <td style="padding: 10px 14px; color: #111827;">{submission_date}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body Content -->
          <tr>
            <td style="padding: 0 28px 18px 28px; color: #374151; font-size: 14px; line-height: 1.7;">
              {body_html}
              {instructions_section}
            </td>
          </tr>

          <!-- Closing Block -->
          <tr>
            <td style="padding: 0 28px 28px 28px; color: #4b5563; font-size: 14px; line-height: 1.6;">
              {closing_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #f9fafb; border-top: 1px solid #e5e7eb; padding: 18px 24px; text-align: center; color: #9ca3af; font-size: 12px; line-height: 1.5;">
              This is an automated notification regarding your e-waste collection request.<br>
              &copy; 2026 EcoLocate &bull; Dedicated to a Zero-Landfill Electronic Future.
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    # Plain text fallback
    plain_text = f"""{heading}

{greeting}

{confirmation_msg}

Reference ID: {submission_id}
Item Categories: {waste_category}
Total Quantity: {total_quantity}
Date: {submission_date}

{body}

{instructions if instructions else ''}

{closing}

---
EcoLocate - Responsible E-Waste Management Platform
"""
    return html, plain_text


def send_email_via_smtp(to_email, subject, html_body, plain_text=None, sender_display_name="EcoLocate Support"):
    """
    Transmit email message through configured SMTP server.
    Handles authentication, TLS handshake, timeouts, and connection errors.
    Returns (success: bool, status_message: str).
    """
    if not to_email or not EMAIL_REGEX.match(str(to_email).strip()):
        return False, f"Invalid or empty recipient email: {to_email}"

    to_email = str(to_email).strip()

    # If running in Flask testing mode, return simulated success without actual SMTP network call
    is_testing = False
    try:
        if current_app and current_app.config.get('TESTING'):
            is_testing = True
    except RuntimeError:
        pass

    # Check for test force-fail flag if used in unit tests
    if is_testing:
        if getattr(Config, 'SIMULATE_SMTP_FAILURE', False):
            return False, "Simulated SMTP failure in test mode"
        return True, "Sent"

    # Read SMTP credentials safely from Config / environment
    smtp_host = os.environ.get('SMTP_HOST') or getattr(Config, 'SMTP_HOST', '')
    smtp_port = int(os.environ.get('SMTP_PORT') or getattr(Config, 'SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USERNAME') or getattr(Config, 'SMTP_USERNAME', '')
    smtp_pass = os.environ.get('SMTP_PASSWORD') or getattr(Config, 'SMTP_PASSWORD', '')

    use_tls_env = os.environ.get('SMTP_USE_TLS')
    if use_tls_env is not None:
        use_tls = str(use_tls_env).strip().lower() in ('true', '1', 'yes')
    else:
        use_tls = getattr(Config, 'SMTP_USE_TLS', True)

    default_sender = os.environ.get('MAIL_DEFAULT_SENDER') or getattr(Config, 'MAIL_DEFAULT_SENDER', '')
    sender_name_env = os.environ.get('MAIL_SENDER_NAME') or getattr(Config, 'MAIL_SENDER_NAME', 'EcoLocate Team')

    if not smtp_host:
        return False, "SMTP server not configured (SMTP_HOST is empty in .env)"

    # Format From header with EcoLocate Team sender name
    parsed_name, parsed_email = parseaddr(default_sender)
    from_email = parsed_email if parsed_email else (smtp_user or "noreply@ecolocate.in")
    effective_name = sender_name_env or sender_display_name or parsed_name or "EcoLocate Team"
    sender_header = formataddr((effective_name, from_email))

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_header
    msg['To'] = to_email

    if plain_text:
        msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)

        # Envelope sender should be clean email address (from_email)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        return True, "Sent"

    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP Authentication failed: {e.smtp_error.decode() if hasattr(e, 'smtp_error') else str(e)}"
    except smtplib.SMTPConnectError as e:
        return False, f"SMTP Connection error: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"SMTP protocol error: {str(e)}"
    except TimeoutError:
        return False, "SMTP connection timed out after 10 seconds"
    except Exception as e:
        return False, f"Email delivery error: {str(e)}"


def get_template_for_submission(user_category, email_type):
    """
    Fetch the active email template matching user_category and email_type.
    Falls back to default definition if not found in database.
    """
    tpl = execute_query(
        """
        SELECT * FROM email_templates
        WHERE user_category = %s AND email_type = %s AND is_active = 1
        LIMIT 1
        """,
        (user_category, email_type),
        fetchone=True
    )
    if tpl:
        return tpl

    # Fallback to defaults
    target_key = f"{'sub_received' if email_type == 'submission_received' else 'req_confirmed'}_{'sgt' if user_category == 'sgt_student' else 'general'}"
    return DEFAULT_TEMPLATE_DEFINITIONS.get(target_key)


def build_submission_context(submission, admin_name="EcoLocate Admin"):
    """
    Extract dynamic placeholders from submission record and its items.
    """
    sub_id = submission.get('id')

    # Aggregate item categories and quantity
    items = execute_query(
        "SELECT category, submitted_quantity, accepted_quantity FROM ewaste_submission_items WHERE submission_id = %s",
        (sub_id,),
        fetchall=True
    ) or []

    categories = list(dict.fromkeys(i['category'] for i in items if i.get('category')))
    waste_category_str = ", ".join(categories) if categories else "General Electronic Waste"
    
    total_qty = submission.get('total_accepted_items') or submission.get('total_submitted_items') or sum(i.get('submitted_quantity', 1) for i in items) or 1

    created_at = submission.get('created_at')
    if isinstance(created_at, datetime):
        date_str = created_at.strftime('%d %B %Y, %I:%M %p')
    else:
        date_str = str(created_at) if created_at else datetime.now().strftime('%d %B %Y')

    user_name = submission.get('student_name') if submission.get('is_student') and submission.get('student_name') else submission.get('full_name', 'Valued User')
    uni_name = submission.get('university_name') or submission.get('university_type') or "SGT University"

    return {
        'user_name': user_name,
        'user_email': submission.get('email', ''),
        'phone_number': submission.get('phone_number', ''),
        'university_name': uni_name,
        'roll_number': submission.get('roll_number', 'N/A') or 'N/A',
        'submission_id': submission.get('submission_code', f"SUB-{sub_id}"),
        'submission_date': date_str,
        'waste_category': waste_category_str,
        'total_quantity': total_qty,
        'submission_status': (submission.get('status') or 'Pending').capitalize(),
        'admin_name': admin_name or 'EcoLocate Administrator'
    }


def send_submission_email(submission_id, email_type='submission_received', admin_name="EcoLocate Admin", force_resend=False):
    """
    Automated email dispatcher for submission events:
    - 'submission_received': Sent when form is submitted
    - 'request_confirmed': Sent when admin confirms request

    Selects SGT Student vs General User template independently.
    Replaces all dynamic variables.
    Sends email and records attempt in email_logs.
    Returns (success: bool, message: str, log_id: int).
    """
    submission = execute_query(
        "SELECT * FROM ewaste_submissions WHERE id = %s",
        (submission_id,),
        fetchone=True
    )
    if not submission:
        return False, f"Submission #{submission_id} not found.", None

    recipient_email = (submission.get('email') or '').strip()
    if not recipient_email or not EMAIL_REGEX.match(recipient_email):
        # Gracefully handle missing or invalid email address
        return False, "No valid recipient email address provided in submission.", None

    # Check for duplicate prevention if not force_resend
    if not force_resend:
        already_sent = execute_query(
            """
            SELECT id FROM email_logs
            WHERE submission_id = %s AND email_type = %s AND status = 'Sent'
            LIMIT 1
            """,
            (submission_id, email_type),
            fetchone=True
        )
        if already_sent:
            return False, f"Email of type '{email_type}' has already been successfully sent for submission #{submission_id}.", already_sent['id']

    # Determine user category
    is_student = bool(submission.get('is_student'))
    uni_type = (submission.get('university_type') or '').strip()
    uni_name = (submission.get('university_name') or '').strip()
    
    if is_student and ('SGT University' in uni_type or 'SGT University' in uni_name):
        user_category = 'sgt_student'
    else:
        user_category = 'general_user'

    # Retrieve template
    tpl = get_template_for_submission(user_category, email_type)
    if not tpl:
        return False, f"No email template found for {user_category} / {email_type}.", None

    # Build context
    context = build_submission_context(submission, admin_name=admin_name)

    # Render dynamic placeholders
    rendered_fields = {
        'heading': substitute_variables(tpl['heading'], context),
        'greeting': substitute_variables(tpl['greeting'], context),
        'confirmation_message': substitute_variables(tpl['confirmation_message'], context),
        'body': substitute_variables(tpl['body'], context),
        'additional_instructions': substitute_variables(tpl.get('additional_instructions') or '', context),
        'closing_message': substitute_variables(tpl['closing_message'], context),
        'sender_display_name': substitute_variables(tpl.get('sender_display_name') or 'EcoLocate Support', context)
    }
    rendered_subject = substitute_variables(tpl['subject'], context)

    html_content, plain_content = build_full_email_html(rendered_fields, context)

    # Attempt SMTP dispatch
    success, status_msg = send_email_via_smtp(
        to_email=recipient_email,
        subject=rendered_subject,
        html_body=html_content,
        plain_text=plain_content,
        sender_display_name=rendered_fields['sender_display_name']
    )

    log_status = 'Sent' if success else 'Failed'
    err_detail = None if success else status_msg
    tpl_id = tpl.get('id')

    # Record in email_logs
    log_id = execute_query(
        """
        INSERT INTO email_logs (
            submission_id, recipient_email, recipient_name, user_category,
            email_type, template_id, subject, status, error_message,
            attempt_count, sent_at
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            1, CASE WHEN %s = 'Sent' THEN NOW() ELSE NULL END
        )
        """,
        (
            submission_id, recipient_email, context['user_name'], user_category,
            email_type, tpl_id, rendered_subject, log_status, err_detail,
            log_status
        ),
        commit=True
    )

    return success, status_msg, log_id


def retry_failed_email_log(log_id):
    """
    Retry sending a previously failed or pending email from email_logs.
    """
    log = execute_query("SELECT * FROM email_logs WHERE id = %s", (log_id,), fetchone=True)
    if not log:
        return False, "Email log record not found."

    submission_id = log.get('submission_id')
    if not submission_id:
        return False, "Cannot retry log record without associated submission ID."

    submission = execute_query("SELECT * FROM ewaste_submissions WHERE id = %s", (submission_id,), fetchone=True)
    if not submission:
        return False, f"Associated submission #{submission_id} no longer exists."

    # Dispatch email with force_resend=True
    success, status_msg, new_log_id = send_submission_email(
        submission_id=submission_id,
        email_type=log['email_type'],
        force_resend=True
    )

    # Increment attempt count on original log or update it
    execute_query(
        """
        UPDATE email_logs
        SET attempt_count = attempt_count + 1,
            status = %s,
            error_message = %s,
            sent_at = CASE WHEN %s = 'Sent' THEN NOW() ELSE sent_at END
        WHERE id = %s
        """,
        (
            'Sent' if success else 'Failed',
            None if success else status_msg,
            'Sent' if success else 'Failed',
            log_id
        ),
        commit=True
    )

    return success, status_msg


def restore_default_template_definition(template_key):
    """
    Restore an email template to its factory default content.
    """
    default_def = DEFAULT_TEMPLATE_DEFINITIONS.get(template_key)
    if not default_def:
        return False, f"No default definition exists for template key '{template_key}'."

    execute_query(
        """
        UPDATE email_templates
        SET subject = %s,
            heading = %s,
            greeting = %s,
            confirmation_message = %s,
            body = %s,
            additional_instructions = %s,
            closing_message = %s,
            sender_display_name = %s,
            is_active = 1
        WHERE template_key = %s
        """,
        (
            default_def['subject'],
            default_def['heading'],
            default_def['greeting'],
            default_def['confirmation_message'],
            default_def['body'],
            default_def['additional_instructions'],
            default_def['closing_message'],
            default_def['sender_display_name'],
            template_key
        ),
        commit=True
    )
    return True, f"Template '{template_key}' restored to default content."
