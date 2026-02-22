import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_admin_users():
    print("Testing Admin User Management...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Get Customers
    print("1. Get Customers")
    res = requests.get(f"{BASE_URL}/admin/customers", headers=admin_headers)
    assert res.status_code == 200
    customers = res.json()
    assert len(customers) >= 1
    customer_id = customers[0]['id']
    print(f"Customers found. Testing with ID {customer_id}.")
    
    # 2. Deactivate Customer
    print("2. Deactivate Customer")
    res = requests.put(f"{BASE_URL}/admin/customers/{customer_id}/status", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['user']['is_active'] == False
    print("Customer deactivated.")
    
    # 3. Activate Customer
    print("3. Activate Customer")
    res = requests.put(f"{BASE_URL}/admin/customers/{customer_id}/status", json={"is_active": True}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['user']['is_active'] == True
    print("Customer activated.")

    print("\nAll admin user tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_admin_users()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
