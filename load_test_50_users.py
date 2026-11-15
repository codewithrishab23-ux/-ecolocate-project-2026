"""
EcoLocate - Phase 8 Multi-User High-Concurrency Performance Test
Simulates 50 simultaneous concurrent users making realistic requests against the Flask application:
- Independent sessions & CSRF
- Homepage & awareness visits
- Map coordinates query
- Multi-criteria city/state searches
- Haversine nearest facility calculations
- Dynamic rewards calculations
- User logins
"""

import time
import random
import re
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

BASE_URL = "http://127.0.0.1:5000"
NUM_CONCURRENT_USERS = 50

CITIES_TO_SEARCH = [
    ("Maharashtra", "Mumbai"),
    ("Delhi", "Delhi"),
    ("Karnataka", "Bengaluru"),
    ("Tamil Nadu", "Chennai"),
    ("Gujarat", "Ahmedabad"),
    ("Uttar Pradesh", "Noida"),
    ("Andhra Pradesh", "Visakhapatnam"),
    ("Haryana", "Gurugram")
]

COORDINATES_TO_QUERY = [
    (28.6139, 77.2090),  # Delhi
    (19.0760, 72.8777),  # Mumbai
    (12.9716, 77.5946),  # Bengaluru
    (13.0827, 80.2707),  # Chennai
    (17.3850, 78.4867),  # Hyderabad
    (18.5204, 73.8567),  # Pune
]

def simulate_user_session(user_id):
    """Simulate a single concurrent user performing sequential realistic requests."""
    session = requests.Session()
    session_latencies = []
    errors = 0
    endpoints_tested = []

    def log_request(name, req_func):
        nonlocal errors
        try:
            t0 = time.perf_counter()
            r = req_func()
            dt = (time.perf_counter() - t0) * 1000
            session_latencies.append(dt)
            if r.status_code not in (200, 201, 302):
                errors += 1
                endpoints_tested.append((name, r.status_code, dt, r.text[:100]))
            else:
                endpoints_tested.append((name, r.status_code, dt, "OK"))
            return r
        except Exception as e:
            errors += 1
            endpoints_tested.append((name, 500, 0, str(e)))
            return None

    # 1. Homepage visit
    log_request("[Page] Home", lambda: session.get(f"{BASE_URL}/", timeout=10))

    # 2. Map coordinates endpoint
    log_request("[API] Map Markers", lambda: session.get(f"{BASE_URL}/api/centres/map", timeout=10))

    # 3. Dynamic search & filter by state and city
    st, ct = random.choice(CITIES_TO_SEARCH)
    log_request("[API] Search Centres", lambda: session.get(f"{BASE_URL}/api/centres?state={st}&city={ct}", timeout=10))

    # 4. Haversine nearest proximity calculation
    lat, lng = random.choice(COORDINATES_TO_QUERY)
    log_request("[API] Haversine Nearby", lambda: session.get(f"{BASE_URL}/api/centres/nearby?lat={lat}&lng={lng}", timeout=10))

    # 5. Awareness Curriculum
    log_request("[Page] Awareness", lambda: session.get(f"{BASE_URL}/awareness", timeout=10))

    # 6. Device listing
    log_request("[API] Devices", lambda: session.get(f"{BASE_URL}/api/devices", timeout=10))

    # 7. Rewards dynamic calculation
    dev_id = random.randint(1, 10)
    qty = random.randint(1, 20)
    log_request("[API] Rewards Calc", lambda: session.post(
        f"{BASE_URL}/api/rewards/calculate",
        json={"device_id": dev_id, "quantity": qty},
        timeout=10
    ))

    # 8. User registration with CSRF token
    unique_email = f"loaduser_{user_id}_{int(time.time()*1000)}_{random.randint(100,999)}@testdomain.demo"
    reg_page = log_request("[Page] Reg Form", lambda: session.get(f"{BASE_URL}/register", timeout=10))
    csrf_token = ""
    if reg_page and reg_page.status_code == 200:
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', reg_page.text)
        if m:
            csrf_token = m.group(1)

    log_request("[Action] Register", lambda: session.post(
        f"{BASE_URL}/register",
        data={
            'csrf_token': csrf_token,
            'full_name': f"LoadUser {user_id}",
            'email': unique_email,
            'password': 'SecureLoadTestPassword123!',
            'confirm_password': 'SecureLoadTestPassword123!',
            'terms': 'on'
        },
        timeout=10,
        allow_redirects=True
    ))

    # 9. Health probe
    log_request("[API] Health Probe", lambda: session.get(f"{BASE_URL}/health", timeout=10))

    return {
        'user_id': user_id,
        'latencies': session_latencies,
        'errors': errors,
        'requests_count': len(session_latencies),
        'endpoints': endpoints_tested
    }

def run_50_concurrent_users_test():
    """Run full load test simulating 50 concurrent threads."""
    print("=================================================================")
    print(f" EcoLocate: Multi-User Concurrency Performance Test")
    print(f" Target: {NUM_CONCURRENT_USERS} Concurrent Users (Simultaneous Threads)")
    print(f" Base URL: {BASE_URL}")
    print("=================================================================\n")

    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"[!] Server returned status {r.status_code}. Is Flask running?")
            return None
    except Exception as e:
        print(f"[!] Could not connect to Flask server at {BASE_URL}: {e}")
        return None

    overall_start = time.perf_counter()
    all_latencies = []
    total_errors = 0
    total_requests = 0
    endpoint_error_details = []

    print(f"[*] Firing {NUM_CONCURRENT_USERS} concurrent user threads simultaneously...")

    with ThreadPoolExecutor(max_workers=NUM_CONCURRENT_USERS) as executor:
        futures = [executor.submit(simulate_user_session, i) for i in range(1, NUM_CONCURRENT_USERS + 1)]

        for future in as_completed(futures):
            res = future.result()
            all_latencies.extend(res['latencies'])
            total_errors += res['errors']
            total_requests += res['requests_count']
            for ep in res['endpoints']:
                if ep[1] not in (200, 201, 302):
                    endpoint_error_details.append(ep)

    total_duration = time.perf_counter() - overall_start

    # Clean up test users created during load test
    from db import execute_query
    execute_query("DELETE FROM users WHERE email LIKE 'loaduser_%@testdomain.demo'", commit=True)

    # Compute statistical percentiles
    all_latencies.sort()
    avg_latency = statistics.mean(all_latencies) if all_latencies else 0
    median_latency = statistics.median(all_latencies) if all_latencies else 0
    p95_latency = all_latencies[int(len(all_latencies) * 0.95)] if all_latencies else 0
    p99_latency = all_latencies[int(len(all_latencies) * 0.99)] if all_latencies else 0
    min_latency = min(all_latencies) if all_latencies else 0
    max_latency = max(all_latencies) if all_latencies else 0
    rps = total_requests / total_duration if total_duration > 0 else 0
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

    report = {
        'concurrent_users': NUM_CONCURRENT_USERS,
        'total_requests': total_requests,
        'successful_requests': total_requests - total_errors,
        'failed_requests': total_errors,
        'error_rate_pct': round(error_rate, 2),
        'total_duration_sec': round(total_duration, 2),
        'requests_per_sec': round(rps, 2),
        'avg_latency_ms': round(avg_latency, 2),
        'median_latency_ms': round(median_latency, 2),
        'p95_latency_ms': round(p95_latency, 2),
        'p99_latency_ms': round(p99_latency, 2),
        'min_latency_ms': round(min_latency, 2),
        'max_latency_ms': round(max_latency, 2)
    }

    print("\n-----------------------------------------------------------------")
    print(f" Concurrency Test Results ({NUM_CONCURRENT_USERS} Simultaneous Users)")
    print("-----------------------------------------------------------------")
    print(f" Total Requests Completed: {total_requests}")
    print(f" Successful Requests:      {total_requests - total_errors}")
    print(f" Failed Requests:          {total_errors} (Error Rate: {report['error_rate_pct']}%)")
    print(f" Total Wall-Clock Time:    {report['total_duration_sec']}s")
    print(f" Throughput (RPS):         {report['requests_per_sec']} req/sec")
    print(f" Average Latency:          {report['avg_latency_ms']} ms")
    print(f" Median Latency:           {report['median_latency_ms']} ms")
    print(f" 95th Percentile Latency:  {report['p95_latency_ms']} ms")
    print(f" 99th Percentile Latency:  {report['p99_latency_ms']} ms")
    print(f" Min Latency:              {report['min_latency_ms']} ms")
    print(f" Max Latency:              {report['max_latency_ms']} ms")
    print("-----------------------------------------------------------------")

    if endpoint_error_details:
        print("\n[!] Sample Error Details (First 5):")
        for err in endpoint_error_details[:5]:
            print(f"    - Endpoint: {err[0]} | Status: {err[1]} | Latency: {round(err[2], 1)}ms | Response: {err[3]}")

    return report

if __name__ == '__main__':
    run_50_concurrent_users_test()
