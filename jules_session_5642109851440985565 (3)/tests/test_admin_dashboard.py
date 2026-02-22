import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_admin_dashboard():
    print("Testing Admin Dashboard...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get Dashboard
    res = requests.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
    assert res.status_code == 200, f"Dashboard failed: {res.text}"
    data = res.json()
    
    print("Dashboard Data:", data)
    assert 'total_users' in data
    assert 'total_vendors' in data
    assert 'total_delivery_boys' in data
    assert 'total_orders' in data
    assert 'total_revenue' in data
    
    # Verify values (based on sample data)
    # 1 Customer, 1 Vendor, 1 Delivery Boy, 0 Orders (initially)
    # If previous tests ran, might be more. But at least >= 1
    assert data['total_users'] >= 1
    assert data['total_vendors'] >= 1
    
    print("Dashboard verified.")

    print("\nAll dashboard tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_admin_dashboard()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
