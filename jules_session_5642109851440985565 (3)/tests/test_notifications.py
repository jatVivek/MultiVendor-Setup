import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000/api"

def test_notifications():
    print("Testing Notifications...")
    
    # Check if log file exists or wait
    if os.path.exists('notifications.log'):
        os.remove('notifications.log')
        
    # Login Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # Add Product & Place Order
    res = requests.post(f"{BASE_URL}/products", json={"name": "Notif Product", "price": 10, "quantity": 10}, headers=vendor_headers)
    product_id = res.json()['id']
    
    res = requests.post(f"{BASE_URL}/orders", json={"items": [{"product_id": product_id, "quantity": 1}], "payment_method": "COD"}, headers=customer_headers)
    order_id = res.json()['order_ids'][0]
    print(f"Order {order_id} placed.")
    
    # Update Status
    requests.put(f"{BASE_URL}/orders/{order_id}/status", json={"status": "Accepted"}, headers=vendor_headers)
    print("Order accepted.")
    
    # Check Log Content
    time.sleep(1) # Allow IO
    assert os.path.exists('notifications.log'), "Notification log not created"
    
    with open('notifications.log', 'r') as f:
        content = f.read()
        print(f"Log content:\n{content}")
        assert f"Your order(s) [{order_id}] have been placed successfully" in content
        assert f"Your order #{order_id} status has been updated to Accepted" in content
        
    print("Notifications verified.")

    print("\nAll notification tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_notifications()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
