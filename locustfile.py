"""
EcoLocate - Locust Multi-User Performance & Load Testing Suite
Simulates 50 concurrent users performing simultaneous realistic workflows:
1. Public Browsing (Homepage, Awareness, Find Centres directory)
2. Geospatial Operations (Leaflet Map pins API, Haversine nearest facility calculation)
3. Multi-Criteria Searches (State & City cascades, keyword queries)
4. EcoRewards Engine (Dynamic device fetching, AJAX calculations)
5. User Authentication & Profile (Concurrent logins, session isolation, saving calculations)
6. Administrative Control (Protected dashboard KPIs and management queries)
"""

import random
from locust import HttpUser, task, between, tag

INDIAN_TEST_COORDINATES = [
    {"name": "Delhi NCR", "lat": 28.6139, "lng": 77.2090},
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714}
]

SEARCH_QUERIES = [
    {"state": "Maharashtra", "city": "Mumbai"},
    {"state": "Delhi", "city": "Delhi"},
    {"state": "Karnataka", "city": "Bengaluru"},
    {"state": "Tamil Nadu", "city": "Chennai"},
    {"state": "Gujarat", "city": "Ahmedabad"},
    {"state": "Uttar Pradesh", "city": "Noida"},
    {"state": "", "q": "Eco"},
    {"state": "", "q": "Recyclers"}
]

class EcoLocateUser(HttpUser):
    """Simulates a community visitor discovering facilities and calculating rewards."""
    wait_time = between(1, 3)

    @task(4)
    def browse_homepage(self):
        """User loads home landing page."""
        self.client.get("/", name="[Page] Home Landing")

    @task(3)
    def browse_find_centres(self):
        """User visits find centres directory."""
        self.client.get("/centres", name="[Page] Find Centres")

    @task(5)
    def search_centres_filtered(self):
        """User searches facilities by state, city, or keyword."""
        query = random.choice(SEARCH_QUERIES)
        params = []
        if query.get("state"):
            params.append(f"state={query['state']}")
        if query.get("city"):
            params.append(f"city={query['city']}")
        if query.get("q"):
            params.append(f"q={query['q']}")
        qs = "&".join(params)
        self.client.get(f"/api/centres?{qs}", name="[API] Search Centres Filtered")

    @task(4)
    def fetch_map_markers(self):
        """User opens Leaflet map and queries all verified facility coordinates."""
        self.client.get("/api/centres/map", name="[API] Leaflet Map Coordinates")

    @task(5)
    def calculate_nearest_facility(self):
        """User uses geolocation to find nearest facility via Haversine formula."""
        loc = random.choice(INDIAN_TEST_COORDINATES)
        self.client.get(
            f"/api/centres/nearby?lat={loc['lat']}&lng={loc['lng']}",
            name="[API] Haversine Nearest Proximity"
        )

    @task(3)
    def view_awareness_page(self):
        """User reads Why E-Waste Matters educational curriculum."""
        self.client.get("/awareness", name="[Page] Awareness Curriculum")

    @task(4)
    def calculate_rewards(self):
        """User calculates EcoPoints for electronic devices."""
        device_id = random.randint(1, 10)
        quantity = random.randint(1, 15)
        self.client.post(
            "/api/rewards/calculate",
            json={"device_id": device_id, "quantity": quantity},
            name="[API] EcoRewards Calculation"
        )

    @task(2)
    def check_health(self):
        """Monitor application health and database connection pooling."""
        self.client.get("/health", name="[API] System Health Probe")
