import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000/api"

def test_invoices():
    print("Testing Invoice Generation...")
    
    # Login Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # Add Product & Place Order
    res = requests.post(f"{BASE_URL}/products", json={"name": "Invoice Product", "price": 50, "quantity": 10}, headers=vendor_headers)
    product_id = res.json()['id']
    
    res = requests.post(f"{BASE_URL}/orders", json={"items": [{"product_id": product_id, "quantity": 1}], "payment_method": "COD"}, headers=customer_headers)
    order_id = res.json()['order_ids'][0]
    
    # 1. Download Invoice (Customer)
    print("1. Download Invoice (Customer)")
    res = requests.get(f"{BASE_URL}/orders/{order_id}/invoice", headers=customer_headers)
    assert res.status_code == 200
    assert res.headers['Content-Type'] == 'application/pdf'
    assert len(res.content) > 0
    print("Invoice PDF received.")
    
    # Save for manual inspection if needed
    with open(f"invoice_{order_id}.pdf", "wb") as f:
        f.write(res.content)
    
    # 2. Unauthorized Access
    print("2. Unauthorized Access")
    # New customer trying to access
    res = requests.post(f"{BASE_URL}/customer/register", json={"mobile": "0000000000", "password": "pass"})
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "0000000000", "password": "pass"})
    other_token = res.json().get("token")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    res = requests.get(f"{BASE_URL}/orders/{order_id}/invoice", headers=other_headers)
    assert res.status_code == 403
    print("Unauthorized access blocked.")

    print("\nAll invoice tests passed!")
    
    # Cleanup
    if os.path.exists(f"invoice_{order_id}.pdf"):
        os.remove(f"invoice_{order_id}.pdf")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_invoices()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
