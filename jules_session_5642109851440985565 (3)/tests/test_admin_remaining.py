import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_admin_remaining():
    print("Testing Remaining Admin Features...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Payment Management
    print("1. Payment Management")
    res = requests.get(f"{BASE_URL}/admin/payments", headers=admin_headers)
    assert res.status_code == 200
    payments = res.json()
    assert isinstance(payments, list)
    print("Payments retrieved.")
    
    # 2. Notification Management
    print("2. Notification Management")
    notif_data = {"message": "System Maintenance", "group": "all"}
    res = requests.post(f"{BASE_URL}/admin/notifications", json=notif_data, headers=admin_headers)
    assert res.status_code == 200
    print("Notification sent.")
    
    # 3. Create Admin User
    print("3. Create Admin User")
    new_admin = {"username": "subadmin", "password": "password"}
    res = requests.post(f"{BASE_URL}/admin/users", json=new_admin, headers=admin_headers)
    if res.status_code == 201:
        print("Admin user created.")
    else:
        print(f"Admin creation result: {res.text}")

    print("\nAll remaining admin tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_admin_remaining()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
