"""
EcoLocate - E-Waste Submission & Points Module
Handles user-facing e-waste submissions (student and non-student),
image upload validation, multi-item processing, tracking views,
and user points wallet ledger displays.
"""

import os
import re
import uuid
from functools import wraps
from flask import (
    request, render_template, redirect, url_for,
    flash, session, jsonify, current_app
)
from werkzeug.utils import secure_filename
from db import execute_query, log_user_activity
from points_service import (
    calculate_points_for_quantity, get_or_create_wallet,
    get_wallet_ledger, get_active_points_tiers
)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

CATEGORIES = [
    "Mobile phones",
    "Laptops",
    "Desktops",
    "Batteries",
    "Chargers and cables",
    "Keyboard and mouse",
    "Printers",
    "TVs",
    "Electronic components",
    "Other electronic waste"
]

CONDITIONS = ["Working", "Not Working", "Damaged", "Unknown"]


def allowed_file(filename):
    """Check if the uploaded file has an approved image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_submission_code():
    """Generate a unique tracking code like SUB-2026-A1B2C."""
    while True:
        token = uuid.uuid4().hex[:6].upper()
        code = f"SUB-2026-{token}"
        existing = execute_query(
            "SELECT id FROM ewaste_submissions WHERE submission_code = %s",
            (code,),
            fetchone=True
        )
        if not existing:
            return code


def login_required(f):
    """Decorator to require standard user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please sign in to access your e-waste submissions and points wallet.', 'error')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def register_submission_routes(app):
    """Register all public and user-facing submission and points routes."""

    @app.route('/submit-ewaste', methods=['GET', 'POST'])
    def submit_ewaste():
        """
        Public / User E-Waste Submission Form.
        Accessible to everyone (SGT University students, other universities, and general public).
        Supports multiple waste items, image uploads, and collection address.
        """
        user_id = session.get('user_id')
        user_prefill = {}
        if user_id:
            user = execute_query(
                "SELECT id, full_name, email FROM users WHERE id = %s",
                (user_id,),
                fetchone=True
            )
            if user:
                user_prefill = user

        if request.method == 'POST':
            # Form data extraction
            is_student_val = request.form.get('is_student', 'no').strip().lower()
            is_student = 1 if is_student_val in ('yes', '1', 'true') else 0

            if is_student:
                student_name = request.form.get('student_name', '').strip()
                university_type = request.form.get('university_type', 'SGT University').strip()
                if university_type == 'Other University' or university_type == 'Other':
                    university_name = request.form.get('university_name_other', '').strip()
                else:
                    university_name = "SGT University"
                roll_number = request.form.get('roll_number', '').strip() or None
                course_dept = request.form.get('course_dept', '').strip() or None
                phone_number = request.form.get('phone_number', '').strip()
                email = request.form.get('email', '').strip() or None
                full_name = student_name

                if not student_name:
                    flash('Please enter the student name.', 'error')
                    return render_template(
                        'submit_ewaste.html',
                        categories=CATEGORIES,
                        conditions=CONDITIONS,
                        user_prefill=user_prefill,
                        form_data=request.form
                    ), 400

                if (university_type in ('Other University', 'Other')) and not university_name:
                    flash('Please specify your university name.', 'error')
                    return render_template(
                        'submit_ewaste.html',
                        categories=CATEGORIES,
                        conditions=CONDITIONS,
                        user_prefill=user_prefill,
                        form_data=request.form
                    ), 400
            else:
                full_name = request.form.get('full_name', '').strip()
                student_name = None
                university_type = None
                university_name = None
                roll_number = None
                course_dept = None
                phone_number = request.form.get('phone_number', '').strip()
                email = request.form.get('email', '').strip() or None

                if not full_name:
                    flash('Please enter your full name.', 'error')
                    return render_template(
                        'submit_ewaste.html',
                        categories=CATEGORIES,
                        conditions=CONDITIONS,
                        user_prefill=user_prefill,
                        form_data=request.form
                    ), 400

            # Validate phone number
            clean_phone = re.sub(r'[\s\-+()]', '', phone_number)
            if not clean_phone or len(clean_phone) < 7:
                flash('Please enter a valid contact phone number.', 'error')
                return render_template(
                    'submit_ewaste.html',
                    categories=CATEGORIES,
                    conditions=CONDITIONS,
                    user_prefill=user_prefill,
                    form_data=request.form
                ), 400

            # Address fields
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            additional_message = request.form.get('additional_message', '').strip() or None

            if not address or not city or not state or not pincode:
                flash('Please fill in complete collection address details (Address, City, State, PIN code).', 'error')
                return render_template(
                    'submit_ewaste.html',
                    categories=CATEGORIES,
                    conditions=CONDITIONS,
                    user_prefill=user_prefill,
                    form_data=request.form
                ), 400

            # Extract dynamic multi-items
            cat_list = request.form.getlist('item_category[]') or request.form.getlist('item_category')
            name_list = request.form.getlist('item_name[]') or request.form.getlist('item_name')
            qty_list = request.form.getlist('item_quantity[]') or request.form.getlist('item_quantity')
            weight_list = request.form.getlist('item_weight[]') or request.form.getlist('item_weight')
            cond_list = request.form.getlist('item_condition[]') or request.form.getlist('item_condition')

            if not cat_list or not name_list or len(cat_list) == 0:
                flash('Please add at least one e-waste item for submission.', 'error')
                return render_template(
                    'submit_ewaste.html',
                    categories=CATEGORIES,
                    conditions=CONDITIONS,
                    user_prefill=user_prefill,
                    form_data=request.form
                ), 400

            items_to_insert = []
            total_submitted_quantity = 0
            total_estimated_weight = 0.0

            for i in range(len(cat_list)):
                cat = cat_list[i].strip() if i < len(cat_list) else "Other electronic waste"
                name = name_list[i].strip() if i < len(name_list) else ""
                if not name:
                    continue  # skip blank entries

                try:
                    qty = int(qty_list[i]) if i < len(qty_list) else 1
                    if qty < 1:
                        qty = 1
                except (ValueError, TypeError):
                    qty = 1

                try:
                    wt = float(weight_list[i]) if i < len(weight_list) and weight_list[i].strip() else None
                    if wt and wt > 0:
                        total_estimated_weight += wt
                except (ValueError, TypeError):
                    wt = None

                cond = cond_list[i].strip() if i < len(cond_list) else "Unknown"
                if cond not in CONDITIONS:
                    cond = "Unknown"

                total_submitted_quantity += qty
                items_to_insert.append({
                    'category': cat,
                    'item_name': name,
                    'quantity': qty,
                    'weight_kg': wt,
                    'condition_state': cond
                })

            if not items_to_insert:
                flash('Please provide valid details for at least one e-waste item.', 'error')
                return render_template(
                    'submit_ewaste.html',
                    categories=CATEGORIES,
                    conditions=CONDITIONS,
                    user_prefill=user_prefill,
                    form_data=request.form
                ), 400

            # Calculate preliminary points estimate based on active tiers
            estimated_points = calculate_points_for_quantity(total_submitted_quantity)

            # Generate unique submission code
            submission_code = generate_submission_code()

            try:
                # Insert master submission record
                sub_id = execute_query(
                    """
                    INSERT INTO ewaste_submissions (
                        submission_code, user_id, is_student, student_name,
                        university_type, university_name, roll_number, course_dept,
                        full_name, phone_number, email, address, city, state, pincode,
                        additional_message, status, total_submitted_items, total_accepted_items,
                        estimated_weight_kg, points_calculated, points_awarded, points_approved
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, 'pending', %s, 0,
                        %s, %s, 0, 0
                    )
                    """,
                    (
                        submission_code, user_id, is_student, student_name,
                        university_type, university_name, roll_number, course_dept,
                        full_name, phone_number, email, address, city, state, pincode,
                        additional_message, total_submitted_quantity,
                        total_estimated_weight if total_estimated_weight > 0 else None,
                        estimated_points
                    ),
                    commit=True
                )

                # Insert items
                for item in items_to_insert:
                    execute_query(
                        """
                        INSERT INTO ewaste_submission_items (
                            submission_id, category, item_name, submitted_quantity,
                            accepted_quantity, weight_kg, condition_state, status
                        ) VALUES (
                            %s, %s, %s, %s,
                            0, %s, %s, 'pending'
                        )
                        """,
                        (
                            sub_id, item['category'], item['item_name'], item['quantity'],
                            item['weight_kg'], item['condition_state']
                        ),
                        commit=True
                    )

                # Process file uploads (item images)
                upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'submissions')
                os.makedirs(upload_folder, exist_ok=True)

                uploaded_files = request.files.getlist('item_images[]') or request.files.getlist('item_images') or request.files.getlist('images')
                for file_obj in uploaded_files:
                    if file_obj and file_obj.filename and allowed_file(file_obj.filename):
                        # Verify file size
                        file_obj.seek(0, os.SEEK_END)
                        size = file_obj.tell()
                        file_obj.seek(0)
                        if size > MAX_FILE_SIZE:
                            continue  # skip files over 5MB

                        orig_name = secure_filename(file_obj.filename)
                        ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'jpg'
                        unique_filename = f"{submission_code}_{uuid.uuid4().hex[:8]}.{ext}"
                        save_path = os.path.join(upload_folder, unique_filename)
                        file_obj.save(save_path)

                        rel_path = f"uploads/submissions/{unique_filename}"
                        execute_query(
                            """
                            INSERT INTO ewaste_submission_images (
                                submission_id, file_path, original_filename, file_size
                            ) VALUES (%s, %s, %s, %s)
                            """,
                            (sub_id, rel_path, orig_name, size),
                            commit=True
                        )

                # Ensure wallet exists for registered user
                if user_id:
                    get_or_create_wallet(user_id)

                flash(
                    f"E-Waste submission received successfully! Your tracking code is {submission_code}. "
                    f"Points will be credited to your account upon verification by our team.",
                    "success"
                )
                return redirect(url_for('submission_detail', submission_code=submission_code))

            except Exception as e:
                app.logger.error(f"E-waste submission error: {e}")
                flash("An unexpected error occurred while saving your submission. Please try again.", "error")
                return render_template(
                    'submit_ewaste.html',
                    categories=CATEGORIES,
                    conditions=CONDITIONS,
                    user_prefill=user_prefill,
                    form_data=request.form
                ), 500

        return render_template(
            'submit_ewaste.html',
            categories=CATEGORIES,
            conditions=CONDITIONS,
            user_prefill=user_prefill
        )

    @app.route('/submission/<submission_code>')
    def submission_detail(submission_code):
        """
        Public / User Submission Tracking Page.
        Displays real-time status of submission, items verification, and points awarded.
        """
        sub = execute_query(
            """
            SELECT s.*, r.name AS recycler_name, r.contact_phone AS recycler_phone,
                   r.collection_status AS recycler_collection_status
            FROM ewaste_submissions s
            LEFT JOIN recyclers r ON s.recycler_id = r.id
            WHERE s.submission_code = %s
            """,
            (submission_code,),
            fetchone=True
        )
        if not sub:
            flash(f"Submission with tracking code '{submission_code}' was not found.", "error")
            return redirect(url_for('submit_ewaste'))

        items = execute_query(
            "SELECT * FROM ewaste_submission_items WHERE submission_id = %s ORDER BY id ASC",
            (sub['id'],),
            fetchall=True
        ) or []

        images = execute_query(
            "SELECT * FROM ewaste_submission_images WHERE submission_id = %s ORDER BY id ASC",
            (sub['id'],),
            fetchall=True
        ) or []

        return render_template(
            'submission_detail.html',
            submission=sub,
            items=items,
            images=images
        )

    @app.route('/my-submissions')
    @login_required
    def my_submissions():
        """List of all e-waste submissions submitted by the logged-in user."""
        user_id = session.get('user_id')
        submissions = execute_query(
            """
            SELECT s.*, 
                   COUNT(i.id) AS item_count,
                   COALESCE(SUM(i.accepted_quantity), 0) AS total_accepted_qty
            FROM ewaste_submissions s
            LEFT JOIN ewaste_submission_items i ON s.id = i.submission_id
            WHERE s.user_id = %s
            GROUP BY s.id
            ORDER BY s.created_at DESC
            """,
            (user_id,),
            fetchall=True
        ) or []

        wallet = get_or_create_wallet(user_id)

        return render_template(
            'my_submissions.html',
            submissions=submissions,
            wallet=wallet
        )

    @app.route('/my-points')
    @login_required
    def my_points():
        """
        Points Wallet page for logged-in user.
        Shows balance, breakdown of repeat submission points earned,
        active points tiers structure, and complete transaction ledger.
        """
        user_id = session.get('user_id')
        wallet = get_or_create_wallet(user_id)
        ledger = get_wallet_ledger(user_id)
        tiers = get_active_points_tiers()

        # Count total approved submissions for this user
        sub_stats = execute_query(
            """
            SELECT 
                COUNT(*) AS total_submissions,
                COALESCE(SUM(CASE WHEN points_approved = 1 THEN 1 ELSE 0 END), 0) AS verified_submissions,
                COALESCE(SUM(points_awarded), 0) AS lifetime_submission_points
            FROM ewaste_submissions
            WHERE user_id = %s
            """,
            (user_id,),
            fetchone=True
        )

        return render_template(
            'my_points.html',
            wallet=wallet,
            ledger=ledger,
            tiers=tiers,
            sub_stats=sub_stats or {}
        )
