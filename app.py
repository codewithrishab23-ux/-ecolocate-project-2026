"""
EcoLocate - E-Waste Facility Locator
Phase 2-5: Flask Application with MySQL Integration, Geospatial Search & Interactive Mapping
Features: User & Admin Authentication, Werkzeug Hashing, Sessions, CSRF, Haversine Nearest Search, Leaflet.js APIs.
"""

import os
import math
import re
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from db import execute_query, check_db_health

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Enable CSRF protection across all forms
csrf = CSRFProtect(app)

@app.after_request
def add_security_headers(response):
    """Add defensive HTTP security headers to all HTTP responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://*.tile.openstreetmap.org https://unpkg.com; "
        "connect-src 'self' https://*.tile.openstreetmap.org; "
        "font-src 'self' data:;"
    )
    return response

# Helper Email Validation Regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# ==============================================================================
# Authentication Decorators
# ==============================================================================

def login_required(f):
    """Decorator to restrict routes to authenticated standard users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please sign in to access this page.', 'error')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to restrict routes to authorized system administrators."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Administrative access required. Please sign in as an admin.', 'error')
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# Public Website Routes
# ==============================================================================

@app.route('/')
def index():
    """Home landing page."""
    return render_template('index.html')

@app.route('/centres')
def centres():
    """Find Recycling Centres directory page connected to MySQL."""
    try:
        states = execute_query(
            "SELECT DISTINCT state FROM centres WHERE state IS NOT NULL AND TRIM(state) != '' ORDER BY state ASC",
            fetchall=True
        )
        devices = execute_query(
            "SELECT id, device_name FROM devices ORDER BY id ASC",
            fetchall=True
        )
        total_row = execute_query("SELECT COUNT(*) AS total FROM centres", fetchone=True)
        total_centres = total_row['total'] if total_row else 0
    except Exception as e:
        app.logger.error(f"Error loading initial centres data: {e}")
        states, devices, total_centres = [], [], 0

    return render_template(
        'centres.html',
        states=states or [],
        devices=devices or [],
        total_centres=total_centres
    )

# ==============================================================================
# Phase 4 Recycling Centre Search & Filter API Endpoints
# ==============================================================================

@app.route('/api/states')
def api_states():
    """Return distinct states list from MySQL centres table."""
    try:
        states = execute_query(
            "SELECT DISTINCT state FROM centres WHERE state IS NOT NULL AND TRIM(state) != '' ORDER BY state ASC",
            fetchall=True
        )
        return jsonify({'success': True, 'states': [s['state'] for s in states] if states else []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cities')
def api_cities():
    """Return distinct cities, optionally filtered by state."""
    state = request.args.get('state', '').strip()
    try:
        if state:
            cities = execute_query(
                "SELECT DISTINCT city FROM centres WHERE state = %s AND city IS NOT NULL AND TRIM(city) != '' ORDER BY city ASC",
                (state,),
                fetchall=True
            )
        else:
            cities = execute_query(
                "SELECT DISTINCT city FROM centres WHERE city IS NOT NULL AND TRIM(city) != '' ORDER BY city ASC",
                fetchall=True
            )
        return jsonify({'success': True, 'cities': [c['city'] for c in cities] if cities else []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices')
def api_devices():
    """Return device categories available in MySQL."""
    try:
        devices = execute_query(
            "SELECT id, device_name, points_per_unit FROM devices ORDER BY id ASC",
            fetchall=True
        )
        return jsonify({'success': True, 'devices': devices or []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.
    
    Parameters:
        lat1, lon1: Coordinates of point 1 in decimal degrees (e.g. user location)
        lat2, lon2: Coordinates of point 2 in decimal degrees (e.g. facility location)
        
    Returns:
        Distance in kilometres (float rounded to 2 decimal places)
    """
    R = 6371.0  # Earth's mean radius in kilometres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def validate_coordinates(lat_val, lng_val):
    """Validate latitude and longitude values."""
    try:
        lat = float(lat_val)
        lng = float(lng_val)
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
            return None, None, "Coordinates out of valid range (lat: [-90, 90], lng: [-180, 180])"
        return lat, lng, None
    except (ValueError, TypeError):
        return None, None, "Invalid numeric format for latitude or longitude"


@app.route('/api/centres')
def api_centres():
    """
    Search and filter recycling centres from MySQL ewaste_db.
    Supports query parameters: state, city, device_id, q, page, limit, user_lat, user_lng.
    If user_lat and user_lng are provided, calculates distance_km for each facility.
    """
    state = request.args.get('state', '').strip()
    city = request.args.get('city', '').strip()
    device_id_raw = request.args.get('device_id', '').strip()
    q = request.args.get('q', '').strip()
    user_lat_raw = request.args.get('user_lat', '').strip()
    user_lng_raw = request.args.get('user_lng', '').strip()

    user_lat, user_lng, _ = validate_coordinates(user_lat_raw, user_lng_raw) if (user_lat_raw and user_lng_raw) else (None, None, None)

    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        limit = min(50, max(1, int(request.args.get('limit', 10))))
    except (ValueError, TypeError):
        limit = 10

    offset = (page - 1) * limit

    # Build parameterized SQL conditions
    where_clauses = ["1=1"]
    params = []

    if state:
        where_clauses.append("c.state = %s")
        params.append(state)

    if city:
        where_clauses.append("c.city = %s")
        params.append(city)

    if q:
        where_clauses.append("(c.centre_name LIKE %s OR c.address LIKE %s OR c.city LIKE %s)")
        wildcard = f"%{q}%"
        params.extend([wildcard, wildcard, wildcard])

    if device_id_raw and device_id_raw.isdigit():
        device_id = int(device_id_raw)
        where_clauses.append("c.id IN (SELECT cd.centre_id FROM centre_devices cd WHERE cd.device_id = %s)")
        params.append(device_id)

    where_sql = " AND ".join(where_clauses)

    try:
        # Total matching records count
        count_sql = f"SELECT COUNT(DISTINCT c.id) AS total FROM centres c WHERE {where_sql}"
        count_row = execute_query(count_sql, tuple(params), fetchone=True)
        total = count_row['total'] if count_row else 0

        # Paginated query
        data_sql = f"""
        SELECT c.id, c.centre_name, c.state, c.city, c.address, c.capacity_mta,
               c.centre_type, c.source, c.website_url, c.website_verification,
               c.website_checked_date, c.phone_number, c.email, c.latitude, c.longitude,
               c.created_at,
               GROUP_CONCAT(d.device_name SEPARATOR ', ') AS accepted_devices
        FROM centres c
        LEFT JOIN centre_devices cd ON c.id = cd.centre_id
        LEFT JOIN devices d ON cd.device_id = d.id
        WHERE {where_sql}
        GROUP BY c.id
        ORDER BY c.state ASC, c.city ASC, c.centre_name ASC
        LIMIT %s OFFSET %s
        """
        data_params = list(params) + [limit, offset]
        centres = execute_query(data_sql, tuple(data_params), fetchall=True) or []

        # Convert decimal coordinates to float numbers for clean JSON serialization
        for centre in centres:
            if centre.get('latitude') is not None and centre.get('longitude') is not None:
                centre['latitude'] = float(centre['latitude'])
                centre['longitude'] = float(centre['longitude'])
                if user_lat is not None and user_lng is not None:
                    centre['distance_km'] = haversine_distance(
                        user_lat, user_lng, centre['latitude'], centre['longitude']
                    )
                else:
                    centre['distance_km'] = None
            else:
                centre['latitude'] = None
                centre['longitude'] = None
                centre['distance_km'] = None

        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return jsonify({
            'success': True,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages,
            'user_location': {'lat': user_lat, 'lng': user_lng} if user_lat is not None else None,
            'centres': centres
        })

    except Exception as e:
        app.logger.error(f"Error querying centres: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/centres/map')
def api_centres_map():
    """
    Fetch all recycling centres that have valid geographical coordinates for Leaflet map markers.
    Facilities with NULL coordinates are excluded from map pins to prevent display errors.
    """
    try:
        sql = """
        SELECT c.id, c.centre_name, c.state, c.city, c.address, c.capacity_mta,
               c.centre_type, c.source, c.website_url, c.website_verification,
               c.phone_number, c.email, c.latitude, c.longitude,
               GROUP_CONCAT(d.device_name SEPARATOR ', ') AS accepted_devices
        FROM centres c
        LEFT JOIN centre_devices cd ON c.id = cd.centre_id
        LEFT JOIN devices d ON cd.device_id = d.id
        WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
        GROUP BY c.id
        ORDER BY c.state ASC, c.city ASC, c.centre_name ASC
        """
        raw_centres = execute_query(sql, fetchall=True) or []
        centres = []
        for c in raw_centres:
            c['latitude'] = float(c['latitude'])
            c['longitude'] = float(c['longitude'])
            centres.append(c)

        return jsonify({
            'success': True,
            'total': len(centres),
            'centres': centres
        })
    except Exception as e:
        app.logger.error(f"Error fetching map centres: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/centres/nearby', methods=['GET', 'POST'])
@csrf.exempt
def api_centres_nearby():
    """
    Receive user's current coordinates (latitude and longitude) and return recycling centres
    with verified coordinates, sorted from nearest to farthest using the Haversine formula.
    User coordinates are strictly transient and NEVER persisted to the database.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        lat_in = data.get('lat') or data.get('latitude')
        lng_in = data.get('lng') or data.get('longitude')
        radius_in = data.get('radius') or data.get('radius_km')
        limit_in = data.get('limit')
    else:
        lat_in = request.args.get('lat') or request.args.get('latitude')
        lng_in = request.args.get('lng') or request.args.get('longitude')
        radius_in = request.args.get('radius') or request.args.get('radius_km')
        limit_in = request.args.get('limit')

    user_lat, user_lng, err = validate_coordinates(lat_in, lng_in)
    if err:
        return jsonify({'success': False, 'error': err}), 400

    try:
        radius_km = float(radius_in) if radius_in else None
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid radius_km parameter'}), 400

    try:
        limit = int(limit_in) if limit_in else None
    except ValueError:
        limit = None

    try:
        # 1. Fetch all facilities with valid coordinates
        sql = """
        SELECT c.id, c.centre_name, c.state, c.city, c.address, c.capacity_mta,
               c.centre_type, c.source, c.website_url, c.website_verification,
               c.website_checked_date, c.phone_number, c.email, c.latitude, c.longitude,
               GROUP_CONCAT(d.device_name SEPARATOR ', ') AS accepted_devices
        FROM centres c
        LEFT JOIN centre_devices cd ON c.id = cd.centre_id
        LEFT JOIN devices d ON cd.device_id = d.id
        WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
        GROUP BY c.id
        """
        rows = execute_query(sql, fetchall=True) or []

        # 2. Count facilities with and without coordinates
        stats_sql = """
        SELECT 
            SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as with_coords,
            SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) as without_coords,
            COUNT(*) as total
        FROM centres
        """
        counts = execute_query(stats_sql, fetchone=True) or {}

        # 3. Compute Haversine distance for each facility
        nearby_list = []
        for row in rows:
            facility_lat = float(row['latitude'])
            facility_lng = float(row['longitude'])
            dist = haversine_distance(user_lat, user_lng, facility_lat, facility_lng)
            if radius_km is None or dist <= radius_km:
                row_copy = dict(row)
                row_copy['latitude'] = facility_lat
                row_copy['longitude'] = facility_lng
                row_copy['distance_km'] = dist
                nearby_list.append(row_copy)

        # 4. Sort ascending by distance (nearest facility first)
        nearby_list.sort(key=lambda x: x['distance_km'])

        if limit and limit > 0:
            result_list = nearby_list[:limit]
        else:
            result_list = nearby_list

        return jsonify({
            'success': True,
            'user_location': {
                'latitude': user_lat,
                'longitude': user_lng
            },
            'count': len(result_list),
            'total_nearby': len(nearby_list),
            'total_with_coordinates': int(counts.get('with_coords') or 0),
            'total_without_coordinates': int(counts.get('without_coords') or 0),
            'radius_km': radius_km,
            'centres': result_list,
            'message': (
                f"Found {len(result_list)} verified recycling centres sorted by proximity."
                if result_list else
                "No recycling centres with verified coordinates found within the specified range. You can use State and City filters to view all 87 registered facilities."
            )
        })

    except Exception as e:
        app.logger.error(f"Error calculating nearby centres: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/centres/<int:centre_id>')
def api_centre_detail(centre_id):
    """Retrieve detailed information for a single recycling centre."""
    try:
        detail_sql = """
        SELECT c.*, GROUP_CONCAT(d.device_name SEPARATOR ', ') AS accepted_devices
        FROM centres c
        LEFT JOIN centre_devices cd ON c.id = cd.centre_id
        LEFT JOIN devices d ON cd.device_id = d.id
        WHERE c.id = %s
        GROUP BY c.id
        """
        centre = execute_query(detail_sql, (centre_id,), fetchone=True)
        if not centre:
            return jsonify({'success': False, 'error': 'Facility not found'}), 404

        return jsonify({'success': True, 'centre': centre})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/awareness')
def awareness():
    """Why E-Waste Matters educational page."""
    return render_template('awareness.html')


@app.route('/rewards')
def rewards():
    """
    EcoRewards interactive calculator page.
    Loads active devices from MySQL and user's past calculation history if logged in.
    """
    try:
        devices = execute_query(
            "SELECT id, device_name, points_per_unit FROM devices ORDER BY id ASC",
            fetchall=True
        ) or []
    except Exception as e:
        app.logger.error(f"Error loading devices for rewards page: {e}")
        devices = []

    user_history = []
    total_points = 0
    user_id = session.get('user_id')
    if user_id:
        try:
            history_sql = """
            SELECT rh.id, rh.quantity, rh.total_points, rh.created_at,
                   d.device_name, d.points_per_unit
            FROM rewards_history rh
            JOIN devices d ON rh.device_id = d.id
            WHERE rh.user_id = %s
            ORDER BY rh.created_at DESC
            LIMIT 15
            """
            user_history = execute_query(history_sql, (user_id,), fetchall=True) or []
            
            sum_sql = "SELECT SUM(total_points) as total FROM rewards_history WHERE user_id = %s"
            sum_row = execute_query(sum_sql, (user_id,), fetchone=True)
            total_points = int(sum_row['total'] or 0) if sum_row and sum_row['total'] else 0
        except Exception as e:
            app.logger.error(f"Error loading rewards history: {e}")
            user_history = []

    return render_template(
        'rewards.html',
        devices=devices,
        user_history=user_history,
        total_points=total_points
    )


@app.route('/api/rewards/calculate', methods=['POST'])
@csrf.exempt
def api_calculate_rewards():
    """
    Backend reward calculation endpoint.
    Formula: Total Points = Quantity * Points Per Unit.
    Performs server-side validation on device selection and quantity.
    """
    data = request.get_json(silent=True) or request.form
    device_id_raw = data.get('device_id')
    quantity_raw = data.get('quantity')

    if not device_id_raw:
        return jsonify({'success': False, 'error': 'Please select an electronic device.'}), 400

    try:
        device_id = int(device_id_raw)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid device identifier.'}), 400

    try:
        quantity = int(quantity_raw)
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'Quantity must be a positive integer greater than zero.'}), 400
        if quantity > 1000:
            return jsonify({'success': False, 'error': 'Quantity exceeds maximum allowable calculation limit (1,000 units).'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Please provide a valid numeric quantity.'}), 400

    try:
        device = execute_query(
            "SELECT id, device_name, points_per_unit FROM devices WHERE id = %s",
            (device_id,),
            fetchone=True
        )
        if not device:
            return jsonify({'success': False, 'error': 'Selected device category not found.'}), 404

        points_per_unit = int(device['points_per_unit'])
        total_points = quantity * points_per_unit

        # Illustrative estimated environmental metrics based on device type
        est_co2_kg = round(quantity * (points_per_unit * 0.12), 1)
        est_materials_g = round(quantity * (points_per_unit * 0.25), 1)

        return jsonify({
            'success': True,
            'device_id': device['id'],
            'device_name': device['device_name'],
            'points_per_unit': points_per_unit,
            'quantity': quantity,
            'total_points': total_points,
            'est_co2_kg': est_co2_kg,
            'est_materials_g': est_materials_g,
            'message': f"{quantity} unit(s) of {device['device_name']} = {total_points} estimated EcoPoints",
            'is_logged_in': bool(session.get('user_id'))
        })

    except Exception as e:
        app.logger.error(f"Error calculating rewards: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rewards/save', methods=['POST'])
@csrf.exempt
def api_save_reward_calculation():
    """
    Save calculated reward projection to user's history in MySQL.
    Strictly restricted to authenticated users.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'Please log in to save reward calculations to your profile.'
        }), 401

    data = request.get_json(silent=True) or request.form
    device_id_raw = data.get('device_id')
    quantity_raw = data.get('quantity')

    try:
        device_id = int(device_id_raw)
        quantity = int(quantity_raw)
        if quantity <= 0 or quantity > 1000:
            return jsonify({'success': False, 'error': 'Quantity must be between 1 and 1,000.'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid device or quantity parameters.'}), 400

    try:
        device = execute_query(
            "SELECT id, device_name, points_per_unit FROM devices WHERE id = %s",
            (device_id,),
            fetchone=True
        )
        if not device:
            return jsonify({'success': False, 'error': 'Device category not found.'}), 404

        total_points = quantity * int(device['points_per_unit'])

        insert_sql = """
        INSERT INTO rewards_history (user_id, device_id, quantity, total_points)
        VALUES (%s, %s, %s, %s)
        """
        execute_query(insert_sql, (user_id, device_id, quantity, total_points), commit=True)

        return jsonify({
            'success': True,
            'message': f'Saved calculation ({total_points} EcoPoints) to your history.',
            'entry': {
                'device_name': device['device_name'],
                'quantity': quantity,
                'total_points': total_points,
                'points_per_unit': device['points_per_unit']
            }
        }), 201

    except Exception as e:
        app.logger.error(f"Error saving reward history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rewards/history', methods=['GET'])
def api_get_rewards_history():
    """
    Fetch reward history for the currently authenticated user.
    Enforces tenant privacy: users cannot access other users' calculation history.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401

    try:
        sql = """
        SELECT rh.id, rh.quantity, rh.total_points, rh.created_at,
               d.device_name, d.points_per_unit
        FROM rewards_history rh
        JOIN devices d ON rh.device_id = d.id
        WHERE rh.user_id = %s
        ORDER BY rh.created_at DESC
        """
        history = execute_query(sql, (user_id,), fetchall=True) or []

        sum_sql = "SELECT SUM(total_points) as total FROM rewards_history WHERE user_id = %s"
        sum_row = execute_query(sum_sql, (user_id,), fetchone=True)
        total = int(sum_row['total'] or 0) if sum_row and sum_row['total'] else 0

        return jsonify({
            'success': True,
            'history': history,
            'total_points': total,
            'count': len(history)
        })

    except Exception as e:
        app.logger.error(f"Error querying rewards history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rewards/history/clear', methods=['POST'])
@csrf.exempt
def api_clear_rewards_history():
    """Clear calculation history for the currently authenticated user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401

    try:
        execute_query("DELETE FROM rewards_history WHERE user_id = %s", (user_id,), commit=True)
        return jsonify({'success': True, 'message': 'Rewards calculation history cleared.'})
    except Exception as e:
        app.logger.error(f"Error clearing rewards history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/about')
def about():
    """About EcoLocate & Roadmap page."""
    return render_template('about.html')
    return render_template('about.html')

# ==============================================================================
# User Authentication Routes (Register, Login, Logout, Profile)
# ==============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with input validation, duplicate check, and password hashing."""
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms')

        # 1. Field presence validation
        if not full_name or not email or not password or not confirm_password:
            flash('All registration fields are required.', 'error')
            return render_template('register.html'), 400

        # 2. Email format validation
        if not EMAIL_REGEX.match(email):
            flash('Please provide a valid email address.', 'error')
            return render_template('register.html'), 400

        # 3. Password length & matching validation
        if len(password) < 8:
            flash('Password must contain at least 8 characters.', 'error')
            return render_template('register.html'), 400

        if password != confirm_password:
            flash('Passwords do not match. Please verify and re-enter.', 'error')
            return render_template('register.html'), 400

        # 4. Terms acceptance check
        if not terms:
            flash('You must accept the Terms of Service to create an account.', 'error')
            return render_template('register.html'), 400

        try:
            # 5. Duplicate email check
            existing_user = execute_query(
                "SELECT id FROM users WHERE email = %s",
                (email,),
                fetchone=True
            )

            if existing_user:
                flash('This email address is already registered. Please sign in.', 'error')
                return render_template('register.html'), 409

            # 6. Secure password hashing
            password_hash = generate_password_hash(password)

            # 7. Insert new user into database
            user_id = execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                (full_name, email, password_hash),
                commit=True
            )

            # 8. Create secure session
            session.clear()
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['user_email'] = email
            session.permanent = True

            flash(f'Account created successfully! Welcome to EcoLocate, {full_name}.', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            app.logger.error(f"Registration error: {e}")
            flash('A database error occurred during registration. Please try again.', 'error')
            return render_template('register.html'), 500

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login authentication using email and hashed password verification."""
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both your email address and password.', 'error')
            return render_template('login.html'), 400

        try:
            # Retrieve user record by email
            user = execute_query(
                "SELECT id, full_name, email, password_hash, is_active FROM users WHERE email = %s",
                (email,),
                fetchone=True
            )

            # Verify password using Werkzeug's secure hash check
            if user and check_password_hash(user['password_hash'], password):
                if user.get('is_active') == 0:
                    flash('Your account has been deactivated. Please contact an administrator.', 'error')
                    return render_template('login.html'), 403

                session.clear()
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                session.permanent = True

                flash(f'Welcome back, {user["full_name"]}!', 'success')
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password. Please verify your credentials.', 'error')
                return render_template('login.html'), 401

        except Exception as e:
            app.logger.error(f"Login error: {e}")
            flash('An error occurred during sign-in. Please try again later.', 'error')
            return render_template('login.html'), 500

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out standard user and terminate session."""
    user_name = session.get('user_name', 'User')
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """Protected user profile page showing account details."""
    user_id = session.get('user_id')
    user = execute_query(
        "SELECT id, full_name, email, created_at FROM users WHERE id = %s",
        (user_id,),
        fetchone=True
    )
    if not user:
        session.clear()
        flash('User account not found. Please sign in again.', 'error')
        return redirect(url_for('login'))

    return render_template('profile.html', user=user)

# ==============================================================================
# Admin Authentication, Dashboard & Management Routes (Phase 7)
# ==============================================================================
from admin import register_admin_routes
register_admin_routes(app)

# ==============================================================================
# Health Check & Diagnostics
# ==============================================================================

@app.route('/health')
def health_check():
    """API health check to verify Flask and MySQL database status."""
    is_healthy, message = check_db_health()
    return jsonify({
        "status": "healthy" if is_healthy else "degraded",
        "database": "connected" if is_healthy else "disconnected",
        "message": message,
        "phase": "Phase 2 (Flask & MySQL)"
    }), (200 if is_healthy else 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1').lower() in ('1', 'true')
    app.run(host='0.0.0.0', port=port, debug=debug)
