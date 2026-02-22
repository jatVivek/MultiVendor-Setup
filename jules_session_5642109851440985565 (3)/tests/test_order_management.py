import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_order_management():
    print("Testing Order Management...")
    
    # 1. Login Agents
    print("1. Logging in Agents")
    # Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    vendor_id = res.json()['user']['id']
    
    # Delivery Boy
    res = requests.post(f"{BASE_URL}/delivery/login", json={"mobile": "5555555555", "password": "delivery123"})
    delivery_token = res.json().get("token")
    delivery_headers = {"Authorization": f"Bearer {delivery_token}"}
    delivery_id = res.json()['user']['id']
    
    # Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("Agents logged in.")
    
    # 2. Add Product & Place Order
    print("2. Placing Order")
    new_product = {
        "name": "Management Coffee",
        "description": "Premium",
        "price": 10.0,
        "quantity": 10,
        "is_active": True
    }
    res = requests.post(f"{BASE_URL}/products", json=new_product, headers=vendor_headers)
    product_id = res.json()["id"]
    
    order_data = {
        "items": [{"product_id": product_id, "quantity": 1}],
        "payment_method": "COD"
    }
    res = requests.post(f"{BASE_URL}/orders", json=order_data, headers=customer_headers)
    order_id = res.json()["order_ids"][0]
    print(f"Order placed with ID {order_id}.")
    
    # 3. Vendor Views & Accepts
    print("3. Vendor Processing")
    res = requests.get(f"{BASE_URL}/vendor/orders", headers=vendor_headers)
    orders = res.json()
    assert any(o['id'] == order_id for o in orders), "Order not found in vendor list"
    
    res = requests.put(f"{BASE_URL}/orders/{order_id}/status", json={"status": "Accepted"}, headers=vendor_headers)
    assert res.status_code == 200, f"Status update failed: {res.text}"
    assert res.json()['order']['status'] == "Accepted", "Status not updated"
    
    # Assign Delivery Boy
    res = requests.put(f"{BASE_URL}/orders/{order_id}/assign", json={"delivery_boy_id": delivery_id}, headers=vendor_headers)
    assert res.status_code == 200, f"Assignment failed: {res.text}"
    assert res.json()['order']['delivery_boy_id'] == delivery_id, "Delivery boy not assigned"
    print("Order accepted and assigned.")
    
    # 4. Delivery Boy Views & Updates
    print("4. Delivery Processing")
    res = requests.get(f"{BASE_URL}/delivery/orders", headers=delivery_headers)
    orders = res.json()
    assert any(o['id'] == order_id for o in orders), "Order not found in delivery list"
    
    res = requests.put(f"{BASE_URL}/orders/{order_id}/status", json={"status": "Picked Up"}, headers=delivery_headers)
    assert res.status_code == 200, f"Delivery status update failed: {res.text}"
    assert res.json()['order']['status'] == "Picked Up", "Status not updated to Picked Up"
    print("Order picked up.")
    
    # 5. Admin Views
    print("5. Admin View")
    res = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers)
    orders = res.json()
    order = next(o for o in orders if o['id'] == order_id)
    assert order['status'] == "Picked Up", f"Admin sees wrong status: {order['status']}"
    assert order['delivery_boy_id'] == delivery_id, "Admin sees wrong delivery boy"
    print("Admin view correct.")

    print("\nAll management tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_order_management()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
