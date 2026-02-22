import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_orders():
    print("Testing Order Placement...")
    
    # 1. Login as Vendor
    print("1. Login as Vendor")
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # 2. Add Product
    print("2. Add Product")
    new_product = {
        "name": "Order Coffee",
        "description": "Premium",
        "price": 10.0,
        "quantity": 10,
        "is_active": True
    }
    res = requests.post(f"{BASE_URL}/products", json=new_product, headers=vendor_headers)
    assert res.status_code == 201, f"Add Product failed: {res.text}"
    product_id = res.json()["id"]
    print(f"Product created with ID {product_id}.")
    
    # 3. Login as Customer
    print("3. Login as Customer")
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    assert res.status_code == 200, f"Customer login failed: {res.text}"
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # 4. Place Order (COD)
    print("4. Place Order (COD)")
    order_data = {
        "items": [{"product_id": product_id, "quantity": 2}],
        "payment_method": "COD"
    }
    res = requests.post(f"{BASE_URL}/orders", json=order_data, headers=customer_headers)
    assert res.status_code == 201, f"Place Order failed: {res.text}"
    print("Order placed successfully.")
    
    # Verify stock reduction
    res = requests.get(f"{BASE_URL}/products", headers=customer_headers) # Public or token protected
    # Actually /products is public, but let's assume it returns updated quantity
    # Or better, vendor checks their product list
    res = requests.get(f"{BASE_URL}/vendor/products", headers=vendor_headers)
    products = res.json()
    product = next(p for p in products if p['id'] == product_id)
    assert product['quantity'] == 8, f"Stock not reduced correctly, expected 8, got {product['quantity']}"
    print("Stock reduced correctly.")

    # 5. Place Order (Wallet)
    print("5. Place Order (Wallet)")
    # Sample customer has 100 wallet balance. Price is 10. Qty 1 = 10. Balance -> 90.
    order_data = {
        "items": [{"product_id": product_id, "quantity": 1}],
        "payment_method": "Wallet"
    }
    res = requests.post(f"{BASE_URL}/orders", json=order_data, headers=customer_headers)
    assert res.status_code == 201, f"Place Order (Wallet) failed: {res.text}"
    print("Order (Wallet) placed successfully.")
    
    # Verify wallet deduction (Login again to check user data or fetch profile)
    # The login endpoint returns user data including wallet balance
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_data = res.json().get("user")
    assert customer_data['wallet_balance'] == 90.0, f"Wallet not deducted correctly, expected 90.0, got {customer_data['wallet_balance']}"
    print("Wallet deducted correctly.")
    
    # 6. Get Customer Orders
    print("6. Get Customer Orders")
    res = requests.get(f"{BASE_URL}/customer/orders", headers=customer_headers)
    assert res.status_code == 200, f"Get Orders failed: {res.text}"
    orders = res.json()
    assert len(orders) >= 2, "Orders not found"
    print("Customer orders retrieved.")

    print("\nAll order tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_orders()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
