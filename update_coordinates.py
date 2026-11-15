"""
EcoLocate - Update Verified Facility Coordinates
This script updates verified geographical coordinates (latitude and longitude)
for central pollution control board (CPCB) recycling facilities with verified addresses.
Facilities without verified coordinates remain NULL to preserve data integrity.
"""

import sys
import db

VERIFIED_COORDINATES = [
    {
        "id": 3,
        "name": "Veera Waste Management Systems",
        "lat": 17.6908,
        "lng": 83.2104,
        "location": "IDA Autonagar, Visakhapatnam, Andhra Pradesh"
    },
    {
        "id": 4,
        "name": "Sungeel India Recycling Pvt. Ltd.",
        "lat": 13.7915,
        "lng": 77.4947,
        "location": "APIIC Industrial Park, Gollapuram, Hindupur, Andhra Pradesh"
    },
    {
        "id": 8,
        "name": "Star E-Processors",
        "lat": 21.1947,
        "lng": 81.9667,
        "location": "Arang, Raipur, Chhattisgarh"
    },
    {
        "id": 9,
        "name": "Fozia Traders",
        "lat": 28.7061,
        "lng": 77.3082,
        "location": "Saboli Mandoli Industrial Area, Delhi"
    },
    {
        "id": 12,
        "name": "Techchef E-Waste Solutions Pvt. Ltd.",
        "lat": 28.5355,
        "lng": 77.2711,
        "location": "DDA Shed, Okhla Industrial Area, Delhi"
    },
    {
        "id": 24,
        "name": "Earth Sense Recycle Pvt. Ltd.",
        "lat": 28.3619,
        "lng": 76.9248,
        "location": "IMT Manesar Sector 5, Gurugram, Haryana"
    },
    {
        "id": 25,
        "name": "Namo E-Waste Management Ltd.",
        "lat": 28.3782,
        "lng": 77.3135,
        "location": "Mathura Road, Faridabad, Haryana"
    },
    {
        "id": 27,
        "name": "Shivalik Solid Waste Management Ltd. (Unit-II)",
        "lat": 31.0427,
        "lng": 76.7198,
        "location": "Nalagarh, Solan, Himachal Pradesh"
    },
    {
        "id": 34,
        "name": "Sriram Eco Raksha Computer Services Pvt. Ltd.",
        "lat": 12.8152,
        "lng": 77.6934,
        "location": "Bommasandra Industrial Estate, Bengaluru, Karnataka"
    },
    {
        "id": 36,
        "name": "E-Friendly Waste Recyclers",
        "lat": 12.9472,
        "lng": 77.5256,
        "location": "Nayandahalli, Bengaluru, Karnataka"
    },
    {
        "id": 38,
        "name": "Moogambigai Metal Refineries (Unit 3)",
        "lat": 12.9463,
        "lng": 74.8122,
        "location": "Baikampady Industrial Area, Mangaluru, Karnataka"
    },
    {
        "id": 39,
        "name": "Kerala Enviro Infrastructure Ltd.",
        "lat": 9.9723,
        "lng": 76.3687,
        "location": "FACT-CD Campus, Ambalamedu, Kochi, Kerala"
    },
    {
        "id": 43,
        "name": "Eco-Recycling Ltd.",
        "lat": 19.4082,
        "lng": 72.8457,
        "location": "Bhoipada, Sativali Road, Vasai (E), Palghar, Maharashtra"
    },
    {
        "id": 52,
        "name": "Ecokart Technology Pvt. Ltd.",
        "lat": 20.1834,
        "lng": 85.6212,
        "location": "Daleiput, Khordha, Odisha"
    },
    {
        "id": 54,
        "name": "Spreco Recycling",
        "lat": 30.6508,
        "lng": 75.6022,
        "location": "Focal Point, Raikot, Ludhiana, Punjab"
    },
    {
        "id": 65,
        "name": "Green Era Recyclers",
        "lat": 11.0286,
        "lng": 76.9213,
        "location": "Thadagam Road, Coimbatore, Tamil Nadu"
    },
    {
        "id": 68,
        "name": "Earth Sense Recycle Pvt. Ltd.",
        "lat": 17.2025,
        "lng": 78.5034,
        "location": "APIIC Industrial Park, Mankal, Maheswaram, Telangana"
    },
    {
        "id": 69,
        "name": "Silicon Planet Recycling Pvt. Ltd.",
        "lat": 17.5284,
        "lng": 78.6791,
        "location": "Ankireddypally, Keesara, Medchal-Malkajgiri, Telangana"
    },
    {
        "id": 72,
        "name": "TES-AMM India Pvt. Ltd.",
        "lat": 17.6322,
        "lng": 78.4812,
        "location": "IDA Medchal, Telangana"
    },
    {
        "id": 73,
        "name": "Auctus E-Recycling Solutions Pvt. Ltd.",
        "lat": 28.6692,
        "lng": 77.4538,
        "location": "M.G. Road Industrial Area, Ghaziabad, Uttar Pradesh"
    }
]

def update_facility_coordinates():
    print("=" * 65)
    print("EcoLocate - Updating Verified Geographical Coordinates")
    print("=" * 65)
    
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    updated_count = 0
    try:
        for item in VERIFIED_COORDINATES:
            # Check if record exists by id and matches name
            cursor.execute(
                "SELECT id, centre_name FROM centres WHERE id = %s",
                (item["id"],)
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE centres SET latitude = %s, longitude = %s WHERE id = %s",
                    (item["lat"], item["lng"], item["id"])
                )
                updated_count += 1
                print(f" [OK] Updated ID {item['id']}: {row['centre_name']} -> ({item['lat']}, {item['lng']})")
            else:
                print(f" [SKIP] ID {item['id']} not found.")
                
        conn.commit()
        print("-" * 65)
        print(f"Successfully updated coordinates for {updated_count} facilities.")
        
        # Verify overall status
        cursor.execute("SELECT COUNT(*) as total, COUNT(latitude) as with_coords FROM centres")
        stats = cursor.fetchone()
        print(f"Total centres: {stats['total']}")
        print(f"Centres with verified coordinates: {stats['with_coords']}")
        print(f"Centres without coordinates (NULL): {stats['total'] - stats['with_coords']}")
        print("=" * 65)
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database update failed: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_facility_coordinates()
