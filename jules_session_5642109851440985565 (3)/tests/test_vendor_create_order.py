import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_vendor_create_order():
    print("Testing Vendor Create Order...")
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # Add Product
    res = requests.post(f"{BASE_URL}/products", json={"name": "Vendor Created Product", "price": 20.0, "quantity": 10}, headers=vendor_headers)
    product_id = res.json()['id']
    
    # 1. Create Order for Customer
    print("1. Create Order for Customer")
    # Customer created in database.py has mobile 1234567890
    order_data = {
        "customer_mobile": "1234567890",
        "items": [{"product_id": product_id, "quantity": 2}]
    }
    res = requests.post(f"{BASE_URL}/vendor/orders", json=order_data, headers=vendor_headers)
    assert res.status_code == 201, f"Vendor create order failed: {res.text}"
    order_id = res.json()['order_id']
    print(f"Order created with ID {order_id}.")
    
    # 2. Verify Order
    print("2. Verify Order")
    res = requests.get(f"{BASE_URL}/vendor/orders", headers=vendor_headers)
    orders = res.json()
    order = next((o for o in orders if o['id'] == order_id), None)
    assert order is not None
    assert order['total_amount'] == 40.0
    print("Order verified in vendor list.")

    print("\nAll vendor create order tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_vendor_create_order()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
