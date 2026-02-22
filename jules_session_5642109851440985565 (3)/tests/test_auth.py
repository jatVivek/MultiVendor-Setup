import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_auth():
    print("Testing Authentication...")
    
    # 1. Admin Login (Legacy)
    print("1. Admin Login")
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    token = res.json().get("token")
    assert token, "Admin token missing"
    print("Admin login successful.")
    
    # 2. Customer Register & Login
    print("2. Customer Register & Login")
    customer_data = {"mobile": "9999999999", "password": "pass", "name": "Test Customer", "email": "test@test.com"}
    res = requests.post(f"{BASE_URL}/customer/register", json=customer_data)
    if res.status_code != 201:
        # Might already exist if re-running
        assert res.status_code == 400 and "already registered" in res.text, f"Customer register failed: {res.text}"
        print("Customer already registered.")
    else:
        print("Customer registered.")
        
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "9999999999", "password": "pass"})
    assert res.status_code == 200, f"Customer login failed: {res.text}"
    token = res.json().get("token")
    assert token, "Customer token missing"
    user_data = res.json().get("user")
    assert user_data['mobile'] == "9999999999", "Incorrect user data"
    print("Customer login successful.")

    # 3. Vendor Register & Login
    print("3. Vendor Register & Login")
    vendor_data = {"mobile": "8888888888", "password": "pass", "shop_name": "Test Shop", "owner_name": "Owner", "address": "Address"}
    res = requests.post(f"{BASE_URL}/vendor/register", json=vendor_data)
    if res.status_code != 201:
        assert res.status_code == 400 and "already registered" in res.text, f"Vendor register failed: {res.text}"
        print("Vendor already registered.")
    else:
        print("Vendor registered.")
        
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "8888888888", "password": "pass"})
    assert res.status_code == 200, f"Vendor login failed: {res.text}"
    token = res.json().get("token")
    assert token, "Vendor token missing"
    print("Vendor login successful.")

    # 4. Delivery Boy Register & Login
    print("4. Delivery Boy Register & Login")
    delivery_data = {"mobile": "7777777777", "password": "pass", "name": "Test Boy", "vehicle_no": "Bike1"}
    res = requests.post(f"{BASE_URL}/delivery/register", json=delivery_data)
    if res.status_code != 201:
        assert res.status_code == 400 and "already registered" in res.text, f"Delivery register failed: {res.text}"
        print("Delivery Boy already registered.")
    else:
        print("Delivery Boy registered.")
        
    res = requests.post(f"{BASE_URL}/delivery/login", json={"mobile": "7777777777", "password": "pass"})
    assert res.status_code == 200, f"Delivery login failed: {res.text}"
    token = res.json().get("token")
    assert token, "Delivery token missing"
    print("Delivery Boy login successful.")

    print("\nAll auth tests passed!")

if __name__ == "__main__":
    try:
        # Wait for server to start if just launched
        time.sleep(2)
        test_auth()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
