import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_security():
    print("Testing Security...")
    
    # Login as Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # 1. Customer tries to add product
    print("1. Customer Add Product Attack")
    new_product = {
        "name": "Hacked Product",
        "price": 0.0,
        "is_active": True
    }
    res = requests.post(f"{BASE_URL}/products", json=new_product, headers=customer_headers)
    assert res.status_code == 403, f"Customer was able to add product! Status: {res.status_code}"
    print("Customer blocked from adding product.")
    
    # Login as Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # Create a product as Vendor
    res = requests.post(f"{BASE_URL}/products", json={"name": "Legit Product", "price": 10, "quantity": 10}, headers=vendor_headers)
    product_id = res.json()['id']
    
    # 2. Customer tries to update product
    print("2. Customer Update Product Attack")
    res = requests.put(f"{BASE_URL}/products/{product_id}", json={"price": 0.0}, headers=customer_headers)
    assert res.status_code == 403, f"Customer was able to update product! Status: {res.status_code}"
    print("Customer blocked from updating product.")
    
    # 3. Customer tries to delete product
    print("3. Customer Delete Product Attack")
    res = requests.delete(f"{BASE_URL}/products/{product_id}", headers=customer_headers)
    assert res.status_code == 403, f"Customer was able to delete product! Status: {res.status_code}"
    print("Customer blocked from deleting product.")
    
    # 4. Delivery Boy Invalid Status Update
    # Login Delivery Boy
    res = requests.post(f"{BASE_URL}/delivery/login", json={"mobile": "5555555555", "password": "delivery123"})
    delivery_token = res.json().get("token")
    delivery_headers = {"Authorization": f"Bearer {delivery_token}"}
    delivery_id = res.json()['user']['id']
    
    # Create order
    res = requests.post(f"{BASE_URL}/orders", json={"items": [{"product_id": product_id, "quantity": 1}]}, headers=customer_headers)
    order_id = res.json()['order_ids'][0]
    
    # Assign (Vendor does this)
    requests.put(f"{BASE_URL}/orders/{order_id}/assign", json={"delivery_boy_id": delivery_id}, headers=vendor_headers)
    
    print("4. Delivery Boy Invalid Status Attack")
    res = requests.put(f"{BASE_URL}/orders/{order_id}/status", json={"status": "Exploded"}, headers=delivery_headers)
    assert res.status_code == 400, f"Invalid status was accepted! Status: {res.status_code}"
    print("Invalid status rejected.")

    print("\nAll security tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_security()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
