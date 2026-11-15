"""
EcoLocate - Phase 7 Admin Management Module
Contains all administration routes, CSV batch ingestion, facility CRUD,
user moderation, device management, and executive analytics.
"""

import os
import io
import csv
import json
import uuid
from functools import wraps
from flask import (
    request, render_template, redirect, url_for,
    flash, session, jsonify, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query, check_db_health

# Temporary memory cache for staged CSV previews (token -> list of row dicts)
_CSV_STAGING_CACHE = {}


def admin_required(f):
    """Decorator to enforce active administrator session on protected endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Administrative access required. Please sign in.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def clean_str(val):
    """Normalize string, stripping whitespace and returning None for empty strings."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def clean_coord(val, min_val, max_val):
    """Parse and validate decimal coordinate within min/max bounds."""
    if val is None or str(val).strip() == '':
        return None
    try:
        f = float(val)
        if min_val <= f <= max_val:
            return round(f, 8)
    except (ValueError, TypeError):
        pass
    return None


def register_admin_routes(app):
    """Attach all Phase 7 administration routes to the Flask application."""

    # ==========================================================================
    # 1. Admin Authentication & Profile
    # ==========================================================================

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Separate administrator login with hashed password authentication."""
        if session.get('admin_id'):
            return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Please enter both administrator username and password.', 'error')
                return render_template('admin_login.html'), 400

            try:
                admin = execute_query(
                    "SELECT id, username, password_hash FROM admins WHERE username = %s",
                    (username,),
                    fetchone=True
                )

                if admin and check_password_hash(admin['password_hash'], password):
                    session['admin_id'] = admin['id']
                    session['admin_username'] = admin['username']
                    session.permanent = True

                    flash(f'Administrator session verified for {admin["username"]}.', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid administrator credentials. Access denied.', 'error')
                    return render_template('admin_login.html'), 401

            except Exception as e:
                app.logger.error(f"Admin login error: {e}")
                flash('Database error during administrative verification.', 'error')
                return render_template('admin_login.html'), 500

        return render_template('admin_login.html')

    @app.route('/admin/logout')
    def admin_logout():
        """Terminate administrator session."""
        session.pop('admin_id', None)
        session.pop('admin_username', None)
        flash('Administrator session terminated.', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin/profile', methods=['GET', 'POST'])
    @admin_required
    def admin_profile():
        """View administrator details and update admin credentials."""
        admin_id = session.get('admin_id')
        admin = execute_query(
            "SELECT id, username, created_at FROM admins WHERE id = %s",
            (admin_id,),
            fetchone=True
        )

        if not admin:
            flash('Admin account not found.', 'error')
            return redirect(url_for('admin_logout'))

        if request.method == 'POST':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            admin_auth = execute_query(
                "SELECT password_hash FROM admins WHERE id = %s",
                (admin_id,),
                fetchone=True
            )

            if not admin_auth or not check_password_hash(admin_auth['password_hash'], current_password):
                flash('Current password is incorrect. Verification failed.', 'error')
                return render_template('admin_profile.html', admin=admin), 400

            if len(new_password) < 8:
                flash('New password must be at least 8 characters long.', 'error')
                return render_template('admin_profile.html', admin=admin), 400

            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'error')
                return render_template('admin_profile.html', admin=admin), 400

            hashed = generate_password_hash(new_password)
            execute_query(
                "UPDATE admins SET password_hash = %s WHERE id = %s",
                (hashed, admin_id),
                commit=True
            )
            flash('Administrator password updated successfully.', 'success')
            return redirect(url_for('admin_profile'))

        return render_template('admin_profile.html', admin=admin)

    # ==========================================================================
    # 2. Executive Dashboard Overview
    # ==========================================================================

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        """Executive control dashboard with KPIs, Chart.js metrics, and recent activity."""
        try:
            centre_row = execute_query("SELECT COUNT(*) AS total FROM centres", fetchone=True)
            user_row = execute_query("SELECT COUNT(*) AS total FROM users", fetchone=True)
            active_users_row = execute_query("SELECT COUNT(*) AS total FROM users WHERE is_active = 1", fetchone=True)
            device_row = execute_query("SELECT COUNT(*) AS total FROM devices", fetchone=True)

            website_row = execute_query(
                "SELECT COUNT(*) AS total FROM centres WHERE website_url IS NOT NULL AND TRIM(website_url) != ''",
                fetchone=True
            )
            phone_row = execute_query(
                "SELECT COUNT(*) AS total FROM centres WHERE phone_number IS NOT NULL AND TRIM(phone_number) != ''",
                fetchone=True
            )
            coords_row = execute_query(
                "SELECT COUNT(*) AS total FROM centres WHERE latitude IS NOT NULL AND longitude IS NOT NULL",
                fetchone=True
            )

            # Chart 1: Top 6 States distribution
            top_states = execute_query(
                "SELECT state, COUNT(*) as count FROM centres GROUP BY state ORDER BY count DESC LIMIT 6",
                fetchall=True
            ) or []

            state_labels = [s['state'] for s in top_states]
            state_counts = [int(s['count']) for s in top_states]

            # Recent 5 centres added
            recent_centres = execute_query(
                "SELECT id, centre_name, state, city, capacity_mta, centre_type, created_at FROM centres ORDER BY id DESC LIMIT 5",
                fetchall=True
            ) or []

            # Recent 5 registered users
            recent_users = execute_query(
                "SELECT id, full_name, email, is_active, created_at FROM users ORDER BY id DESC LIMIT 5",
                fetchall=True
            ) or []

            return render_template(
                'admin_dashboard.html',
                centre_count=int(centre_row['total'] or 0),
                user_count=int(user_row['total'] or 0),
                active_users_count=int(active_users_row['total'] or 0) if active_users_row else 0,
                device_count=int(device_row['total'] or 0),
                website_count=int(website_row['total'] or 0) if website_row else 0,
                phone_count=int(phone_row['total'] or 0) if phone_row else 0,
                coords_count=int(coords_row['total'] or 0) if coords_row else 0,
                top_states=top_states,
                state_labels=state_labels,
                state_counts=state_counts,
                recent_centres=recent_centres,
                recent_users=recent_users
            )
        except Exception as e:
            app.logger.error(f"Error loading admin dashboard: {e}")
            flash('Error loading executive database metrics.', 'error')
            return render_template(
                'admin_dashboard.html',
                centre_count=0, user_count=0, active_users_count=0, device_count=0,
                website_count=0, phone_count=0, coords_count=0,
                top_states=[], state_labels=[], state_counts=[],
                recent_centres=[], recent_users=[]
            )

    # ==========================================================================
    # 3. Recycling Centre Management (CRUD, Search & Filters)
    # ==========================================================================

    @app.route('/admin/centres')
    @admin_required
    def admin_centres():
        """List, search, and filter all recycling facilities with pagination."""
        page = request.args.get('page', 1, type=int)
        limit = 15
        offset = (page - 1) * limit

        query_term = request.args.get('q', '').strip()
        state_filter = request.args.get('state', '').strip()
        city_filter = request.args.get('city', '').strip()

        # Fetch available states for dropdown
        states = execute_query(
            "SELECT state, COUNT(*) as count FROM centres GROUP BY state ORDER BY state ASC",
            fetchall=True
        ) or []

        where_clauses = []
        params = []

        if query_term:
            where_clauses.append("(centre_name LIKE %s OR address LIKE %s OR city LIKE %s)")
            like_term = f"%{query_term}%"
            params.extend([like_term, like_term, like_term])

        if state_filter:
            where_clauses.append("state = %s")
            params.append(state_filter)

        if city_filter:
            where_clauses.append("city LIKE %s")
            params.append(f"%{city_filter}%")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = f"SELECT COUNT(*) as total FROM centres {where_sql}"
        count_row = execute_query(count_sql, tuple(params), fetchone=True)
        total_count = int(count_row['total'] or 0) if count_row else 0
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1

        data_sql = f"""
        SELECT id, centre_name, state, city, address, capacity_mta, centre_type,
               website_url, website_verification, phone_number, email,
               latitude, longitude, created_at
        FROM centres
        {where_sql}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """
        data_params = list(params) + [limit, offset]
        centres = execute_query(data_sql, tuple(data_params), fetchall=True) or []

        return render_template(
            'admin_centres.html',
            centres=centres,
            states=states,
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            current_query=query_term,
            current_state=state_filter,
            current_city=city_filter
        )

    @app.route('/admin/centres/add', methods=['GET', 'POST'])
    @admin_required
    def admin_centres_add():
        """Add a new recycling facility with duplicate prevention."""
        if request.method == 'POST':
            name = clean_str(request.form.get('centre_name'))
            state = clean_str(request.form.get('state'))
            city = clean_str(request.form.get('city'))
            address = clean_str(request.form.get('address'))
            capacity = clean_str(request.form.get('capacity_mta'))
            centre_type = clean_str(request.form.get('centre_type')) or 'Authorised dismantler/recycler'
            source = clean_str(request.form.get('source')) or 'CPCB Authorised Recyclers'
            website = clean_str(request.form.get('website_url'))
            verification = clean_str(request.form.get('website_verification'))
            checked_date = clean_str(request.form.get('website_checked_date'))
            phone = clean_str(request.form.get('phone_number'))
            email = clean_str(request.form.get('email'))

            lat = clean_coord(request.form.get('latitude'), -90.0, 90.0)
            lng = clean_coord(request.form.get('longitude'), -180.0, 180.0)

            if not name or not state or not city or not address:
                flash('Facility Name, State, City, and Address are required.', 'error')
                return render_template('admin_centre_form.html', is_edit=False, centre=None), 400

            # Duplicate prevention check
            duplicate = execute_query(
                "SELECT id, centre_name FROM centres WHERE LOWER(TRIM(centre_name)) = LOWER(TRIM(%s)) AND LOWER(TRIM(address)) = LOWER(TRIM(%s))",
                (name, address),
                fetchone=True
            )
            if duplicate:
                flash(f"A recycling centre matching '{name}' at this exact address already exists (#ID {duplicate['id']}).", 'error')
                return render_template('admin_centre_form.html', is_edit=False, centre=None), 409

            insert_sql = """
            INSERT INTO centres (
                centre_name, state, city, address, capacity_mta, centre_type,
                source, website_url, website_verification, website_checked_date,
                phone_number, email, latitude, longitude
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            centre_id = execute_query(
                insert_sql,
                (name, state, city, address, capacity, centre_type,
                 source, website, verification, checked_date,
                 phone, email, lat, lng),
                commit=True
            )

            flash(f"Recycling centre '{name}' added successfully (#ID {centre_id}).", 'success')
            return redirect(url_for('admin_centres'))

        return render_template('admin_centre_form.html', is_edit=False, centre=None)

    @app.route('/admin/centres/edit/<int:centre_id>', methods=['GET', 'POST'])
    @admin_required
    def admin_centres_edit(centre_id):
        """Update existing recycling centre details."""
        centre = execute_query("SELECT * FROM centres WHERE id = %s", (centre_id,), fetchone=True)
        if not centre:
            flash('Recycling centre not found.', 'error')
            return redirect(url_for('admin_centres'))

        if request.method == 'POST':
            name = clean_str(request.form.get('centre_name'))
            state = clean_str(request.form.get('state'))
            city = clean_str(request.form.get('city'))
            address = clean_str(request.form.get('address'))
            capacity = clean_str(request.form.get('capacity_mta'))
            centre_type = clean_str(request.form.get('centre_type')) or 'Authorised dismantler/recycler'
            source = clean_str(request.form.get('source')) or 'CPCB Authorised Recyclers'
            website = clean_str(request.form.get('website_url'))
            verification = clean_str(request.form.get('website_verification'))
            checked_date = clean_str(request.form.get('website_checked_date'))
            phone = clean_str(request.form.get('phone_number'))
            email = clean_str(request.form.get('email'))

            lat = clean_coord(request.form.get('latitude'), -90.0, 90.0)
            lng = clean_coord(request.form.get('longitude'), -180.0, 180.0)

            if not name or not state or not city or not address:
                flash('Facility Name, State, City, and Address are required.', 'error')
                return render_template('admin_centre_form.html', is_edit=True, centre=centre), 400

            # Prevent duplicate with another record
            duplicate = execute_query(
                "SELECT id FROM centres WHERE LOWER(TRIM(centre_name)) = LOWER(TRIM(%s)) AND LOWER(TRIM(address)) = LOWER(TRIM(%s)) AND id != %s",
                (name, address, centre_id),
                fetchone=True
            )
            if duplicate:
                flash(f"Another facility with this name and address already exists (#ID {duplicate['id']}).", 'error')
                return render_template('admin_centre_form.html', is_edit=True, centre=centre), 409

            update_sql = """
            UPDATE centres SET
                centre_name = %s, state = %s, city = %s, address = %s,
                capacity_mta = %s, centre_type = %s, source = %s,
                website_url = %s, website_verification = %s, website_checked_date = %s,
                phone_number = %s, email = %s, latitude = %s, longitude = %s
            WHERE id = %s
            """
            execute_query(
                update_sql,
                (name, state, city, address, capacity, centre_type,
                 source, website, verification, checked_date,
                 phone, email, lat, lng, centre_id),
                commit=True
            )

            flash(f"Recycling centre '{name}' updated successfully.", 'success')
            return redirect(url_for('admin_centres'))

        return render_template('admin_centre_form.html', is_edit=True, centre=centre)

    @app.route('/admin/centres/view/<int:centre_id>')
    @admin_required
    def admin_centres_view(centre_id):
        """View full details and geospatial routing for a single centre."""
        centre = execute_query("SELECT * FROM centres WHERE id = %s", (centre_id,), fetchone=True)
        if not centre:
            flash('Recycling centre not found.', 'error')
            return redirect(url_for('admin_centres'))

        devices = execute_query(
            "SELECT d.device_name FROM centre_devices cd JOIN devices d ON cd.device_id = d.id WHERE cd.centre_id = %s",
            (centre_id,),
            fetchall=True
        ) or []
        accepted_devices = [d['device_name'] for d in devices]

        return render_template('admin_centre_detail.html', centre=centre, accepted_devices=accepted_devices)

    @app.route('/admin/centres/delete/<int:centre_id>', methods=['POST'])
    @admin_required
    def admin_centres_delete(centre_id):
        """Permanently delete a recycling centre with confirmation."""
        centre = execute_query("SELECT centre_name FROM centres WHERE id = %s", (centre_id,), fetchone=True)
        if not centre:
            flash('Facility not found or already removed.', 'error')
            return redirect(url_for('admin_centres'))

        execute_query("DELETE FROM centres WHERE id = %s", (centre_id,), commit=True)
        flash(f"Recycling centre '{centre['centre_name']}' has been permanently removed.", 'success')
        return redirect(url_for('admin_centres'))

    # ==========================================================================
    # 4. CSV Management (Upload, Schema Validation, Preview, Batch Ingestion)
    # ==========================================================================

    @app.route('/admin/centres/import-csv', methods=['GET', 'POST'])
    @admin_required
    def admin_csv_import():
        """Upload, validate, preview, and ingest recycling centres via CSV."""
        if request.method == 'POST':
            file = request.files.get('csv_file')
            preview_only = request.form.get('preview_only') == '1'

            if not file or not file.filename:
                flash('Please select a valid CSV file to upload.', 'error')
                return render_template('admin_csv_import.html')

            if not file.filename.lower().endswith('.csv'):
                flash('Only .csv files are supported for batch ingestion.', 'error')
                return render_template('admin_csv_import.html')

            try:
                # Read content safely as text (handles UTF-8 and BOM)
                content = file.stream.read().decode('utf-8-sig', errors='replace')
                reader = csv.DictReader(io.StringIO(content))

                headers = [h.strip().lower() for h in (reader.fieldnames or [])]
                
                # Check column mapping: must have name, state, city, address
                has_name = any(col in headers for col in ['name', 'centre_name'])
                has_state = any(col in headers for col in ['state', 'state_name'])
                has_city = any(col in headers for col in ['city_district', 'city'])
                has_addr = any(col in headers for col in ['address', 'facility_address'])

                if not (has_name and has_state and has_city and has_addr):
                    missing = []
                    if not has_name: missing.append("name or centre_name")
                    if not has_state: missing.append("state")
                    if not has_city: missing.append("city_district or city")
                    if not has_addr: missing.append("address")
                    flash(f"Missing required CSV columns: {', '.join(missing)}.", 'error')
                    return render_template('admin_csv_import.html')

                parsed_rows = []
                duplicates_list = []
                errors_list = []
                new_rows = []

                for row_idx, raw_row in enumerate(reader, start=2):
                    # Normalized column getter
                    def get_field(keys, default=None):
                        for k in keys:
                            for raw_k, raw_v in raw_row.items():
                                if raw_k and raw_k.strip().lower() == k:
                                    s = clean_str(raw_v)
                                    if s is not None:
                                        return s
                        return default

                    name = get_field(['name', 'centre_name'])
                    state = get_field(['state', 'state_name'])
                    city = get_field(['city_district', 'city'])
                    address = get_field(['address', 'facility_address'])

                    if not name or not state or not city or not address:
                        errors_list.append({'row': row_idx, 'error': 'Missing name, state, city, or address.'})
                        continue

                    capacity = get_field(['capacity_mta', 'capacity'])
                    centre_type = get_field(['type', 'centre_type'], 'Authorised dismantler/recycler')
                    source = get_field(['source'], 'CPCB Authorised Recyclers')
                    website = get_field(['website_url', 'website'])
                    verification = get_field(['website_verification'])
                    checked_date = get_field(['website_checked_date'])
                    phone = get_field(['phone_number', 'phone'])
                    email = get_field(['email'])
                    lat = clean_coord(get_field(['latitude', 'lat']), -90.0, 90.0)
                    lng = clean_coord(get_field(['longitude', 'lng']), -180.0, 180.0)

                    # Check duplicate against existing MySQL records
                    existing = execute_query(
                        "SELECT id FROM centres WHERE LOWER(TRIM(centre_name)) = LOWER(TRIM(%s)) AND LOWER(TRIM(address)) = LOWER(TRIM(%s))",
                        (name, address),
                        fetchone=True
                    )

                    row_dict = {
                        'row_num': row_idx,
                        'name': name,
                        'state': state,
                        'city': city,
                        'address': address,
                        'capacity': capacity,
                        'type': centre_type,
                        'source': source,
                        'website_url': website,
                        'website_verification': verification,
                        'website_checked_date': checked_date,
                        'phone_number': phone,
                        'email': email,
                        'latitude': lat,
                        'longitude': lng,
                        'is_duplicate': bool(existing)
                    }

                    parsed_rows.append(row_dict)

                    if existing:
                        duplicates_list.append({'row': row_idx, 'name': name, 'state': state, 'city': city})
                    else:
                        new_rows.append(row_dict)

                total_rows = len(parsed_rows)
                new_count = len(new_rows)
                dup_count = len(duplicates_list)

                # If preview mode requested, stage in memory and render preview
                if preview_only:
                    token = str(uuid.uuid4())
                    _CSV_STAGING_CACHE[token] = new_rows
                    preview_data = {
                        'total_rows': total_rows,
                        'new_count': new_count,
                        'duplicate_count': dup_count,
                        'rows': parsed_rows
                    }
                    return render_template(
                        'admin_csv_import.html',
                        preview_mode=True,
                        preview_data=preview_data,
                        staging_token=token
                    )

                # Direct Import: commit new_rows to MySQL
                imported_count = 0
                insert_sql = """
                INSERT INTO centres (
                    centre_name, state, city, address, capacity_mta, centre_type,
                    source, website_url, website_verification, website_checked_date,
                    phone_number, email, latitude, longitude
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for item in new_rows:
                    execute_query(
                        insert_sql,
                        (item['name'], item['state'], item['city'], item['address'],
                         item['capacity'], item['type'], item['source'], item['website_url'],
                         item['website_verification'], item['website_checked_date'],
                         item['phone_number'], item['email'], item['latitude'], item['longitude']),
                        commit=True
                    )
                    imported_count += 1

                import_result = {
                    'total_rows': total_rows,
                    'imported_count': imported_count,
                    'duplicate_count': dup_count,
                    'failed_count': len(errors_list),
                    'duplicates_list': duplicates_list,
                    'errors_list': errors_list
                }
                flash(f"CSV Ingestion complete: {imported_count} new facilities committed, {dup_count} duplicates safely skipped.", 'success')
                return render_template('admin_csv_import.html', import_result=import_result)

            except Exception as e:
                app.logger.error(f"CSV Ingestion error: {e}")
                flash(f"Failed to process CSV file: {str(e)}", 'error')
                return render_template('admin_csv_import.html')

        return render_template('admin_csv_import.html')

    @app.route('/admin/centres/import-csv/confirm', methods=['POST'])
    @admin_required
    def admin_csv_import_confirm():
        """Commit staged preview records to MySQL database."""
        token = request.form.get('staging_token')
        staged = _CSV_STAGING_CACHE.pop(token, None)

        if not staged:
            flash('Staged CSV records expired or already committed. Please upload the file again.', 'error')
            return redirect(url_for('admin_csv_import'))

        imported_count = 0
        insert_sql = """
        INSERT INTO centres (
            centre_name, state, city, address, capacity_mta, centre_type,
            source, website_url, website_verification, website_checked_date,
            phone_number, email, latitude, longitude
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for item in staged:
            execute_query(
                insert_sql,
                (item['name'], item['state'], item['city'], item['address'],
                 item['capacity'], item['type'], item['source'], item['website_url'],
                 item['website_verification'], item['website_checked_date'],
                 item['phone_number'], item['email'], item['latitude'], item['longitude']),
                commit=True
            )
            imported_count += 1

        flash(f"Batch import successful: {imported_count} verified facilities added to MySQL directory.", 'success')
        return redirect(url_for('admin_centres'))

    # ==========================================================================
    # 5. User Management (List, Search, View Details, Toggle Status)
    # ==========================================================================

    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """List registered users with search by name/email and status filtering."""
        query_term = request.args.get('q', '').strip()
        status_filter = request.args.get('status', '').strip()

        where_clauses = []
        params = []

        if query_term:
            where_clauses.append("(u.full_name LIKE %s OR u.email LIKE %s)")
            like_term = f"%{query_term}%"
            params.extend([like_term, like_term])

        if status_filter == 'active':
            where_clauses.append("u.is_active = 1")
        elif status_filter == 'inactive':
            where_clauses.append("u.is_active = 0")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Strictly omit password_hash from queries to ensure absolute privacy
        sql = f"""
        SELECT u.id, u.full_name, u.email, u.is_active, u.created_at,
               COUNT(rh.id) as calculation_count,
               COALESCE(SUM(rh.total_points), 0) as total_points
        FROM users u
        LEFT JOIN rewards_history rh ON u.id = rh.user_id
        {where_sql}
        GROUP BY u.id
        ORDER BY u.id DESC
        """
        users = execute_query(sql, tuple(params), fetchall=True) or []

        total_users_row = execute_query("SELECT COUNT(*) as total FROM users", fetchone=True)
        total_users = int(total_users_row['total'] or 0) if total_users_row else 0

        return render_template(
            'admin_users.html',
            users=users,
            total_users=total_users,
            current_query=query_term,
            current_status=status_filter
        )

    @app.route('/admin/users/view/<int:user_id>')
    @admin_required
    def admin_users_view(user_id):
        """View user profile metrics and reward calculation log without exposing passwords."""
        user = execute_query(
            "SELECT id, full_name, email, is_active, created_at FROM users WHERE id = %s",
            (user_id,),
            fetchone=True
        )
        if not user:
            flash('User account not found.', 'error')
            return redirect(url_for('admin_users'))

        history = execute_query(
            """
            SELECT rh.id, rh.quantity, rh.total_points, rh.created_at, d.device_name
            FROM rewards_history rh
            JOIN devices d ON rh.device_id = d.id
            WHERE rh.user_id = %s
            ORDER BY rh.created_at DESC
            LIMIT 25
            """,
            (user_id,),
            fetchall=True
        ) or []

        total_points = sum(int(h['total_points']) for h in history)
        total_devices_recycled = sum(int(h['quantity']) for h in history)

        return render_template(
            'admin_user_detail.html',
            user=user,
            history=history,
            total_points=total_points,
            total_devices_recycled=total_devices_recycled
        )

    @app.route('/admin/users/toggle-status/<int:user_id>', methods=['POST'])
    @admin_required
    def admin_users_toggle_status(user_id):
        """Activate or deactivate a user account."""
        user = execute_query("SELECT id, full_name, email, is_active FROM users WHERE id = %s", (user_id,), fetchone=True)
        if not user:
            flash('User account not found.', 'error')
            return redirect(url_for('admin_users'))

        new_status = 0 if user.get('is_active') == 1 else 1
        execute_query("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id), commit=True)

        status_text = "activated" if new_status == 1 else "deactivated"
        flash(f"Account for {user['full_name']} ({user['email']}) has been {status_text}.", 'success')
        return redirect(url_for('admin_users'))

    # ==========================================================================
    # 6. Device Management (List, Add, Edit, Delete)
    # ==========================================================================

    @app.route('/admin/devices')
    @admin_required
    def admin_devices():
        """View all electronic device categories with reward points and history usage."""
        sql = """
        SELECT d.id, d.device_name, d.points_per_unit,
               COUNT(DISTINCT rh.id) AS usage_count
        FROM devices d
        LEFT JOIN rewards_history rh ON d.id = rh.device_id
        GROUP BY d.id
        ORDER BY d.id ASC
        """
        devices = execute_query(sql, fetchall=True) or []
        return render_template('admin_devices.html', devices=devices)

    @app.route('/admin/devices/add', methods=['POST'])
    @admin_required
    def admin_devices_add():
        """Add new electronic device category with duplicate prevention."""
        name = clean_str(request.form.get('device_name'))
        points_raw = request.form.get('points_per_unit', '0')

        try:
            points = max(0, int(points_raw))
        except (ValueError, TypeError):
            flash('Points per unit must be a valid non-negative integer.', 'error')
            return redirect(url_for('admin_devices'))

        if not name:
            flash('Device name cannot be blank.', 'error')
            return redirect(url_for('admin_devices'))

        duplicate = execute_query(
            "SELECT id FROM devices WHERE LOWER(TRIM(device_name)) = LOWER(TRIM(%s))",
            (name,),
            fetchone=True
        )
        if duplicate:
            flash(f"A device category named '{name}' already exists.", 'error')
            return redirect(url_for('admin_devices'))

        execute_query(
            "INSERT INTO devices (device_name, points_per_unit) VALUES (%s, %s)",
            (name, points),
            commit=True
        )
        flash(f"Device category '{name}' ({points} EcoPoints/unit) added successfully.", 'success')
        return redirect(url_for('admin_devices'))

    @app.route('/admin/devices/edit/<int:device_id>', methods=['POST'])
    @admin_required
    def admin_devices_edit(device_id):
        """Update electronic device category name and points per unit."""
        device = execute_query("SELECT id, device_name FROM devices WHERE id = %s", (device_id,), fetchone=True)
        if not device:
            flash('Device category not found.', 'error')
            return redirect(url_for('admin_devices'))

        name = clean_str(request.form.get('device_name'))
        points_raw = request.form.get('points_per_unit', '0')

        try:
            points = max(0, int(points_raw))
        except (ValueError, TypeError):
            flash('Points per unit must be a valid non-negative integer.', 'error')
            return redirect(url_for('admin_devices'))

        if not name:
            flash('Device name cannot be blank.', 'error')
            return redirect(url_for('admin_devices'))

        duplicate = execute_query(
            "SELECT id FROM devices WHERE LOWER(TRIM(device_name)) = LOWER(TRIM(%s)) AND id != %s",
            (name, device_id),
            fetchone=True
        )
        if duplicate:
            flash(f"Another device category named '{name}' already exists.", 'error')
            return redirect(url_for('admin_devices'))

        execute_query(
            "UPDATE devices SET device_name = %s, points_per_unit = %s WHERE id = %s",
            (name, points, device_id),
            commit=True
        )
        flash(f"Device category '{name}' updated ({points} EcoPoints/unit).", 'success')
        return redirect(url_for('admin_devices'))

    @app.route('/admin/devices/delete/<int:device_id>', methods=['POST'])
    @admin_required
    def admin_devices_delete(device_id):
        """Permanently delete electronic device category."""
        device = execute_query("SELECT device_name FROM devices WHERE id = %s", (device_id,), fetchone=True)
        if not device:
            flash('Device category not found or already deleted.', 'error')
            return redirect(url_for('admin_devices'))

        execute_query("DELETE FROM devices WHERE id = %s", (device_id,), commit=True)
        flash(f"Device category '{device['device_name']}' deleted.", 'success')
        return redirect(url_for('admin_devices'))
