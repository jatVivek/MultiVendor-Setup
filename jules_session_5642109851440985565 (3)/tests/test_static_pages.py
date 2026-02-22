import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_static_pages():
    print("Testing Static Page Management...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Get Page (Public)
    print("1. Get Page")
    res = requests.get(f"{BASE_URL}/pages/privacy-policy")
    assert res.status_code == 200
    page = res.json()
    assert page['title'] == "Privacy Policy"
    print("Page retrieved.")
    
    # 2. Update Page (Admin)
    print("2. Update Page")
    update_data = {"content": "Updated Privacy Policy Content"}
    res = requests.put(f"{BASE_URL}/admin/pages/privacy-policy", json=update_data, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()['content'] == "Updated Privacy Policy Content"
    print("Page updated.")
    
    # 3. Get All Pages (Admin)
    print("3. Get All Pages")
    res = requests.get(f"{BASE_URL}/admin/pages", headers=admin_headers)
    assert res.status_code == 200
    pages = res.json()
    assert len(pages) >= 3
    print("All pages retrieved.")

    print("\nAll static page tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_static_pages()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
