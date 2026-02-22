import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_vendor_dashboard():
    print("Testing Vendor Dashboard...")
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # 1. Get Dashboard
    print("1. Get Vendor Dashboard")
    res = requests.get(f"{BASE_URL}/vendor/dashboard", headers=vendor_headers)
    assert res.status_code == 200, f"Dashboard failed: {res.text}"
    data = res.json()
    
    print("Vendor Dashboard Data:", data)
    assert 'total_orders' in data
    assert 'total_sales' in data
    assert 'total_customers' in data
    
    # Values might be 0 or >0 depending on previous tests, just check structure
    assert isinstance(data['total_orders'], int)
    
    print("Vendor Dashboard verified.")

    print("\nAll vendor dashboard tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_vendor_dashboard()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
