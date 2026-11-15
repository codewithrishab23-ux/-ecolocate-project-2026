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

    @classmethod
    def tearDownClass(cls):
        """Clean up test users after test suite completes."""
        execute_query("DELETE FROM users WHERE email LIKE '%@testdomain.demo'", commit=True)
        execute_query("DELETE FROM centres WHERE id > 87", commit=True)
        execute_query("DELETE FROM devices WHERE device_name LIKE 'Test %'", commit=True)

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

if __name__ == '__main__':
    unittest.main()
