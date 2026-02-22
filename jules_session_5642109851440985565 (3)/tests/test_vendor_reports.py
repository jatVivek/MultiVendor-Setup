import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_vendor_reports():
    print("Testing Vendor Reports...")
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # 1. Export Orders (CSV)
    print("1. Export Orders")
    res = requests.get(f"{BASE_URL}/vendor/orders/export", headers=vendor_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers['Content-Type']
    content = res.text
    assert "Order ID" in content
    print("CSV Export received.")
    
    # 2. Get Transactions
    print("2. Get Transactions")
    res = requests.get(f"{BASE_URL}/vendor/transactions", headers=vendor_headers)
    assert res.status_code == 200
    transactions = res.json()
    assert isinstance(transactions, list)
    if len(transactions) > 0:
        assert 'transaction_id' in transactions[0]
    print("Transactions retrieved.")

    print("\nAll vendor report tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_vendor_reports()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
