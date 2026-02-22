import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_profiles():
    print("Testing Profile Management...")
    
    # Login Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # 1. Update Customer Profile
    print("1. Update Customer Profile")
    update_data = {"name": "New Name", "email": "newemail@test.com"}
    res = requests.put(f"{BASE_URL}/customer/profile", json=update_data, headers=customer_headers)
    assert res.status_code == 200, f"Update Customer failed: {res.text}"
    user = res.json()['user']
    assert user['name'] == "New Name"
    assert user['email'] == "newemail@test.com"
    print("Customer profile updated.")
    
    # 2. Update Vendor Profile
    print("2. Update Vendor Profile")
    update_data = {"shop_name": "New Shop Name", "min_order_qty": 5}
    res = requests.put(f"{BASE_URL}/vendor/profile", json=update_data, headers=vendor_headers)
    assert res.status_code == 200, f"Update Vendor failed: {res.text}"
    user = res.json()['user']
    assert user['shop_name'] == "New Shop Name"
    assert user['min_order_qty'] == 5
    print("Vendor profile updated.")

    print("\nAll profile tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_profiles()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
