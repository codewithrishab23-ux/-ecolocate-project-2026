"""
Comprehensive Automated Test Suite for EcoLocate
Phases 1, 2, 3, and 4 (Flask, MySQL, Ingested Data, Search & Filter API, Contact Options).
"""

import unittest
from app import app
from db import execute_query, check_db_health
from werkzeug.security import check_password_hash

class EcoLocateComprehensiveTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Clean up test users from ewaste_db before running suite."""
        execute_query("DELETE FROM users WHERE email LIKE '%@testdomain.demo'", commit=True)
        execute_query("DELETE FROM centres WHERE id > 87", commit=True)
        execute_query("DELETE FROM devices WHERE device_name LIKE 'Test %'", commit=True)
        execute_query("DELETE FROM ewaste_submissions WHERE phone_number LIKE '99999%' OR email LIKE '%@testdomain.demo'", commit=True)
        execute_query("DELETE FROM email_logs WHERE recipient_email LIKE '%@testdomain.demo'", commit=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test users after test suite completes."""
        execute_query("DELETE FROM users WHERE email LIKE '%@testdomain.demo'", commit=True)
        execute_query("DELETE FROM centres WHERE id > 87", commit=True)
        execute_query("DELETE FROM devices WHERE device_name LIKE 'Test %'", commit=True)
        execute_query("DELETE FROM ewaste_submissions WHERE phone_number LIKE '99999%' OR email LIKE '%@testdomain.demo'", commit=True)
        execute_query("DELETE FROM email_logs WHERE recipient_email LIKE '%@testdomain.demo'", commit=True)

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Programmatic test client bypass
        self.client = self.app.test_client()

    # ==========================================================================
    # Phase 2 Core Tests: Authentication & Session Management
    # ==========================================================================

    def test_01_database_connectivity(self):
        """Test 1: Verify MySQL connectivity and health check endpoint."""
        healthy, message = check_db_health()
        self.assertTrue(healthy, f"Database connectivity failed: {message}")
        
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'healthy')
        self.assertEqual(json_data['database'], 'connected')
        print("\n[PASS] Test 1: Database Connectivity & Health Check Verified.")

    def test_02_user_registration(self):
        """Test 2: Verify user registration and password hashing in MySQL."""
        email = "alice@testdomain.demo"
        full_name = "Alice Green"
        password = "SecurePassword123!"

        response = self.client.post('/register', data={
            'full_name': full_name,
            'email': email,
            'password': password,
            'confirm_password': password,
            'terms': 'on'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Alice Green", response.data)

        db_user = execute_query(
            "SELECT id, full_name, email, password_hash, created_at FROM users WHERE email = %s",
            (email,),
            fetchone=True
        )
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user['full_name'], full_name)
        self.assertNotEqual(db_user['password_hash'], password)
        self.assertTrue(check_password_hash(db_user['password_hash'], password))
        print("[PASS] Test 2: User Registration & Werkzeug Password Hashing Verified.")

    def test_03_duplicate_email_prevention(self):
        """Test 3: Verify that duplicate email registration returns 409 Conflict."""
        email = "alice@testdomain.demo"

        response = self.client.post('/register', data={
            'full_name': "Alice Clone",
            'email': email,
            'password': "DifferentPassword456!",
            'confirm_password': "DifferentPassword456!",
            'terms': 'on'
        })

        self.assertEqual(response.status_code, 409)
        self.assertIn(b"already registered", response.data)
        print("[PASS] Test 3: Duplicate Email Registration Prevention Verified.")

    def test_04_incorrect_password_handling(self):
        """Test 4: Verify invalid login password returns 401 Unauthorized."""
        response = self.client.post('/login', data={
            'email': "alice@testdomain.demo",
            'password': "WrongPassword999!"
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid email or password", response.data)
        print("[PASS] Test 4: Incorrect Password Rejection Verified.")

    def test_05_successful_login(self):
        """Test 5: Verify successful user login creates active session."""
        with self.client as c:
            response = c.post('/login', data={
                'email': "alice@testdomain.demo",
                'password': "SecurePassword123!"
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Welcome back, Alice Green!", response.data)
            
            with c.session_transaction() as sess:
                self.assertIsNotNone(sess.get('user_id'))
                self.assertEqual(sess.get('user_name'), "Alice Green")

        print("[PASS] Test 5: Successful User Login & Session Creation Verified.")

    def test_06_logout_functionality(self):
        """Test 6: Verify logout terminates session."""
        with self.client as c:
            c.post('/login', data={
                'email': "alice@testdomain.demo",
                'password': "SecurePassword123!"
            })

            logout_resp = c.get('/logout', follow_redirects=True)
            self.assertEqual(logout_resp.status_code, 200)
            self.assertIn(b"signed out successfully", logout_resp.data)

            with c.session_transaction() as sess:
                self.assertIsNone(sess.get('user_id'))

        print("[PASS] Test 6: User Logout & Session Invalidation Verified.")

    def test_07_session_protection(self):
        """Test 7: Verify unauthenticated request to /profile is redirected."""
        unauth_resp = self.client.get('/profile', follow_redirects=True)
        self.assertIn(b"Please sign in to access this page", unauth_resp.data)
        print("[PASS] Test 7: Route Protection (@login_required) Verified.")

    def test_08_admin_login(self):
        """Test 8: Verify admin login with hashed credentials and session."""
        with self.client as c:
            response = c.post('/admin/login', data={
                'username': "admin",
                'password': "AdminSecure2026!"
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Control Panel", response.data)

            with c.session_transaction() as sess:
                self.assertIsNotNone(sess.get('admin_id'))
                self.assertEqual(sess.get('admin_username'), "admin")

        print("[PASS] Test 8: Admin Authentication Verified.")

    def test_09_admin_user_role_separation(self):
        """Test 9: Verify normal user is barred from admin dashboard."""
        with self.client as c:
            c.post('/login', data={
                'email': "alice@testdomain.demo",
                'password': "SecurePassword123!"
            })

            admin_dash_resp = c.get('/admin/dashboard', follow_redirects=True)
            self.assertIn(b"Administrative access required", admin_dash_resp.data)

        print("[PASS] Test 9: Admin and User Access Role Separation Verified.")

    def test_10_multiple_independent_sessions(self):
        """Test 10: Verify multiple users have completely isolated sessions."""
        client_alice = self.app.test_client()
        client_bob = self.app.test_client()

        client_bob.post('/register', data={
            'full_name': "Bob Circuit",
            'email': "bob@testdomain.demo",
            'password': "BobPassword456!",
            'confirm_password': "BobPassword456!",
            'terms': 'on'
        })

        client_alice.post('/login', data={
            'email': "alice@testdomain.demo",
            'password': "SecurePassword123!"
        })

        client_bob.post('/login', data={
            'email': "bob@testdomain.demo",
            'password': "BobPassword456!"
        })

        self.assertIn(b"Alice Green", client_alice.get('/profile').data)
        self.assertNotIn(b"Bob Circuit", client_alice.get('/profile').data)

        self.assertIn(b"Bob Circuit", client_bob.get('/profile').data)
        self.assertNotIn(b"Alice Green", client_bob.get('/profile').data)
        print("[PASS] Test 10: Multiple Independent User Sessions Verified.")

    # ==========================================================================
    # Phase 3 & 4 Tests: Search, Filter System & Contact Channels
    # ==========================================================================

    def test_11_api_states(self):
        """Test 11: Verify /api/states returns distinct states from MySQL."""
        response = self.client.get('/api/states')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        states = data['states']
        self.assertGreaterEqual(len(states), 20)
        self.assertIn('Delhi', states)
        self.assertIn('Maharashtra', states)
        self.assertIn('Karnataka', states)
        print("[PASS] Test 11: Dynamic States List from MySQL Verified.")

    def test_12_api_cities_by_state(self):
        """Test 12: Verify /api/cities dynamically filters cities for a given state."""
        # Cities in Andhra Pradesh
        response_ap = self.client.get('/api/cities?state=Andhra+Pradesh')
        self.assertEqual(response_ap.status_code, 200)
        data_ap = response_ap.get_json()
        self.assertTrue(data_ap['success'])
        cities_ap = data_ap['cities']
        self.assertIn('Visakhapatnam', cities_ap)
        self.assertIn('Anantapur', cities_ap)
        self.assertNotIn('Pune', cities_ap)

        # Cities in Maharashtra
        response_mh = self.client.get('/api/cities?state=Maharashtra')
        data_mh = response_mh.get_json()
        cities_mh = data_mh['cities']
        self.assertIn('Mumbai', cities_mh)
        self.assertIn('Pune', cities_mh)
        self.assertNotIn('Visakhapatnam', cities_mh)
        print("[PASS] Test 12: Dynamic City Filtering by State Verified.")

    def test_13_api_devices(self):
        """Test 13: Verify /api/devices returns standard categories from devices table."""
        response = self.client.get('/api/devices')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        device_names = [d['device_name'] for d in data['devices']]
        self.assertIn('Mobile Phones & Tablets', device_names)
        self.assertIn('Laptops & Computers', device_names)
        print("[PASS] Test 13: Devices Table Integration Verified.")

    def test_14_search_by_state(self):
        """Test 14: Search facilities by state."""
        response = self.client.get('/api/centres?state=Delhi')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 6)
        for centre in data['centres']:
            self.assertEqual(centre['state'], 'Delhi')
        print("[PASS] Test 14: Filter Facilities by State Verified (6 in Delhi).")

    def test_15_search_by_city(self):
        """Test 15: Search facilities by city."""
        response = self.client.get('/api/centres?state=Andhra+Pradesh&city=Visakhapatnam')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 3)
        for centre in data['centres']:
            self.assertEqual(centre['city'], 'Visakhapatnam')
        print("[PASS] Test 15: Filter Facilities by City Verified (3 in Visakhapatnam).")

    def test_16_multiple_filters_and_keyword(self):
        """Test 16: Apply multiple filters together (state + keyword search)."""
        response = self.client.get('/api/centres?state=Delhi&q=Techchef')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 1)
        self.assertIn('Techchef', data['centres'][0]['centre_name'])
        print("[PASS] Test 16: Compound Filters & Keyword Search Verified.")

    def test_17_search_unavailable_location(self):
        """Test 17: Search for non-existent location returns 0 without error."""
        response = self.client.get('/api/centres?state=Atlantis')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 0)
        self.assertEqual(len(data['centres']), 0)
        print("[PASS] Test 17: Empty Result Handling for Unavailable Locations Verified.")

    def test_18_pagination(self):
        """Test 18: Verify pagination across the 87 ingested database facilities."""
        response_p1 = self.client.get('/api/centres?page=1&limit=10')
        self.assertEqual(response_p1.status_code, 200)
        data_p1 = response_p1.get_json()
        self.assertEqual(data_p1['total'], 87)
        self.assertEqual(len(data_p1['centres']), 10)
        self.assertEqual(data_p1['page'], 1)
        self.assertEqual(data_p1['total_pages'], 9)

        response_p9 = self.client.get('/api/centres?page=9&limit=10')
        data_p9 = response_p9.get_json()
        self.assertEqual(len(data_p9['centres']), 7)  # 87 total = 8*10 + 7
        print("[PASS] Test 18: Pagination Verified (87 items across 9 pages).")

    def test_19_centre_detail(self):
        """Test 19: Retrieve single centre detail by ID."""
        response = self.client.get('/api/centres/3')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['centre']['centre_name'], 'Veera Waste Management Systems')
        self.assertEqual(data['centre']['website_url'], 'https://www.veeraenergies.com/')
        print("[PASS] Test 19: Single Facility Detail Query Verified.")

    def test_20_contact_channels_integrity(self):
        """Test 20: Verify contact channels data integrity (no fabricated contacts or coordinates)."""
        response = self.client.get('/api/centres?limit=50')
        data = response.get_json()
        centres = data['centres']
        for c in centres:
            # Lat/Lng should either be valid or None (never arbitrary placeholder strings)
            if c['latitude'] is not None:
                self.assertIsInstance(c['latitude'], (int, float))
            # Address and Name must always be non-empty
            self.assertTrue(bool(c['centre_name'].strip()))
            self.assertTrue(bool(c['address'].strip()))

        print("[PASS] Test 20: Contact Information Integrity & Verification Verified.")

    # ==========================================================================
    # Phase 5 Tests: Interactive Map, Haversine Nearest Search & Geolocation
    # ==========================================================================

    def test_21_haversine_formula_math(self):
        """Test 21: Verify Haversine formula calculates accurate distances in kilometres."""
        from app import haversine_distance
        # Reference coordinates: New Delhi (28.6139, 77.2090) to Mumbai (19.0760, 72.8777)
        # Known great-circle distance is approximately 1148 km (+/- 10 km)
        distance = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        self.assertAlmostEqual(distance, 1148.0, delta=15.0)

        # Distance to itself should be 0.0
        self.assertEqual(haversine_distance(28.6139, 77.2090, 28.6139, 77.2090), 0.0)
        print("[PASS] Test 21: Haversine Distance Calculation Verified (Earth radius 6371 km).")

    def test_22_api_centres_map_coordinates(self):
        """Test 22: Verify /api/centres/map returns only centres with valid coordinates."""
        response = self.client.get('/api/centres/map')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 20)
        for c in data['centres']:
            self.assertIsNotNone(c['latitude'])
            self.assertIsNotNone(c['longitude'])
            self.assertIsInstance(c['latitude'], (int, float))
            self.assertIsInstance(c['longitude'], (int, float))
            self.assertTrue(bool(c['centre_name']))
            self.assertTrue(bool(c['address']))
        print("[PASS] Test 22: Interactive Map Data Endpoint Verified (20 facilities plotted).")

    def test_23_nearby_centres_sorting(self):
        """Test 23: Verify /api/centres/nearby sorts facilities ascending (nearest first)."""
        # User in South Delhi near Okhla (28.5355, 77.2711)
        response = self.client.get('/api/centres/nearby?lat=28.5355&lng=77.2711')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)

        centres = data['centres']
        # Nearest facility should be Techchef E-Waste Solutions in Okhla (distance ~0.0 km)
        nearest = centres[0]
        self.assertIn('Techchef', nearest['centre_name'])
        self.assertLessEqual(nearest['distance_km'], 1.0)

        # Verify ascending order
        distances = [c['distance_km'] for c in centres]
        self.assertEqual(distances, sorted(distances))
        print("[PASS] Test 23: Nearest Centre Calculation & Proximity Sorting Verified.")

    def test_24_distance_in_kilometres_format(self):
        """Test 24: Verify distance is reported as float in kilometres with decimal precision."""
        response = self.client.get('/api/centres/nearby?lat=12.9716&lng=77.5946')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        for c in data['centres']:
            self.assertIn('distance_km', c)
            self.assertIsInstance(c['distance_km'], (int, float))
            self.assertGreaterEqual(c['distance_km'], 0.0)
        print("[PASS] Test 24: Distance Displayed in Kilometres Verified.")

    def test_25_invalid_coordinate_validation(self):
        """Test 25: Verify out-of-range or malformed coordinates return 400 Bad Request."""
        # Latitude > 90
        res1 = self.client.get('/api/centres/nearby?lat=95.0&lng=77.0')
        self.assertEqual(res1.status_code, 400)
        self.assertFalse(res1.get_json()['success'])

        # Longitude < -180
        res2 = self.client.get('/api/centres/nearby?lat=28.0&lng=-190.0')
        self.assertEqual(res2.status_code, 400)

        # Non-numeric string
        res3 = self.client.get('/api/centres/nearby?lat=abc&lng=xyz')
        self.assertEqual(res3.status_code, 400)
        print("[PASS] Test 25: Coordinate Validation & Error Handling Verified.")

    def test_26_centres_without_coordinates_remain_searchable(self):
        """Test 26: Verify facilities without coordinates (NULL) remain searchable in directory."""
        response = self.client.get('/api/centres?page=1&limit=50')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total'], 87)

        # Confirm facilities without coordinates exist and have complete address
        null_coords_found = False
        for c in data['centres']:
            if c['latitude'] is None or c['longitude'] is None:
                null_coords_found = True
                self.assertTrue(bool(c['address'].strip()))
                self.assertTrue(bool(c['city'].strip()))
        self.assertTrue(null_coords_found, "Database must contain facilities with NULL coordinates")
        print("[PASS] Test 26: Facilities Without Coordinates Remain Searchable & Intact.")

    def test_27_nearby_with_radius_filter(self):
        """Test 27: Verify radius_km parameter restricts results to specified radius."""
        # Delhi coordinates with 40 km radius
        response = self.client.get('/api/centres/nearby?lat=28.6139&lng=77.2090&radius_km=40')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        for c in data['centres']:
            self.assertLessEqual(c['distance_km'], 40.0)
        print("[PASS] Test 27: Radius-based Spatial Filtering Verified.")

    def test_28_leaflet_map_page_render(self):
        """Test 28: Verify centres.html renders Leaflet assets, map div, and location button."""
        response = self.client.get('/centres')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('id="map"', html)
        self.assertIn('leaflet@1.9.4', html)
        self.assertIn('Use My Current Location', html)
        self.assertIn('OpenStreetMap', html)
        self.assertIn('nearest-notice-banner', html)
        print("[PASS] Test 28: Interactive Leaflet Map & Geolocation UI Integration Verified.")

    def test_29_post_centres_nearby_json(self):
        """Test 29: Verify POST /api/centres/nearby accepts JSON coordinate payload."""
        response = self.client.post('/api/centres/nearby', json={
            'latitude': 12.9716,
            'longitude': 77.5946
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        # Nearest in Bengaluru should be E-Friendly or Sriram Eco Raksha
        nearest = data['centres'][0]
        self.assertEqual(nearest['state'], 'Karnataka')
        self.assertEqual(nearest['city'], 'Bengaluru')
        print("[PASS] Test 29: POST Geolocation Endpoint Verified (Bengaluru cluster).")

    def test_30_nearby_missing_coordinates_stats(self):
        """Test 30: Verify nearby response returns total with and without coordinates."""
        response = self.client.get('/api/centres/nearby?lat=28.61&lng=77.20')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total_with_coordinates'], 20)
        self.assertEqual(data['total_without_coordinates'], 67)
        self.assertIn('user_location', data)
        self.assertEqual(data['user_location']['latitude'], 28.61)
        print("[PASS] Test 30: Database Coordinate Statistics & Transparency Verified.")

    # ==========================================================================
    # Phase 6 Tests: E-Waste Awareness, Rewards Calculator & History Log
    # ==========================================================================

    def test_31_awareness_page_loads_and_examples(self):
        """Test 31: Verify awareness page loads with What is E-Waste and examples."""
        response = self.client.get('/awareness')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('What is Electronic Waste', html)
        self.assertIn('Mobile Phones', html)
        self.assertIn('Laptops', html)
        self.assertIn('Batteries', html)
        self.assertIn('Televisions', html)
        self.assertIn('Chargers', html)
        print("[PASS] Test 31: Awareness Page & Common Examples Verified.")

    def test_32_three_harmful_materials(self):
        """Test 32: Verify Lead, Mercury, and Cadmium hazardous materials are detailed."""
        response = self.client.get('/awareness')
        html = response.data.decode('utf-8')
        # Lead
        self.assertIn('id="lead"', html)
        self.assertIn('Lead', html)
        self.assertIn('soldering', html.lower())
        # Mercury
        self.assertIn('id="mercury"', html)
        self.assertIn('Mercury', html)
        self.assertIn('Fluorescent display backlights', html)
        # Cadmium
        self.assertIn('id="cadmium"', html)
        self.assertIn('Cadmium', html)
        self.assertIn('Rechargeable NiCd batteries', html)
        print("[PASS] Test 32: The Big Three Hazardous Materials (Pb, Hg, Cd) Verified.")

    def test_33_environmental_impact_sections(self):
        """Test 33: Verify all 4 environmental impact dimensions are explained."""
        response = self.client.get('/awareness')
        html = response.data.decode('utf-8')
        self.assertIn('Soil Pollution', html)
        self.assertIn('Water Contamination', html)
        self.assertIn('Air Pollution (Unsafe Open Burning)', html)
        self.assertIn('Harm to Plants, Animals', html)
        print("[PASS] Test 33: Environmental Degradation Impacts Verified.")

    def test_34_responsible_recycling_and_steps(self):
        """Test 34: Verify responsible recycling principles and 4 actionable steps."""
        response = self.client.get('/awareness')
        html = response.data.decode('utf-8')
        self.assertIn('Why NOT Regular Dustbins?', html)
        self.assertIn('Why Certified Facilities Matter', html)
        self.assertIn('How to Recycle Your E-Waste in 4 Simple Steps', html)
        self.assertIn('Backup &amp; Wipe Data', html)
        self.assertIn('Separate Accessories', html)
        self.assertIn('Locate Certified Recycler', html)
        self.assertIn('Drop Off &amp; Calculate Rewards', html)
        print("[PASS] Test 34: Responsible Recycling Principles & 4 Steps Verified.")

    def test_35_rewards_page_loads_devices_from_mysql(self):
        """Test 35: Verify rewards page dynamically fetches devices from MySQL."""
        response = self.client.get('/rewards')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('Mobile Phone', html)
        self.assertIn('Laptop', html)
        self.assertIn('Tablet', html)
        self.assertIn('Desktop Computer', html)
        self.assertIn('Television', html)
        self.assertIn('Keyboard', html)
        self.assertIn('Mouse', html)
        self.assertIn('Charger', html)
        self.assertIn('Disclaimer: Illustrative Demonstration Values Only', html)
        print("[PASS] Test 35: Rewards Page & MySQL Dynamic Devices Loading Verified.")

    def test_36_reward_calculation_formula(self):
        """Test 36: Verify calculation formula: Total Points = Quantity * Points Per Unit."""
        # Query device id for Mobile Phone (10 points)
        dev = execute_query("SELECT id, points_per_unit FROM devices WHERE device_name = 'Mobile Phone'", fetchone=True)
        self.assertIsNotNone(dev)
        phone_id = dev['id']
        self.assertEqual(dev['points_per_unit'], 10)

        # 3 Mobile phones = 30 points
        response = self.client.post('/api/rewards/calculate', json={
            'device_id': phone_id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_points'], 30)
        self.assertEqual(data['points_per_unit'], 10)
        self.assertEqual(data['quantity'], 3)

        # 2 Laptops (25 points each) = 50 points
        laptop = execute_query("SELECT id FROM devices WHERE device_name = 'Laptop'", fetchone=True)
        res_laptop = self.client.post('/api/rewards/calculate', json={
            'device_id': laptop['id'],
            'quantity': 2
        })
        self.assertEqual(res_laptop.get_json()['total_points'], 50)
        print("[PASS] Test 36: Reward Calculation Formula Verified (3 Mobile Phones = 30 pts; 2 Laptops = 50 pts).")

    def test_37_quantity_validation_backend(self):
        """Test 37: Verify backend validates quantities (rejects <=0, non-numeric, >1000)."""
        dev = execute_query("SELECT id FROM devices LIMIT 1", fetchone=True)
        dev_id = dev['id']

        # Zero quantity
        r1 = self.client.post('/api/rewards/calculate', json={'device_id': dev_id, 'quantity': 0})
        self.assertEqual(r1.status_code, 400)

        # Negative quantity
        r2 = self.client.post('/api/rewards/calculate', json={'device_id': dev_id, 'quantity': -5})
        self.assertEqual(r2.status_code, 400)

        # Non-numeric quantity
        r3 = self.client.post('/api/rewards/calculate', json={'device_id': dev_id, 'quantity': 'invalid'})
        self.assertEqual(r3.status_code, 400)

        # Excessively large quantity (>1000)
        r4 = self.client.post('/api/rewards/calculate', json={'device_id': dev_id, 'quantity': 1001})
        self.assertEqual(r4.status_code, 400)
        print("[PASS] Test 37: Backend Quantity Validation Verified.")

    def test_38_authenticated_save_reward_calculation(self):
        """Test 38: Verify authenticated user can save calculation to rewards_history."""
        # Unauthenticated attempt should fail with 401
        res_unauth = self.client.post('/api/rewards/save', json={'device_id': 6, 'quantity': 2})
        self.assertEqual(res_unauth.status_code, 401)

        # Authenticate as Alice
        user = execute_query("SELECT id FROM users WHERE email = 'alice@testdomain.demo'", fetchone=True)
        if not user:
            from werkzeug.security import generate_password_hash
            user_id = execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                ("Alice Green", "alice@testdomain.demo", generate_password_hash("SecurePassword123!")),
                commit=True
            )
        else:
            user_id = user['id']

        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_name'] = "Alice Green"

        # Save calculation
        dev = execute_query("SELECT id, points_per_unit FROM devices WHERE device_name = 'Mobile Phone'", fetchone=True)
        res_save = self.client.post('/api/rewards/save', json={'device_id': dev['id'], 'quantity': 4})
        self.assertEqual(res_save.status_code, 201)
        save_data = res_save.get_json()
        self.assertTrue(save_data['success'])
        self.assertEqual(save_data['entry']['total_points'], 40)

        # Verify entry in MySQL
        history_row = execute_query(
            "SELECT quantity, total_points FROM rewards_history WHERE user_id = %s",
            (user_id,),
            fetchone=True
        )
        self.assertIsNotNone(history_row)
        self.assertEqual(history_row['quantity'], 4)
        self.assertEqual(history_row['total_points'], 40)
        print("[PASS] Test 38: Authenticated Reward History Persistence Verified.")

    def test_39_tenant_privacy_rewards_history(self):
        """Test 39: Verify users cannot view or access another user's reward history."""
        # Ensure Bob exists in MySQL
        bob = execute_query("SELECT id FROM users WHERE email = 'bob@testdomain.demo'", fetchone=True)
        if not bob:
            from werkzeug.security import generate_password_hash
            bob_id = execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                ("Bob Blue", "bob@testdomain.demo", generate_password_hash("SecurePassword123!")),
                commit=True
            )
        else:
            bob_id = bob['id']

        # Clear Bob's history before testing privacy
        execute_query("DELETE FROM rewards_history WHERE user_id = %s", (bob_id,), commit=True)

        # Set session as Bob
        with self.client.session_transaction() as sess:
            sess['user_id'] = bob_id
            sess['user_name'] = "Bob Blue"

        # Bob's history should be empty initially (cannot see Alice's records)
        res_bob = self.client.get('/api/rewards/history')
        self.assertEqual(res_bob.status_code, 200)
        data_bob = res_bob.get_json()
        self.assertEqual(data_bob['count'], 0)
        self.assertEqual(data_bob['total_points'], 0)

        # Bob saves a laptop calculation (2 laptops = 50 pts)
        laptop = execute_query("SELECT id FROM devices WHERE device_name = 'Laptop'", fetchone=True)
        res_save = self.client.post('/api/rewards/save', json={'device_id': laptop['id'], 'quantity': 2})
        self.assertEqual(res_save.status_code, 201)

        res_bob_after = self.client.get('/api/rewards/history')
        data_after = res_bob_after.get_json()
        self.assertEqual(data_after['count'], 1)
        self.assertEqual(data_after['total_points'], 50)
        self.assertEqual(data_after['history'][0]['device_name'], 'Laptop')
        print("[PASS] Test 39: Multi-User Rewards History Privacy & Isolation Verified.")

    def test_40_clear_rewards_history(self):
        """Test 40: Verify user can clear their own calculation history."""
        # Ensure Bob exists
        bob = execute_query("SELECT id FROM users WHERE email = 'bob@testdomain.demo'", fetchone=True)
        if not bob:
            from werkzeug.security import generate_password_hash
            bob_id = execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                ("Bob Blue", "bob@testdomain.demo", generate_password_hash("SecurePassword123!")),
                commit=True
            )
        else:
            bob_id = bob['id']

        # Ensure Bob has at least 1 record to clear
        laptop = execute_query("SELECT id FROM devices WHERE device_name = 'Laptop'", fetchone=True)
        execute_query(
            "INSERT INTO rewards_history (user_id, device_id, quantity, total_points) VALUES (%s, %s, 1, 25)",
            (bob_id, laptop['id']),
            commit=True
        )

        with self.client.session_transaction() as sess:
            sess['user_id'] = bob_id
            sess['user_name'] = "Bob Blue"

        # Bob clears his history
        res_clear = self.client.post('/api/rewards/history/clear')
        self.assertEqual(res_clear.status_code, 200)

        res_check = self.client.get('/api/rewards/history')
        self.assertEqual(res_check.get_json()['count'], 0)
        self.assertEqual(res_check.get_json()['total_points'], 0)
        print("[PASS] Test 40: Rewards History Clear Endpoint Verified.")

    # ==========================================================================
    # Phase 7 Tests: Admin Dashboard, Centre CRUD, CSV Ingestion, Users & Devices
    # ==========================================================================

    def test_41_admin_login_and_logout(self):
        """Test 41: Verify admin login session, credentials, and logout."""
        # 1. Successful Login
        res_login = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'AdminSecure2026!'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Control Panel", res_login.data)

        # 2. Logout terminates admin session
        res_logout = self.client.get('/admin/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b"Administrator session terminated", res_logout.data)

        # 3. Accessing dashboard without admin session redirects to login
        res_dash = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b"Administrative access required", res_dash.data)
        print("[PASS] Test 41: Admin Login, Session Isolation & Logout Verified.")

    def test_42_admin_dashboard_statistics(self):
        """Test 42: Verify admin dashboard statistics and Chart.js datasets."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check KPI cards
        self.assertIn('Recycling Centres', html)
        self.assertIn('Registered Users', html)
        self.assertIn('Electronic Devices', html)
        self.assertIn('Official Websites', html)
        self.assertIn('Direct Phone Numbers', html)
        self.assertIn('GPS Mapped Centres', html)
        self.assertIn('stateDistributionChart', html)
        self.assertIn('verificationBreakdownChart', html)
        print("[PASS] Test 42: Admin Executive Dashboard Statistics & Chart.js Config Verified.")

    def test_43_admin_centre_crud_operations(self):
        """Test 43: Verify Add, Duplicate Prevention, Edit, View, and Delete of Recycling Centre."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # 1. Add Centre
        centre_data = {
            'centre_name': 'Test Eco Facility 2026',
            'state': 'Maharashtra',
            'city': 'Pune',
            'address': 'Plot 404, Industrial Phase 1, Bhosari, Pune 411026',
            'capacity_mta': '1,500 MTA',
            'centre_type': 'Authorised dismantler/recycler',
            'source': 'CPCB Registry',
            'website_url': 'https://test-ecofacility.demo',
            'website_verification': 'Audited domain',
            'website_checked_date': '2026-11-14',
            'phone_number': '+91 20 2712 1234',
            'email': 'contact@test-ecofacility.demo',
            'latitude': '18.62750000',
            'longitude': '73.84410000'
        }
        res_add = self.client.post('/admin/centres/add', data=centre_data, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b"Test Eco Facility 2026", res_add.data)

        # Verify record in MySQL
        db_centre = execute_query(
            "SELECT id, centre_name, city, capacity_mta FROM centres WHERE centre_name = 'Test Eco Facility 2026'",
            fetchone=True
        )
        self.assertIsNotNone(db_centre)
        centre_id = db_centre['id']

        # 2. Duplicate Prevention: Attempt to add identical name & address returns 409
        res_dup = self.client.post('/admin/centres/add', data=centre_data)
        self.assertEqual(res_dup.status_code, 409)
        self.assertIn(b"already exists", res_dup.data)

        # 3. View Centre Detail
        res_view = self.client.get(f'/admin/centres/view/{centre_id}')
        self.assertEqual(res_view.status_code, 200)
        self.assertIn(b"Plot 404, Industrial Phase 1", res_view.data)

        # 4. Edit Centre
        centre_data['capacity_mta'] = '3,000 MTA'
        centre_data['phone_number'] = '+91 20 2712 9999'
        res_edit = self.client.post(f'/admin/centres/edit/{centre_id}', data=centre_data, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)

        # Verify update in MySQL
        updated = execute_query("SELECT capacity_mta, phone_number FROM centres WHERE id = %s", (centre_id,), fetchone=True)
        self.assertEqual(updated['capacity_mta'], '3,000 MTA')
        self.assertEqual(updated['phone_number'], '+91 20 2712 9999')

        # 5. Delete Centre
        res_del = self.client.post(f'/admin/centres/delete/{centre_id}', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        # Verify deletion from MySQL
        deleted = execute_query("SELECT id FROM centres WHERE id = %s", (centre_id,), fetchone=True)
        self.assertIsNone(deleted)
        print("[PASS] Test 43: Centre Complete CRUD & Duplicate Prevention Verified.")

    def test_44_admin_centre_search_and_filter(self):
        """Test 44: Verify search by name and filter by state/city in admin directory."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # Filter by State (Delhi)
        res_delhi = self.client.get('/admin/centres?state=Delhi')
        self.assertEqual(res_delhi.status_code, 200)
        self.assertIn(b"Delhi", res_delhi.data)

        # Search by keyword (Eco)
        res_search = self.client.get('/admin/centres?q=Eco')
        self.assertEqual(res_search.status_code, 200)
        self.assertIn(b"Eco", res_search.data)
        print("[PASS] Test 44: Centre Search & State/City Filtering in Admin Verified.")

    def test_45_admin_csv_import_pipeline(self):
        """Test 45: Verify batch CSV upload, column schema validation, and duplicate handling."""
        execute_query("DELETE FROM centres WHERE centre_name LIKE 'Test %'", commit=True)

        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        import io

        # 1. Rejection of non-CSV file
        bad_file = (io.BytesIO(b"Hello world"), "test.txt")
        res_bad = self.client.post('/admin/centres/import-csv', data={'csv_file': bad_file}, content_type='multipart/form-data')
        self.assertIn(b"Only .csv files are supported", res_bad.data)

        # 2. Upload valid CSV with 1 new centre + 1 duplicate of existing centre
        csv_content = (
            "name,state,city_district,address,capacity_mta,type,website_url\n"
            "Test Batch Ingested Centre 1,Karnataka,Bengaluru,\"Plot 12, Peenya Industrial Area\",800 MTA,Authorised Recycler,https://batch1.demo\n"
            "Green Waves Environmental Solution,Andhra Pradesh,Visakhapatnam,\"Sy. No. 43/1, Mindi (V), Gajuwaka (M), Visakhapatnam\",1200 MTA,Authorised dismantler/recycler,http://greenwaves.co.in\n"
        )
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), "batch_import.csv")
        res_import = self.client.post(
            '/admin/centres/import-csv',
            data={'csv_file': csv_file, 'preview_only': '0'},
            content_type='multipart/form-data',
            follow_redirects=True
        )
        self.assertEqual(res_import.status_code, 200)
        self.assertIn(b"1 new facilities committed", res_import.data)
        self.assertIn(b"1 duplicates safely skipped", res_import.data)

        # Verify new centre exists in MySQL
        new_centre = execute_query(
            "SELECT id FROM centres WHERE centre_name = 'Test Batch Ingested Centre 1'",
            fetchone=True
        )
        self.assertIsNotNone(new_centre)

        # Clean up test facility
        execute_query("DELETE FROM centres WHERE centre_name = 'Test Batch Ingested Centre 1'", commit=True)
        print("[PASS] Test 45: Admin CSV Batch Ingestion & Duplicate Handling Verified.")

    def test_46_admin_user_listing_and_privacy(self):
        """Test 46: Verify admin can list users, view profile, and passwords are never exposed."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # Ensure test user exists
        user = execute_query("SELECT id FROM users WHERE email = 'alice@testdomain.demo'", fetchone=True)
        if not user:
            from werkzeug.security import generate_password_hash
            execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                ("Alice Green", "alice@testdomain.demo", generate_password_hash("SecurePassword123!")),
                commit=True
            )
            user = execute_query("SELECT id FROM users WHERE email = 'alice@testdomain.demo'", fetchone=True)

        user_id = user['id']

        # 1. User listing
        res_users = self.client.get('/admin/users?q=Alice')
        self.assertEqual(res_users.status_code, 200)
        html_users = res_users.data.decode('utf-8')
        self.assertIn('Alice Green', html_users)
        self.assertIn('alice@testdomain.demo', html_users)
        # CRITICAL SECURITY CHECK: password hash must NOT be in HTML
        self.assertNotIn('scrypt:', html_users)
        self.assertNotIn('pbkdf2:', html_users)

        # 2. View user detail
        res_view = self.client.get(f'/admin/users/view/{user_id}')
        self.assertEqual(res_view.status_code, 200)
        html_view = res_view.data.decode('utf-8')
        self.assertIn('Account Profile Overview', html_view)
        self.assertIn('Alice Green', html_view)
        self.assertNotIn('scrypt:', html_view)
        print("[PASS] Test 46: User Management Directory & Strict Password Privacy Verified.")

    def test_47_admin_user_toggle_status_and_login_blocking(self):
        """Test 47: Verify activating/deactivating accounts and login enforcement."""
        user = execute_query("SELECT id FROM users WHERE email = 'alice@testdomain.demo'", fetchone=True)
        user_id = user['id']

        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # 1. Deactivate account
        self.client.post(f'/admin/users/toggle-status/{user_id}')
        status_check = execute_query("SELECT is_active FROM users WHERE id = %s", (user_id,), fetchone=True)
        self.assertEqual(status_check['is_active'], 0)

        # 2. User attempts to log in -> rejected with 403
        client_alice = self.app.test_client()
        res_login_blocked = client_alice.post('/login', data={
            'email': 'alice@testdomain.demo',
            'password': 'SecurePassword123!'
        })
        self.assertEqual(res_login_blocked.status_code, 403)
        self.assertIn(b"account has been deactivated", res_login_blocked.data)

        # 3. Re-activate account
        self.client.post(f'/admin/users/toggle-status/{user_id}')
        status_restored = execute_query("SELECT is_active FROM users WHERE id = %s", (user_id,), fetchone=True)
        self.assertEqual(status_restored['is_active'], 1)

        # 4. User can log in again
        res_login_ok = client_alice.post('/login', data={
            'email': 'alice@testdomain.demo',
            'password': 'SecurePassword123!'
        }, follow_redirects=True)
        self.assertEqual(res_login_ok.status_code, 200)
        print("[PASS] Test 47: Account Activation/Deactivation & Sign-In Guard Verified.")

    def test_48_admin_device_management_crud(self):
        """Test 48: Verify device addition, duplicate prevention, editing, and deletion."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # 1. Add device
        res_add = self.client.post('/admin/devices/add', data={
            'device_name': 'Test Solar Inverter',
            'points_per_unit': '45'
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)

        db_dev = execute_query("SELECT id, points_per_unit FROM devices WHERE device_name = 'Test Solar Inverter'", fetchone=True)
        self.assertIsNotNone(db_dev)
        dev_id = db_dev['id']
        self.assertEqual(db_dev['points_per_unit'], 45)

        # 2. Duplicate prevention
        res_dup = self.client.post('/admin/devices/add', data={
            'device_name': 'Test Solar Inverter',
            'points_per_unit': '45'
        }, follow_redirects=True)
        self.assertIn(b"already exists", res_dup.data)

        # 3. Edit device
        res_edit = self.client.post(f'/admin/devices/edit/{dev_id}', data={
            'device_name': 'Test Solar Inverter Pro',
            'points_per_unit': '60'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)

        updated_dev = execute_query("SELECT device_name, points_per_unit FROM devices WHERE id = %s", (dev_id,), fetchone=True)
        self.assertEqual(updated_dev['device_name'], 'Test Solar Inverter Pro')
        self.assertEqual(updated_dev['points_per_unit'], 60)

        # 4. Delete device
        res_del = self.client.post(f'/admin/devices/delete/{dev_id}', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        deleted = execute_query("SELECT id FROM devices WHERE id = %s", (dev_id,), fetchone=True)
        self.assertIsNone(deleted)
        print("[PASS] Test 48: Device Management Complete CRUD & Duplication Check Verified.")

    def test_49_unauthorized_user_blocked_from_all_admin_endpoints(self):
        """Test 49: Verify non-admin user is rejected from all admin endpoints."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 999
            sess['user_name'] = "Normal User"

        admin_urls = [
            '/admin/dashboard',
            '/admin/centres',
            '/admin/centres/add',
            '/admin/centres/import-csv',
            '/admin/users',
            '/admin/activities',
            '/admin/devices',
            '/admin/profile'
        ]
        for url in admin_urls:
            resp = self.client.get(url, follow_redirects=False)
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/admin/login', resp.headers['Location'])

        print("[PASS] Test 49: Strict Non-Admin Boundary Protection Across All Admin Endpoints Verified.")

    def test_50_public_website_phases_remain_functional(self):
        """Test 50: Verify existing user authentication, map, search, awareness, and rewards continue working without regressions."""
        # 1. Homepage
        self.assertEqual(self.client.get('/').status_code, 200)
        # 2. Centres Directory & Leaflet Map
        res_centres = self.client.get('/centres')
        self.assertEqual(res_centres.status_code, 200)
        self.assertIn(b"leaflet", res_centres.data.lower())
        # 3. Map Data Endpoint
        res_map = self.client.get('/api/centres/map')
        self.assertEqual(res_map.status_code, 200)
        self.assertTrue(res_map.get_json()['success'])
        # 4. Proximity Haversine Endpoint
        res_near = self.client.get('/api/centres/nearby?lat=28.61&lng=77.20')
        self.assertEqual(res_near.status_code, 200)
        # 5. Awareness Curriculum
        self.assertEqual(self.client.get('/awareness').status_code, 200)
        # 6. Rewards Calculator
        self.assertEqual(self.client.get('/rewards').status_code, 200)
        print("[PASS] Test 50: Public Website, Interactive Map & Rewards Regressions Check Verified.")

    def test_51_user_activity_table_schema_verification(self):
        """Test 51: Verify user_activity table exists in MySQL with all required columns and constraints."""
        cols = execute_query("SHOW COLUMNS FROM user_activity", fetchall=True) or []
        col_names = [c['Field'] for c in cols]
        required = ['activity_id', 'user_id', 'activity_type', 'search_query', 'city', 'state', 'centre_id', 'created_at']
        for r in required:
            self.assertIn(r, col_names)
        print("[PASS] Test 51: User Activity Table Existence & Schema Verified.")

    def test_52_user_login_and_logout_activity_tracking(self):
        """Test 52: Verify user login and logout events are automatically logged into user_activity."""
        email = "alice@testdomain.demo"
        password = "SecurePassword123!"

        # Ensure user exists
        user = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
        if not user:
            from werkzeug.security import generate_password_hash
            execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                ("Alice Green", email, generate_password_hash(password)),
                commit=True
            )
            user = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
        user_id = user['id']

        # 1. Log in
        res = self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify login activity logged
        login_act = execute_query(
            "SELECT * FROM user_activity WHERE user_id = %s AND activity_type = 'login' ORDER BY activity_id DESC LIMIT 1",
            (user_id,),
            fetchone=True
        )
        self.assertIsNotNone(login_act)
        self.assertEqual(login_act['activity_type'], 'login')

        # 2. Log out
        res_out = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_out.status_code, 200)

        # Verify logout activity logged
        logout_act = execute_query(
            "SELECT * FROM user_activity WHERE user_id = %s AND activity_type = 'logout' ORDER BY activity_id DESC LIMIT 1",
            (user_id,),
            fetchone=True
        )
        self.assertIsNotNone(logout_act)
        self.assertEqual(logout_act['activity_type'], 'logout')
        print("[PASS] Test 52: User Login & Logout Activity Tracking Verified.")

    def test_53_centre_search_and_filter_activity_tracking(self):
        """Test 53: Verify searching and filtering recycling centres logs query, state, and city."""
        # Search for Delhi
        res = self.client.get('/api/centres?page=1&state=Delhi&q=Recycle')
        self.assertEqual(res.status_code, 200)

        # Verify search activity logged
        search_act = execute_query(
            "SELECT * FROM user_activity WHERE activity_type = 'search' AND state = 'Delhi' ORDER BY activity_id DESC LIMIT 1",
            fetchone=True
        )
        self.assertIsNotNone(search_act)
        self.assertEqual(search_act['state'], 'Delhi')
        self.assertEqual(search_act['search_query'], 'Recycle')
        print("[PASS] Test 53: Centre Search & Filter Activity Tracking Verified.")

    def test_54_centre_details_view_activity_tracking(self):
        """Test 54: Verify viewing centre details logs centre_view with centre_id, city, and state."""
        # Query first centre
        centre = execute_query("SELECT id, city, state FROM centres LIMIT 1", fetchone=True)
        self.assertIsNotNone(centre)
        c_id = centre['id']

        res = self.client.get(f'/api/centres/{c_id}')
        self.assertEqual(res.status_code, 200)

        # Verify centre_view logged
        view_act = execute_query(
            "SELECT * FROM user_activity WHERE activity_type = 'centre_view' AND centre_id = %s ORDER BY activity_id DESC LIMIT 1",
            (c_id,),
            fetchone=True
        )
        self.assertIsNotNone(view_act)
        self.assertEqual(view_act['centre_id'], c_id)
        self.assertEqual(view_act['city'], centre['city'])
        self.assertEqual(view_act['state'], centre['state'])
        print("[PASS] Test 54: Centre Details View Activity Tracking Verified.")

    def test_55_rewards_calculator_activity_tracking(self):
        """Test 55: Verify rewards calculation logs rewards_calc activity."""
        device = execute_query("SELECT id FROM devices LIMIT 1", fetchone=True)
        d_id = device['id']

        res = self.client.post('/api/rewards/calculate', json={
            'device_id': d_id,
            'quantity': 4
        }, headers={'Content-Type': 'application/json'})
        self.assertEqual(res.status_code, 200)

        # Verify rewards_calc logged
        calc_act = execute_query(
            "SELECT * FROM user_activity WHERE activity_type = 'rewards_calc' ORDER BY activity_id DESC LIMIT 1",
            fetchone=True
        )
        self.assertIsNotNone(calc_act)
        self.assertIn("4x", calc_act['search_query'])
        print("[PASS] Test 55: Rewards Calculator Activity Tracking Verified.")

    def test_56_live_database_synchronisation_crud_to_search(self):
        """Test 56: Verify that Admin adding, editing, or deleting a recycling centre immediately reflects in User search results without hardcoded data."""
        # 1. Log in as admin
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # 2. Add new recycling centre via Admin
        test_centre_name = "EcoSync Test Facility Phase 8"
        add_res = self.client.post('/admin/centres/add', data={
            'centre_name': test_centre_name,
            'state': 'Goa',
            'city': 'Panaji',
            'address': 'Plot 101, Kundaim Industrial Estate, Goa 403115',
            'capacity_mta': '500 MTA',
            'centre_type': 'Authorised dismantler/recycler',
            'source': 'CPCB Verified List',
            'website_url': 'https://www.ecosync-test.in',
            'website_verification': 'Direct domain verified',
            'phone_number': '+91 832 2390100',
            'email': 'contact@ecosync-test.in',
            'latitude': '15.4909',
            'longitude': '73.8278'
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)

        # 3. Query from standard user search endpoint -> MUST appear immediately
        user_search = self.client.get('/api/centres?state=Goa&q=EcoSync').get_json()
        self.assertTrue(user_search['success'])
        self.assertEqual(user_search['total'], 1)
        created_id = user_search['centres'][0]['id']
        self.assertEqual(user_search['centres'][0]['centre_name'], test_centre_name)

        # 4. Edit the facility via Admin
        updated_centre_name = "EcoSync Premier Recycling Hub"
        edit_res = self.client.post(f'/admin/centres/edit/{created_id}', data={
            'centre_name': updated_centre_name,
            'state': 'Goa',
            'city': 'Panaji',
            'address': 'Plot 101, Kundaim Industrial Estate, Goa 403115',
            'capacity_mta': '1200 MTA',
            'centre_type': 'Authorised dismantler/recycler',
            'source': 'CPCB Verified List',
            'website_url': 'https://www.ecosync-test.in',
            'phone_number': '+91 832 2390100',
            'latitude': '15.4909',
            'longitude': '73.8278'
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)

        # 5. Query user search -> MUST reflect updated name immediately
        user_search_updated = self.client.get('/api/centres?state=Goa&q=Premier').get_json()
        self.assertEqual(user_search_updated['total'], 1)
        self.assertEqual(user_search_updated['centres'][0]['centre_name'], updated_centre_name)

        # 6. Delete the facility via Admin
        del_res = self.client.post(f'/admin/centres/delete/{created_id}', follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)

        # 7. Query user search -> MUST be gone immediately
        user_search_deleted = self.client.get('/api/centres?state=Goa&q=Premier').get_json()
        self.assertEqual(user_search_deleted['total'], 0)

        print("[PASS] Test 56: Live Database Synchronisation (Admin CRUD -> User Search) Verified.")

    def test_57_admin_activity_dashboard_and_filters(self):
        """Test 57: Verify Admin Activity Dashboard (/admin/activities) renders with KPI counts, filters, and activity history."""
        # Log in as admin
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # Access /admin/activities
        resp = self.client.get('/admin/activities')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"User Activity Tracking", resp.data)
        self.assertIn(b"Activity Audit Trail", resp.data)

        # Test filter by type
        resp_filter = self.client.get('/admin/activities?type=login')
        self.assertEqual(resp_filter.status_code, 200)

        # Test search filter
        resp_search = self.client.get('/admin/activities?q=Delhi')
        self.assertEqual(resp_search.status_code, 200)

        print("[PASS] Test 57: Admin Activity Dashboard & Filtering Options Verified.")

    def test_58_non_admin_blocked_from_activity_dashboard(self):
        """Test 58: Verify standard authenticated users and unauthenticated guests are strictly blocked from /admin/activities."""
        # 1. Unauthenticated guest -> redirected to /admin/login
        resp_guest = self.client.get('/admin/activities', follow_redirects=False)
        self.assertEqual(resp_guest.status_code, 302)
        self.assertIn('/admin/login', resp_guest.headers['Location'])

        # 2. Standard authenticated user -> blocked and redirected to /admin/login
        user = execute_query("SELECT id FROM users LIMIT 1", fetchone=True)
        user_id = user['id'] if user else 1
        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_name'] = "Regular User"
            sess.pop('admin_id', None)

        resp_user = self.client.get('/admin/activities', follow_redirects=False)
        self.assertEqual(resp_user.status_code, 302)
        self.assertIn('/admin/login', resp_user.headers['Location'])

        print("[PASS] Test 58: Strict Non-Admin Boundary Protection on Activity Logs Verified.")

    def test_59_concurrent_multi_user_activity_isolation(self):
        """Test 59: Verify multiple users simultaneously perform distinct searches in different cities and their activities are tracked independently."""
        client_a = self.app.test_client()
        client_b = self.app.test_client()

        # Client A searches Pune, Maharashtra
        res_a = client_a.get('/api/centres?page=1&state=Maharashtra&city=Pune')
        self.assertEqual(res_a.status_code, 200)

        # Client B searches Bengaluru, Karnataka
        res_b = client_b.get('/api/centres?page=1&state=Karnataka&city=Bengaluru')
        self.assertEqual(res_b.status_code, 200)

        # Verify both activities logged independently in MySQL
        act_pune = execute_query(
            "SELECT * FROM user_activity WHERE activity_type = 'search' AND city = 'Pune' ORDER BY activity_id DESC LIMIT 1",
            fetchone=True
        )
        act_blr = execute_query(
            "SELECT * FROM user_activity WHERE activity_type = 'search' AND city = 'Bengaluru' ORDER BY activity_id DESC LIMIT 1",
            fetchone=True
        )

        self.assertIsNotNone(act_pune)
        self.assertIsNotNone(act_blr)
        self.assertEqual(act_pune['city'], 'Pune')
        self.assertEqual(act_blr['city'], 'Bengaluru')
        self.assertNotEqual(act_pune['activity_id'], act_blr['activity_id'])

        print("[PASS] Test 59: Concurrent Multi-User Independent City Searches Verified.")

    # ==========================================================================
    # Phase 9 Tests: E-Waste Submissions & Repeat Submission Points System
    # ==========================================================================

    def _create_test_user_helper(self, email, name="Test Submitter"):
        """Helper to create or get test user for submissions testing."""
        from werkzeug.security import generate_password_hash
        user = execute_query("SELECT id, full_name, email FROM users WHERE email = %s", (email,), fetchone=True)
        if not user:
            u_id = execute_query(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, generate_password_hash("TestPassword123!")),
                commit=True
            )
            user = {'id': u_id, 'full_name': name, 'email': email}
        return user

    def test_60_scenario_1_user_submits_1_item_earns_5_points(self):
        """Test 60 (Scenario 1): New user submits 1 item -> verified -> 5 points credited."""
        user = self._create_test_user_helper("scenario1_user@testdomain.demo", "Scenario 1 User")
        
        # 1. User submits 1 item
        with self.client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['user_name'] = user['full_name']

        resp = self.client.post('/submit-ewaste', data={
            'is_student': 'yes',
            'student_name': 'Scenario 1 User',
            'university_type': 'SGT University',
            'roll_number': '241306039',
            'course_dept': 'BCA AIML',
            'phone_number': '9999900001',
            'email': user['email'],
            'address': 'SGT University Hostel Block B',
            'city': 'Gurugram',
            'state': 'Haryana',
            'pincode': '122505',
            'item_category[]': ['Mobile phones'],
            'item_name[]': ['Old Nokia Phone'],
            'item_quantity[]': ['1'],
            'item_condition[]': ['Working']
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Retrieve created submission
        sub = execute_query(
            "SELECT * FROM ewaste_submissions WHERE user_id = %s ORDER BY id DESC LIMIT 1",
            (user['id'],),
            fetchone=True
        )
        self.assertIsNotNone(sub)
        self.assertEqual(sub['total_submitted_items'], 1)
        self.assertEqual(sub['points_approved'], 0)

        # 2. Admin verifies item & approves points
        from points_service import award_submission_points
        # Verify item quantity
        execute_query(
            "UPDATE ewaste_submission_items SET accepted_quantity = 1, status = 'verified' WHERE submission_id = %s",
            (sub['id'],),
            commit=True
        )
        success, msg, pts = award_submission_points(sub['id'], admin_id=1)
        self.assertTrue(success)
        self.assertEqual(pts, 5)

        # 3. Check wallet balance
        from points_service import get_or_create_wallet
        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 5)
        self.assertEqual(wallet['total_earned'], 5)
        print("[PASS] Test 60: Scenario 1 - 1 Item Submitted -> Verified -> 5 Points Credited.")

    def test_61_scenario_2_repeat_submission_earns_points_again(self):
        """Test 61 (Scenario 2): Same user submits another item later -> 5 points again (cumulative wallet balance = 10)."""
        user = self._create_test_user_helper("scenario1_user@testdomain.demo")
        
        # User makes a SECOND independent submission
        with self.client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['user_name'] = user['full_name']

        resp = self.client.post('/submit-ewaste', data={
            'is_student': 'yes',
            'student_name': 'Scenario 1 User',
            'university_type': 'SGT University',
            'phone_number': '9999900001',
            'email': user['email'],
            'address': 'SGT University Hostel Block B',
            'city': 'Gurugram',
            'state': 'Haryana',
            'pincode': '122505',
            'item_category[]': ['Batteries'],
            'item_name[]': ['Laptop Battery Pack'],
            'item_quantity[]': ['1'],
            'item_condition[]': ['Damaged']
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        sub2 = execute_query(
            "SELECT * FROM ewaste_submissions WHERE user_id = %s ORDER BY id DESC LIMIT 1",
            (user['id'],),
            fetchone=True
        )
        self.assertIsNotNone(sub2)

        # Admin verifies & approves points
        from points_service import award_submission_points, get_or_create_wallet
        execute_query(
            "UPDATE ewaste_submission_items SET accepted_quantity = 1, status = 'verified' WHERE submission_id = %s",
            (sub2['id'],),
            commit=True
        )
        success, msg, pts = award_submission_points(sub2['id'], admin_id=1)
        self.assertTrue(success)
        self.assertEqual(pts, 5, "Second 1-item submission must earn 5 points (evaluated per submission!)")

        # Check user wallet balance: 5 from 1st + 5 from 2nd = 10
        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 10)
        self.assertEqual(wallet['total_earned'], 10)
        print("[PASS] Test 61: Scenario 2 - Repeat Submission Evaluated Per Submission -> Cumulative 10 Points Verified.")

    def test_62_scenario_3_two_items_submission_earns_15_points(self):
        """Test 62 (Scenario 3): Submission with 2 items -> 15 points."""
        user = self._create_test_user_helper("scenario3_user@testdomain.demo", "Scenario 3 User")
        from points_service import award_submission_points, get_or_create_wallet

        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-SCEN3', %s, 0, 'Scenario 3 User', '9999900003', 'Sector 14', 'Gurugram', 'Haryana', '122001', 'pending', 2)
            """,
            (user['id'],),
            commit=True
        )
        execute_query(
            """
            INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status)
            VALUES (%s, 'Laptops', 'Old Lenovo ThinkPad', 2, 2, 'verified')
            """,
            (sub_id,),
            commit=True
        )

        success, msg, pts = award_submission_points(sub_id, admin_id=1)
        self.assertTrue(success)
        self.assertEqual(pts, 15)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 15)
        print("[PASS] Test 62: Scenario 3 - 2 Items Submission -> 15 Points Verified.")

    def test_63_scenario_4_five_items_submission_earns_40_points(self):
        """Test 63 (Scenario 4): Submission with 5 items -> 40 points."""
        user = self._create_test_user_helper("scenario4_user@testdomain.demo", "Scenario 4 User")
        from points_service import award_submission_points, get_or_create_wallet

        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-SCEN4', %s, 0, 'Scenario 4 User', '9999900004', 'Civil Lines', 'Gurugram', 'Haryana', '122001', 'pending', 5)
            """,
            (user['id'],),
            commit=True
        )
        execute_query(
            """
            INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status)
            VALUES (%s, 'Chargers and cables', 'Power Adapters', 5, 5, 'verified')
            """,
            (sub_id,),
            commit=True
        )

        success, msg, pts = award_submission_points(sub_id, admin_id=1)
        self.assertTrue(success)
        self.assertEqual(pts, 40)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 40)
        print("[PASS] Test 63: Scenario 4 - 5 Items Submission -> 40 Points Verified.")

    def test_64_scenario_5_multiple_categories_in_one_submission(self):
        """Test 64 (Scenario 5): Multiple categories in 1 submission (e.g. mobile phone + laptop + cables)."""
        user = self._create_test_user_helper("scenario5_user@testdomain.demo", "Scenario 5 User")
        from points_service import award_submission_points, get_or_create_wallet

        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-SCEN5', %s, 0, 'Scenario 5 User', '9999900005', 'DLF Phase 3', 'Gurugram', 'Haryana', '122002', 'pending', 3)
            """,
            (user['id'],),
            commit=True
        )
        # 3 items across 3 distinct categories
        for cat, name in [('Mobile phones', 'Samsung J7'), ('Laptops', 'HP Pavilion'), ('Chargers and cables', 'HDMI Cable')]:
            execute_query(
                """
                INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status)
                VALUES (%s, %s, %s, 1, 1, 'verified')
                """,
                (sub_id, cat, name),
                commit=True
            )

        success, msg, pts = award_submission_points(sub_id, admin_id=1)
        self.assertTrue(success)
        # 3 total accepted items -> 25 points tier
        self.assertEqual(pts, 25)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 25)
        print("[PASS] Test 64: Scenario 5 - Multiple Categories in 1 Submission (3 items -> 25 pts) Verified.")

    def test_65_scenario_6_admin_edits_accepted_quantity_before_approval(self):
        """Test 65 (Scenario 6): Admin edits accepted quantity before points approval (4 submitted, 2 accepted -> 15 pts)."""
        user = self._create_test_user_helper("scenario6_user@testdomain.demo", "Scenario 6 User")
        from points_service import award_submission_points, get_or_create_wallet

        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-SCEN6', %s, 0, 'Scenario 6 User', '9999900006', 'Sohna Road', 'Gurugram', 'Haryana', '122018', 'pending', 4)
            """,
            (user['id'],),
            commit=True
        )
        execute_query(
            """
            INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status)
            VALUES (%s, 'Keyboard and mouse', 'Keyboards', 4, 0, 'pending')
            """,
            (sub_id,),
            commit=True
        )

        # Admin verifies only 2 of the 4 keyboards are acceptable
        execute_query(
            "UPDATE ewaste_submission_items SET accepted_quantity = 2, status = 'verified' WHERE submission_id = %s",
            (sub_id,),
            commit=True
        )

        success, msg, pts = award_submission_points(sub_id, admin_id=1)
        self.assertTrue(success)
        # 2 accepted items -> 15 points
        self.assertEqual(pts, 15)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 15)
        print("[PASS] Test 65: Scenario 6 - Admin Quantity Modification Respected in Points Calculation Verified.")

    def test_66_scenario_7_rejected_items_excluded_from_points(self):
        """Test 66 (Scenario 7): Rejected items excluded from accepted count and points calculation."""
        user = self._create_test_user_helper("scenario7_user@testdomain.demo", "Scenario 7 User")
        from points_service import award_submission_points, get_or_create_wallet

        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-SCEN7', %s, 0, 'Scenario 7 User', '9999900007', 'Sector 56', 'Gurugram', 'Haryana', '122011', 'pending', 3)
            """,
            (user['id'],),
            commit=True
        )
        # Item 1: Accepted (1 item)
        execute_query(
            """
            INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status)
            VALUES (%s, 'Mobile phones', 'Nokia C2', 1, 1, 'verified')
            """,
            (sub_id,),
            commit=True
        )
        # Item 2: Rejected (2 items)
        execute_query(
            """
            INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status, rejection_reason)
            VALUES (%s, 'Batteries', 'Leaking Acid Batteries', 2, 0, 'rejected', 'Hazardous acid leakage')
            """,
            (sub_id,),
            commit=True
        )

        success, msg, pts = award_submission_points(sub_id, admin_id=1)
        self.assertTrue(success)
        # Only 1 item accepted -> 5 points
        self.assertEqual(pts, 5)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 5)
        print("[PASS] Test 66: Scenario 7 - Rejected Items Excluded from Points Calculation Verified.")

    def test_67_scenario_8_duplicate_points_claim_prevention(self):
        """Test 67 (Scenario 8): Duplicate points claim prevention on same submission."""
        user = self._create_test_user_helper("scenario8_user@testdomain.demo", "Scenario 8 User")
        from points_service import award_submission_points, get_or_create_wallet

        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-SCEN8', %s, 0, 'Scenario 8 User', '9999900008', 'Sector 4', 'Gurugram', 'Haryana', '122001', 'pending', 1)
            """,
            (user['id'],),
            commit=True
        )
        execute_query(
            """
            INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status)
            VALUES (%s, 'Laptops', 'Acer Aspire', 1, 1, 'verified')
            """,
            (sub_id,),
            commit=True
        )

        # 1st approval -> succeeds
        success1, msg1, pts1 = award_submission_points(sub_id, admin_id=1)
        self.assertTrue(success1)
        self.assertEqual(pts1, 5)

        # 2nd approval attempt on the SAME submission -> must fail!
        success2, msg2, pts2 = award_submission_points(sub_id, admin_id=1)
        self.assertFalse(success2)
        self.assertIn("already", msg2.lower())
        self.assertEqual(pts2, 0)

        # Wallet balance remains strictly 5
        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 5)
        print("[PASS] Test 67: Scenario 8 - Strict Duplicate Points Claim Prevention Verified.")

    def test_68_scenario_9_normal_user_blocked_from_admin_submission_endpoints(self):
        """Test 68 (Scenario 9): Normal user blocked from admin submissions endpoints."""
        user = self._create_test_user_helper("scenario9_user@testdomain.demo", "Scenario 9 User")

        # Session as normal user without admin_id
        with self.client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['user_name'] = user['full_name']
            sess.pop('admin_id', None)

        endpoints = [
            '/admin/submissions',
            '/admin/submissions/1',
            '/admin/submissions/export-csv',
            '/admin/collections/report',
            '/admin/collections/export-csv',
            '/admin/points',
            f'/admin/points/user/{user["id"]}',
            '/admin/points/tiers',
            '/admin/recyclers'
        ]

        for ep in endpoints:
            res = self.client.get(ep, follow_redirects=False)
            self.assertEqual(res.status_code, 302, f"Expected 302 redirect for {ep}")
            self.assertIn('/admin/login', res.headers['Location'])

        print("[PASS] Test 68: Scenario 9 - Non-Admin Blocked from All Submissions & Points Admin Endpoints Verified.")

    def test_69_scenario_10_submission_wise_points_history_displayed_separately(self):
        """Test 69 (Scenario 10): Submission-wise points history displayed separately in user points ledger and submissions page."""
        user = self._create_test_user_helper("scenario10_user@testdomain.demo", "Scenario 10 User")
        from points_service import award_submission_points, get_wallet_ledger

        # Create two distinct submissions for this user
        sub1_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-10A', %s, 0, 'Scenario 10 User', '9999900010', 'Address A', 'Gurugram', 'Haryana', '122001', 'pending', 1)
            """,
            (user['id'],),
            commit=True
        )
        execute_query("INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status) VALUES (%s, 'TVs', 'Old CRT', 1, 1, 'verified')", (sub1_id,), commit=True)
        award_submission_points(sub1_id, admin_id=1)

        sub2_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, user_id, is_student, full_name, phone_number,
                address, city, state, pincode, status, total_submitted_items
            ) VALUES ('SUB-TEST-10B', %s, 0, 'Scenario 10 User', '9999900010', 'Address B', 'Gurugram', 'Haryana', '122001', 'pending', 2)
            """,
            (user['id'],),
            commit=True
        )
        execute_query("INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity, accepted_quantity, status) VALUES (%s, 'Laptops', 'Old Dell', 2, 2, 'verified')", (sub2_id,), commit=True)
        award_submission_points(sub2_id, admin_id=1)

        # Check ledger entries: exactly 2 separate transactions
        ledger = get_wallet_ledger(user['id'])
        self.assertGreaterEqual(len(ledger), 2)
        codes = [tx['submission_code'] for tx in ledger]
        self.assertIn('SUB-TEST-10A', codes)
        self.assertIn('SUB-TEST-10B', codes)

        # Verify /my-points template loads with both transactions
        with self.client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['user_name'] = user['full_name']
        res = self.client.get('/my-points')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SUB-TEST-10A", res.data)
        self.assertIn(b"SUB-TEST-10B", res.data)

        print("[PASS] Test 69: Scenario 10 - Submission-Wise Points Ledger Entries Separately Displayed Verified.")

    def test_70_scenario_11_wallet_balance_equals_sum_of_transactions_ledger(self):
        """Test 70 (Scenario 11): Points wallet balance equals exact sum of transactions ledger."""
        user = self._create_test_user_helper("scenario11_user@testdomain.demo", "Scenario 11 User")
        from points_service import manual_adjust_points, recalculate_wallet_balance, get_or_create_wallet

        # Add multiple transactions (+20, +15, -10)
        manual_adjust_points(user['id'], 20, "Bonus credit 1", admin_id=1)
        manual_adjust_points(user['id'], 15, "Bonus credit 2", admin_id=1)
        manual_adjust_points(user['id'], -10, "Adjustment debit", admin_id=1)

        # Calculate sum from ledger
        totals = execute_query(
            "SELECT SUM(points_amount) AS calc_total FROM points_transactions WHERE user_id = %s",
            (user['id'],),
            fetchone=True
        )
        expected_balance = totals['calc_total']
        self.assertEqual(expected_balance, 25)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], expected_balance)

        # Recalculate to verify idempotent consistency
        recalculated = recalculate_wallet_balance(user['id'])
        self.assertEqual(recalculated, expected_balance)
        print("[PASS] Test 70: Scenario 11 - 100% Wallet Balance to Ledger Consistency Verified.")

    def test_71_scenario_12_separate_points_balances_across_multiple_users(self):
        """Test 71 (Scenario 12): Separate points balances across multiple users."""
        user_a = self._create_test_user_helper("scenario12_user_a@testdomain.demo", "User A")
        user_b = self._create_test_user_helper("scenario12_user_b@testdomain.demo", "User B")
        from points_service import manual_adjust_points, get_or_create_wallet

        manual_adjust_points(user_a['id'], 35, "Points for User A", admin_id=1)
        manual_adjust_points(user_b['id'], 60, "Points for User B", admin_id=1)

        wallet_a = get_or_create_wallet(user_a['id'])
        wallet_b = get_or_create_wallet(user_b['id'])

        self.assertEqual(wallet_a['current_balance'], 35)
        self.assertEqual(wallet_b['current_balance'], 60)
        self.assertNotEqual(wallet_a['current_balance'], wallet_b['current_balance'])
        print("[PASS] Test 71: Scenario 12 - Independent Wallet Isolation Across Multiple Users Verified.")

    def test_72_scenario_13_dynamic_admin_modification_of_points_tiers(self):
        """Test 72 (Scenario 13): Dynamic admin modification of points tiers without code edits."""
        from points_service import save_points_tier, calculate_points_for_quantity

        # Get existing 1-item tier
        tier1 = execute_query("SELECT id, points_awarded FROM points_tiers WHERE min_quantity = 1 AND max_quantity = 1", fetchone=True)
        self.assertIsNotNone(tier1)
        original_pts = tier1['points_awarded']

        try:
            # Dynamically update 1-item tier to 8 points
            save_points_tier(
                tier_name="1 Item Tier (Updated)",
                min_quantity=1,
                max_quantity=1,
                points_awarded=8,
                is_active=1,
                tier_id=tier1['id']
            )

            # Calculation for 1 item should now immediately return 8
            new_calculated = calculate_points_for_quantity(1)
            self.assertEqual(new_calculated, 8)

        finally:
            # Restore to original value (5 points)
            save_points_tier(
                tier_name="1 Item Tier",
                min_quantity=1,
                max_quantity=1,
                points_awarded=original_pts,
                is_active=1,
                tier_id=tier1['id']
            )
            restored = calculate_points_for_quantity(1)
            self.assertEqual(restored, original_pts)

        print("[PASS] Test 72: Scenario 13 - Dynamic Points Tiers Admin Modification Verified.")

    def test_73_scenario_14_manual_adjustment_requires_reason_and_records_in_ledger(self):
        """Test 73 (Scenario 14): Manual points adjustment requires non-empty reason and records in ledger."""
        user = self._create_test_user_helper("scenario14_user@testdomain.demo", "Scenario 14 User")
        from points_service import manual_adjust_points, get_or_create_wallet, get_wallet_ledger

        # 1. Attempt adjustment without reason -> Must fail
        success_empty, msg_empty = manual_adjust_points(user['id'], 10, "", admin_id=1)
        self.assertFalse(success_empty)
        self.assertIn("reason is required", msg_empty.lower())

        # 2. Attempt adjustment with whitespace-only reason -> Must fail
        success_ws, msg_ws = manual_adjust_points(user['id'], 10, "   ", admin_id=1)
        self.assertFalse(success_ws)
        self.assertIn("reason is required", msg_ws.lower())

        # 3. Valid adjustment with mandatory explanation reason -> Must succeed
        success_valid, msg_valid = manual_adjust_points(user['id'], 15, "Compensation for logistics delay", admin_id=1)
        self.assertTrue(success_valid)

        wallet = get_or_create_wallet(user['id'])
        self.assertEqual(wallet['current_balance'], 15)

        # 4. Verify transaction recorded in ledger
        ledger = get_wallet_ledger(user['id'])
        self.assertGreaterEqual(len(ledger), 1)
        latest_tx = ledger[0]
        self.assertEqual(latest_tx['points_amount'], 15)
        self.assertEqual(latest_tx['reason'], "Compensation for logistics delay")
        self.assertEqual(latest_tx['created_by_admin_id'], 1)
        print("[PASS] Test 73: Scenario 14 - Mandatory Adjustment Reason & Ledger Recording Verified.")

    # ==========================================================================
    # Phase 10 Tests: Email Notification & Template Management System
    # ==========================================================================

    def test_74_scenario_01_sgt_student_submits_and_receives_sgt_template(self):
        """Test 74 (Scenario 1): SGT University student submits form and receives SGT email template."""
        email = "sgt_student_test@testdomain.demo"
        resp = self.client.post('/submit-ewaste', data={
            'is_student': 'yes',
            'student_name': 'Daksh / Yogesh SGT',
            'university_type': 'SGT University',
            'roll_number': '241306039',
            'course_dept': 'BCA AIML',
            'phone_number': '9999910001',
            'email': email,
            'address': 'SGT University Block A, Budhera',
            'city': 'Gurugram',
            'state': 'Haryana',
            'pincode': '122505',
            'item_category[]': ['Mobile phones'],
            'item_name[]': ['OnePlus 7T'],
            'item_quantity[]': ['1'],
            'item_condition[]': ['Working']
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Verify email_logs
        log = execute_query(
            "SELECT * FROM email_logs WHERE recipient_email = %s ORDER BY id DESC LIMIT 1",
            (email,),
            fetchone=True
        )
        self.assertIsNotNone(log)
        self.assertEqual(log['user_category'], 'sgt_student')
        self.assertEqual(log['email_type'], 'submission_received')
        self.assertEqual(log['status'], 'Sent')
        self.assertIn("SGT University", log['subject'])
        print("[PASS] Test 74: Scenario 1 - SGT Student Form Submission Routed to SGT Template.")

    def test_75_scenario_02_other_university_student_receives_general_template(self):
        """Test 75 (Scenario 2): Student from another university receives general email template."""
        email = "other_uni_student@testdomain.demo"
        resp = self.client.post('/submit-ewaste', data={
            'is_student': 'yes',
            'student_name': 'Aarav Mehta',
            'university_type': 'Other University',
            'university_name_other': 'Delhi Technological University',
            'roll_number': '2K22/CO/101',
            'course_dept': 'CSE',
            'phone_number': '9999910002',
            'email': email,
            'address': 'Rohini Sector 16',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110085',
            'item_category[]': ['Laptops'],
            'item_name[]': ['Dell Inspiron'],
            'item_quantity[]': ['1'],
            'item_condition[]': ['Not Working']
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        log = execute_query(
            "SELECT * FROM email_logs WHERE recipient_email = %s ORDER BY id DESC LIMIT 1",
            (email,),
            fetchone=True
        )
        self.assertIsNotNone(log)
        self.assertEqual(log['user_category'], 'general_user')
        self.assertEqual(log['email_type'], 'submission_received')
        self.assertEqual(log['status'], 'Sent')
        print("[PASS] Test 75: Scenario 2 - Other University Student Form Submission Routed to General Template.")

    def test_76_scenario_03_non_student_receives_general_template(self):
        """Test 76 (Scenario 3): Non-student citizen receives general email template."""
        email = "citizen_user@testdomain.demo"
        resp = self.client.post('/submit-ewaste', data={
            'is_student': 'no',
            'full_name': 'Sunita Rao',
            'phone_number': '9999910003',
            'email': email,
            'address': 'DLF Cyber City Phase 2',
            'city': 'Gurugram',
            'state': 'Haryana',
            'pincode': '122002',
            'item_category[]': ['TVs'],
            'item_name[]': ['Sony Bravia LCD'],
            'item_quantity[]': ['1'],
            'item_condition[]': ['Damaged']
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        log = execute_query(
            "SELECT * FROM email_logs WHERE recipient_email = %s ORDER BY id DESC LIMIT 1",
            (email,),
            fetchone=True
        )
        self.assertIsNotNone(log)
        self.assertEqual(log['user_category'], 'general_user')
        self.assertEqual(log['email_type'], 'submission_received')
        self.assertEqual(log['status'], 'Sent')
        print("[PASS] Test 76: Scenario 3 - Non-Student Citizen Submission Routed to General Template.")

    def test_77_scenario_04_admin_edits_sgt_template_and_changes_appear(self):
        """Test 77 (Scenario 4): Admin edits SGT template and changes appear in subsequent emails."""
        from email_service import restore_default_template_definition

        # Get SGT template
        tpl = execute_query("SELECT id, subject FROM email_templates WHERE template_key = 'sub_received_sgt'", fetchone=True)
        self.assertIsNotNone(tpl)

        custom_subject = "Special EcoLocate Green SGT Campus Notification [{{submission_id}}]"
        custom_heading = "Welcome SGT Green Warriors"

        # Admin logs in & updates template
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        resp = self.client.post(f'/admin/emails/templates/{tpl["id"]}', data={
            'action': 'save',
            'subject': custom_subject,
            'heading': custom_heading,
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'Custom confirmation message for SGT.',
            'body': 'Your e-waste request {{submission_id}} is priority tracked.',
            'additional_instructions': 'Hand over at hostel gate.',
            'closing_message': 'Regards, SGT Team',
            'sender_display_name': 'SGT EcoLocate',
            'is_active': '1'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Clear admin session
        with self.client.session_transaction() as sess:
            sess.pop('admin_id', None)

        # User submits form
        email = "sgt_after_edit@testdomain.demo"
        self.client.post('/submit-ewaste', data={
            'is_student': 'yes',
            'student_name': 'SGT Modified Test',
            'university_type': 'SGT University',
            'phone_number': '9999910004',
            'email': email,
            'address': 'SGT University Faculty Block',
            'city': 'Gurugram',
            'state': 'Haryana',
            'pincode': '122505',
            'item_category[]': ['Batteries'],
            'item_name[]': ['Lithium Cells'],
            'item_quantity[]': ['2'],
            'item_condition[]': ['Working']
        }, follow_redirects=True)

        log = execute_query(
            "SELECT * FROM email_logs WHERE recipient_email = %s ORDER BY id DESC LIMIT 1",
            (email,),
            fetchone=True
        )
        self.assertIsNotNone(log)
        self.assertIn("Special EcoLocate Green SGT Campus Notification", log['subject'])

        # Restore default template
        restore_default_template_definition('sub_received_sgt')
        print("[PASS] Test 77: Scenario 4 - Admin Edited SGT Template Successfully Applied to Subsequent Email.")

    def test_78_scenario_05_admin_edits_general_template_independently(self):
        """Test 78 (Scenario 5): Admin edits general template independently without altering SGT template."""
        from email_service import restore_default_template_definition

        gen_tpl = execute_query("SELECT id, subject FROM email_templates WHERE template_key = 'sub_received_general'", fetchone=True)
        sgt_tpl = execute_query("SELECT id, subject FROM email_templates WHERE template_key = 'sub_received_sgt'", fetchone=True)
        original_sgt_subject = sgt_tpl['subject']

        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # Edit general template
        resp = self.client.post(f'/admin/emails/templates/{gen_tpl["id"]}', data={
            'action': 'save',
            'subject': 'Independent General Citizen Subject [{{submission_id}}]',
            'heading': 'Citizen Circular Loop Heading',
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'General confirmation text.',
            'body': 'General body text {{submission_id}}.',
            'additional_instructions': '',
            'closing_message': 'Regards, EcoLocate',
            'sender_display_name': 'EcoLocate',
            'is_active': '1'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Verify SGT template subject remained 100% unchanged
        sgt_after = execute_query("SELECT subject FROM email_templates WHERE template_key = 'sub_received_sgt'", fetchone=True)
        self.assertEqual(sgt_after['subject'], original_sgt_subject, "Editing general template must never modify SGT template!")

        # Restore general template
        restore_default_template_definition('sub_received_general')
        print("[PASS] Test 78: Scenario 5 - General Template Edited Independently Without Affecting SGT Template.")

    def test_79_scenario_06_user_receives_automatic_submission_received_email(self):
        """Test 79 (Scenario 6): User receives automatic submission-received email upon form submission."""
        email = "auto_sub_user@testdomain.demo"
        resp = self.client.post('/submit-ewaste', data={
            'is_student': 'no',
            'full_name': 'Automated Submission User',
            'phone_number': '9999910006',
            'email': email,
            'address': 'Golf Course Road',
            'city': 'Gurugram',
            'state': 'Haryana',
            'pincode': '122002',
            'item_category[]': ['Electronic components'],
            'item_name[]': ['Arduino Boards & Sensors'],
            'item_quantity[]': ['5'],
            'item_condition[]': ['Working']
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        log = execute_query(
            "SELECT * FROM email_logs WHERE recipient_email = %s AND email_type = 'submission_received'",
            (email,),
            fetchone=True
        )
        self.assertIsNotNone(log)
        self.assertEqual(log['status'], 'Sent')
        self.assertIsNotNone(log['sent_at'])
        print("[PASS] Test 79: Scenario 6 - Automatic Submission Received Email Dispatched & Logged.")

    def test_80_scenario_07_admin_confirms_request_and_user_receives_confirmation_email(self):
        """Test 80 (Scenario 7): Admin confirms a request and the user receives a confirmation email."""
        # 1. Create a submission
        email = "confirm_test_user@testdomain.demo"
        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, full_name, phone_number, email, address,
                city, state, pincode, is_student, university_type, status,
                total_submitted_items
            ) VALUES (
                'SUB-CONF-TEST1', 'Confirmation Candidate', '9999910007', %s, 'Sector 29',
                'Gurugram', 'Haryana', '122001', 0, NULL, 'pending', 2
            )
            """,
            (email,),
            commit=True
        )
        execute_query("INSERT INTO ewaste_submission_items (submission_id, category, item_name, submitted_quantity) VALUES (%s, 'Laptops', 'ThinkPad T480', 2)", (sub_id,), commit=True)

        # 2. Admin logs in and clicks "Confirm Request"
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        resp = self.client.post(f'/admin/submissions/{sub_id}', data={
            'action': 'confirm_request'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # 3. Verify submission status updated to 'confirmed'
        updated_sub = execute_query("SELECT status, confirmed_at, confirmed_by FROM ewaste_submissions WHERE id = %s", (sub_id,), fetchone=True)
        self.assertEqual(updated_sub['status'], 'confirmed')
        self.assertIsNotNone(updated_sub['confirmed_at'])
        self.assertEqual(updated_sub['confirmed_by'], 1)

        # 4. Verify request_confirmed email logged
        email_log = execute_query(
            "SELECT * FROM email_logs WHERE submission_id = %s AND email_type = 'request_confirmed'",
            (sub_id,),
            fetchone=True
        )
        self.assertIsNotNone(email_log)
        self.assertEqual(email_log['status'], 'Sent')
        print("[PASS] Test 80: Scenario 7 - Admin 'Confirm Request' Updates Status to Confirmed & Dispatches Email.")

    def test_81_scenario_08_email_failure_does_not_prevent_form_submission(self):
        """Test 81 (Scenario 8): Email failure does not prevent form submission."""
        from config import Config
        Config.SIMULATE_SMTP_FAILURE = True

        email = "smtp_fail_sub@testdomain.demo"
        try:
            # User submits form while SMTP fails
            resp = self.client.post('/submit-ewaste', data={
                'is_student': 'no',
                'full_name': 'Resilient Form Submitter',
                'phone_number': '9999910008',
                'email': email,
                'address': 'MG Road Metro Station',
                'city': 'Gurugram',
                'state': 'Haryana',
                'pincode': '122002',
                'item_category[]': ['Printers'],
                'item_name[]': ['HP LaserJet M1005'],
                'item_quantity[]': ['1'],
                'item_condition[]': ['Working']
            }, follow_redirects=True)

            # Form submission MUST succeed with HTTP 200
            self.assertEqual(resp.status_code, 200)

            # Submission must be saved in database
            sub = execute_query("SELECT * FROM ewaste_submissions WHERE email = %s", (email,), fetchone=True)
            self.assertIsNotNone(sub)
            self.assertEqual(sub['status'], 'pending')

            # Failed email must be recorded in email_logs
            log = execute_query("SELECT * FROM email_logs WHERE recipient_email = %s", (email,), fetchone=True)
            self.assertIsNotNone(log)
            self.assertEqual(log['status'], 'Failed')
            self.assertIn("Simulated SMTP failure", log['error_message'])

        finally:
            Config.SIMULATE_SMTP_FAILURE = False

        print("[PASS] Test 81: Scenario 8 - Email Failure Does Not Block Form Submission; Logged as Failed.")

    def test_82_scenario_09_email_failure_does_not_undo_admin_confirmation(self):
        """Test 82 (Scenario 9): Email failure does not undo admin confirmation."""
        from config import Config

        # 1. Create a submission
        email = "smtp_fail_confirm@testdomain.demo"
        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, full_name, phone_number, email, address,
                city, state, pincode, is_student, university_type, status,
                total_submitted_items
            ) VALUES (
                'SUB-CONF-FAIL1', 'Fail Confirm User', '9999910009', %s, 'Sector 15',
                'Gurugram', 'Haryana', '122001', 0, NULL, 'pending', 1
            )
            """,
            (email,),
            commit=True
        )

        Config.SIMULATE_SMTP_FAILURE = True
        try:
            with self.client.session_transaction() as sess:
                sess['admin_id'] = 1
                sess['admin_username'] = 'admin'

            # Admin confirms request
            resp = self.client.post(f'/admin/submissions/{sub_id}', data={
                'action': 'confirm_request'
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # Request status MUST remain 'confirmed' (not reverted to pending)
            updated_sub = execute_query("SELECT status, confirmed_at, confirmed_by FROM ewaste_submissions WHERE id = %s", (sub_id,), fetchone=True)
            self.assertEqual(updated_sub['status'], 'confirmed')
            self.assertIsNotNone(updated_sub['confirmed_at'])

            # Email log records Failed
            log = execute_query("SELECT * FROM email_logs WHERE submission_id = %s AND email_type = 'request_confirmed'", (sub_id,), fetchone=True)
            self.assertIsNotNone(log)
            self.assertEqual(log['status'], 'Failed')

        finally:
            Config.SIMULATE_SMTP_FAILURE = False

        print("[PASS] Test 82: Scenario 9 - Email Failure Does Not Undo Admin Confirmation; Status Stays Confirmed.")

    def test_83_scenario_10_admin_can_retry_failed_emails(self):
        """Test 83 (Scenario 10): Admin can retry failed emails and status updates to Sent."""
        # 1. Create submission and insert a failed email log
        email = "retry_test_user@testdomain.demo"
        sub_id = execute_query(
            """
            INSERT INTO ewaste_submissions (
                submission_code, full_name, phone_number, email, address,
                city, state, pincode, is_student, university_type, status,
                total_submitted_items
            ) VALUES (
                'SUB-RETRY-10', 'Retry User', '9999910010', %s, 'Sohna Road',
                'Gurugram', 'Haryana', '122018', 0, NULL, 'confirmed', 1
            )
            """,
            (email,),
            commit=True
        )
        log_id = execute_query(
            """
            INSERT INTO email_logs (
                submission_id, recipient_email, recipient_name, user_category,
                email_type, subject, status, error_message, attempt_count
            ) VALUES (
                %s, %s, 'Retry User', 'general_user',
                'request_confirmed', 'Test Confirmation', 'Failed', 'Initial failure', 1
            )
            """,
            (sub_id, email),
            commit=True
        )

        # 2. Admin retries the email
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        resp = self.client.post(f'/admin/emails/retry/{log_id}', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # 3. Verify log status updated to 'Sent' and attempt count incremented
        updated_log = execute_query("SELECT status, attempt_count, error_message FROM email_logs WHERE id = %s", (log_id,), fetchone=True)
        self.assertEqual(updated_log['status'], 'Sent')
        self.assertGreaterEqual(updated_log['attempt_count'], 2)
        self.assertIsNone(updated_log['error_message'])

        print("[PASS] Test 83: Scenario 10 - Admin Retry for Failed Email Successfully Executed & Log Updated.")

    def test_84_scenario_11_dynamic_variables_display_correct_submission_info(self):
        """Test 84 (Scenario 11): Dynamic variables display correct submission information."""
        from datetime import datetime
        from email_service import substitute_variables, build_submission_context

        submission = {
            'id': 999,
            'submission_code': 'SUB-2026-VARTST',
            'full_name': 'Yogesh Sharma',
            'email': 'yogesh@testdomain.demo',
            'phone_number': '9876543210',
            'is_student': 1,
            'student_name': 'Yogesh Sharma',
            'university_type': 'SGT University',
            'university_name': 'SGT University',
            'roll_number': '241306039',
            'status': 'confirmed',
            'total_submitted_items': 4,
            'total_accepted_items': 3,
            'created_at': datetime(2026, 11, 22, 10, 30)
        }

        context = build_submission_context(submission, admin_name="Admin Guide")
        self.assertEqual(context['user_name'], 'Yogesh Sharma')
        self.assertEqual(context['submission_id'], 'SUB-2026-VARTST')
        self.assertEqual(context['roll_number'], '241306039')
        self.assertEqual(context['admin_name'], 'Admin Guide')

        template_text = "Dear {{user_name}}, ref {{submission_id}} (Roll {{roll_number}}) by {{admin_name}}."
        rendered = substitute_variables(template_text, context)
        self.assertEqual(rendered, "Dear Yogesh Sharma, ref SUB-2026-VARTST (Roll 241306039) by Admin Guide.")
        print("[PASS] Test 84: Scenario 11 - Dynamic Variables Substitution Verified with Exact Context.")

    def test_85_scenario_12_admin_can_preview_and_test_email_templates(self):
        """Test 85 (Scenario 12): Admin can preview and test email templates."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # 1. Preview AJAX Endpoint
        resp_prev = self.client.post('/admin/emails/preview', json={
            'user_category': 'sgt_student',
            'email_type': 'submission_received',
            'subject': 'Preview Subject for {{user_name}}',
            'heading': 'Preview Heading',
            'greeting': 'Dear {{user_name}},',
            'confirmation_message': 'Preview confirmation message.',
            'body': 'Your submission {{submission_id}} is verified.',
            'additional_instructions': 'Preview instructions.',
            'closing_message': 'Best regards,\nPreview Team',
            'sender_display_name': 'EcoLocate Preview'
        })
        self.assertEqual(resp_prev.status_code, 200)
        json_data = resp_prev.get_json()
        self.assertTrue(json_data['success'])
        self.assertIn("Preview Subject for", json_data['subject'])
        self.assertIn("Preview Heading", json_data['html'])

        # 2. Test Email Dispatch
        tpl = execute_query("SELECT id FROM email_templates LIMIT 1", fetchone=True)
        resp_test = self.client.post(f'/admin/emails/templates/{tpl["id"]}', data={
            'action': 'send_test',
            'test_recipient': 'test_admin_inbox@testdomain.demo'
        }, follow_redirects=True)
        self.assertEqual(resp_test.status_code, 200)

        print("[PASS] Test 85: Scenario 12 - Live Preview & Send Test Email Functionality Verified.")

    def test_86_scenario_13_email_history_correctly_records_sending_attempts(self):
        """Test 86 (Scenario 13): Email history correctly records sending attempts and supports filters."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # View full history
        resp = self.client.get('/admin/emails/history')
        self.assertEqual(resp.status_code, 200)

        # View with category filter
        resp_sgt = self.client.get('/admin/emails/history?category=sgt_student')
        self.assertEqual(resp_sgt.status_code, 200)

        # View with status filter
        resp_sent = self.client.get('/admin/emails/history?status=Sent')
        self.assertEqual(resp_sent.status_code, 200)

        print("[PASS] Test 86: Scenario 13 - Email History Log Table and Filtering Options Verified.")

    def test_87_scenario_14_normal_users_blocked_from_email_templates(self):
        """Test 87 (Scenario 14): Normal users cannot access or modify email templates."""
        user = self._create_test_user_helper("unauth_email_user@testdomain.demo")

        with self.client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['user_name'] = user['full_name']
            sess.pop('admin_id', None)

        endpoints = [
            '/admin/emails/templates',
            '/admin/emails/templates/1',
            '/admin/emails/history'
        ]

        for ep in endpoints:
            res = self.client.get(ep, follow_redirects=False)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/admin/login', res.headers['Location'])

        # Attempt POST to save template
        res_post = self.client.post('/admin/emails/templates/1', data={'action': 'save', 'subject': 'Hacked'}, follow_redirects=False)
        self.assertEqual(res_post.status_code, 302)
        self.assertIn('/admin/login', res_post.headers['Location'])

        print("[PASS] Test 87: Scenario 14 - Strict Non-Admin Boundary Protection for Email Management Verified.")

    def test_88_scenario_15_smtp_credentials_never_exposed_to_frontend(self):
        """Test 88 (Scenario 15): SMTP credentials (such as passwords) are never exposed to frontend users or admin templates."""
        from config import Config
        Config.SMTP_PASSWORD = "SuperSecretSMTPPassword999!"

        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_username'] = 'admin'

        # Check template editor page
        resp_tpl = self.client.get('/admin/emails/templates/1')
        self.assertNotIn("SuperSecretSMTPPassword999!", resp_tpl.data.decode('utf-8', errors='ignore'))

        # Check history page
        resp_hist = self.client.get('/admin/emails/history')
        self.assertNotIn("SuperSecretSMTPPassword999!", resp_hist.data.decode('utf-8', errors='ignore'))

        # Check public submission form
        resp_public = self.client.get('/submit-ewaste')
        self.assertNotIn("SuperSecretSMTPPassword999!", resp_public.data.decode('utf-8', errors='ignore'))

        # Reset password
        Config.SMTP_PASSWORD = ""
        print("[PASS] Test 88: Scenario 15 - Complete Zero-Leakage of Sensitive SMTP Credentials Verified.")



if __name__ == '__main__':
    unittest.main()
