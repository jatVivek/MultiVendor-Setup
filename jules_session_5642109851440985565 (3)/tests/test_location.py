import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_location():
    print("Testing Location-based Filtering...")
    
    # 1. Get Nearby Products (Exact Match)
    print("1. Get Nearby Products (Exact Match)")
    # Vendor is at 40.7128, -74.0060 (Downtown)
    res = requests.get(f"{BASE_URL}/products/nearby?lat=40.7128&long=-74.0060&radius=1")
    assert res.status_code == 200
    products = res.json()
    assert len(products) >= 1, "Should find products at exact location"
    print("Products found at exact location.")
    
    # 2. Get Nearby Products (Within 10km)
    print("2. Get Nearby Products (Within 10km)")
    # Nearby location: 40.7138, -74.0070 (~150m away)
    res = requests.get(f"{BASE_URL}/products/nearby?lat=40.7138&long=-74.0070&radius=1")
    assert res.status_code == 200
    products = res.json()
    assert len(products) >= 1, "Should find products within 1km"
    print("Products found within radius.")
    
    # 3. Get Nearby Products (Far Away)
    print("3. Get Nearby Products (Far Away)")
    # Far location: 34.0522, -118.2437 (Los Angeles)
    res = requests.get(f"{BASE_URL}/products/nearby?lat=34.0522&long=-118.2437&radius=10")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 0, "Should not find products far away"
    print("No products found far away.")

    print("\nAll location tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_location()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
