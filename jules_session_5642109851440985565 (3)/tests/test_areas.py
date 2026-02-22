import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_areas():
    print("Testing Area Management...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Get Areas (Public)
    print("1. Get Areas")
    res = requests.get(f"{BASE_URL}/areas")
    assert res.status_code == 200
    areas = res.json()
    assert len(areas) >= 2, "Sample areas not found"
    print("Areas found.")
    
    # 2. Add Area (Admin)
    print("2. Add Area")
    new_area = {"name": "Test Area", "city": "Test City", "pin_code": "99999"}
    res = requests.post(f"{BASE_URL}/areas", json=new_area, headers=admin_headers)
    assert res.status_code == 201
    area_id = res.json()['id']
    print(f"Area added with ID {area_id}.")
    
    # 3. Update Area (Admin)
    print("3. Update Area")
    res = requests.put(f"{BASE_URL}/areas/{area_id}", json={"name": "Updated Area"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['name'] == "Updated Area"
    print("Area updated.")
    
    # 4. Delete Area (Admin)
    print("4. Delete Area")
    res = requests.delete(f"{BASE_URL}/areas/{area_id}", headers=admin_headers)
    assert res.status_code == 200
    print("Area deleted.")

    print("\nAll area tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_areas()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
