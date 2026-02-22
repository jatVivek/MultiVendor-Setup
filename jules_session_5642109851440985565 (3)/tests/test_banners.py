import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_banners():
    print("Testing Banner Management...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Get Banners (Public)
    print("1. Get Banners")
    res = requests.get(f"{BASE_URL}/banners")
    assert res.status_code == 200
    banners = res.json()
    assert len(banners) >= 2, "Sample banners not found"
    print("Banners found.")
    
    # Filter by type
    res = requests.get(f"{BASE_URL}/banners?type=Home")
    assert res.status_code == 200
    home_banners = res.json()
    assert all(b['type'] == 'Home' for b in home_banners)
    print("Filtered banners found.")
    
    # 2. Add Banner (Admin)
    print("2. Add Banner")
    new_banner = {"image_url": "test.jpg", "type": "Home"}
    res = requests.post(f"{BASE_URL}/banners", json=new_banner, headers=admin_headers)
    assert res.status_code == 201
    banner_id = res.json()['id']
    print(f"Banner added with ID {banner_id}.")
    
    # 3. Delete Banner (Admin)
    print("3. Delete Banner")
    res = requests.delete(f"{BASE_URL}/banners/{banner_id}", headers=admin_headers)
    assert res.status_code == 200
    print("Banner deleted.")

    print("\nAll banner tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_banners()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
