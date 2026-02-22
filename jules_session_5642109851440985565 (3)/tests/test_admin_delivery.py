import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_admin_delivery():
    print("Testing Admin Delivery Boy Management...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Get Delivery Boys
    print("1. Get Delivery Boys")
    res = requests.get(f"{BASE_URL}/admin/delivery_boys", headers=admin_headers)
    assert res.status_code == 200
    boys = res.json()
    assert len(boys) >= 1
    boy_id = boys[0]['id']
    print(f"Delivery Boys found. Testing with ID {boy_id}.")
    
    # 2. Deactivate
    print("2. Deactivate")
    res = requests.put(f"{BASE_URL}/admin/delivery_boys/{boy_id}/status", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['delivery_boy']['is_active'] == False
    print("Delivery Boy deactivated.")
    
    # 3. Activate
    print("3. Activate")
    res = requests.put(f"{BASE_URL}/admin/delivery_boys/{boy_id}/status", json={"is_active": True}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['delivery_boy']['is_active'] == True
    print("Delivery Boy activated.")

    print("\nAll admin delivery tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_admin_delivery()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
