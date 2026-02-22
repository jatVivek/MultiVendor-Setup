import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_admin_vendors():
    print("Testing Admin Vendor Management...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Get Vendors
    print("1. Get Vendors")
    res = requests.get(f"{BASE_URL}/admin/vendors", headers=admin_headers)
    assert res.status_code == 200
    vendors = res.json()
    assert len(vendors) >= 1
    vendor_id = vendors[0]['id']
    print(f"Vendors found. Testing with ID {vendor_id}.")
    
    # 2. Reject Vendor (Deactivate)
    print("2. Reject Vendor")
    res = requests.put(f"{BASE_URL}/admin/vendors/{vendor_id}/approve", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['vendor']['is_active'] == False
    print("Vendor rejected.")
    
    # 3. Approve Vendor
    print("3. Approve Vendor")
    res = requests.put(f"{BASE_URL}/admin/vendors/{vendor_id}/approve", json={"is_active": True}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['vendor']['is_active'] == True
    print("Vendor approved.")

    print("\nAll admin vendor tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_admin_vendors()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
