import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000/api"

def test_vendor_bulk_invoices():
    print("Testing Vendor Bulk Invoices...")
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # 1. Download Bulk Invoices
    print("1. Download Bulk Invoices")
    res = requests.get(f"{BASE_URL}/vendor/invoices/bulk", headers=vendor_headers)
    assert res.status_code == 200
    assert "application/zip" in res.headers['Content-Type']
    assert len(res.content) > 0
    print("Zip file received.")
    
    # Optional: Save to check
    with open("bulk_invoices.zip", "wb") as f:
        f.write(res.content)
        
    print("\nAll bulk invoice tests passed!")
    
    # Cleanup
    if os.path.exists("bulk_invoices.zip"):
        os.remove("bulk_invoices.zip")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_vendor_bulk_invoices()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
