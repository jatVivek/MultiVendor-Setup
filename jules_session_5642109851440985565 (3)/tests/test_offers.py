import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_offers():
    print("Testing Discounts & Offers...")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"})
    admin_token = res.json().get("token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Login Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # 1. Add Offer (Admin)
    print("1. Add Offer")
    new_offer = {
        "code": "TEST50_UNIQUE",
        "discount_percentage": 50.0,
        "min_cart_value": 10.0,
        "is_active": True
    }
    # Check if exists first or handle 201/500
    res = requests.post(f"{BASE_URL}/offers", json=new_offer, headers=admin_headers)
    if res.status_code == 201:
        print("Offer created.")
    else:
        # If it failed due to unique constraint, try deleting or using it
        # Just use a unique code per test run or cleanup would be better
        print(f"Offer might exist: {res.text}")
    
    # 2. Add Product
    res = requests.post(f"{BASE_URL}/products", json={"name": "Offer Product", "price": 100.0, "quantity": 10}, headers=vendor_headers)
    product_id = res.json()['id']
    
    # 3. Place Order with Coupon
    print("3. Place Order with Coupon")
    order_data = {
        "items": [{"product_id": product_id, "quantity": 1}],
        "payment_method": "COD",
        "coupon_code": "TEST50_UNIQUE"
    }
    res = requests.post(f"{BASE_URL}/orders", json=order_data, headers=customer_headers)
    assert res.status_code == 201, f"Order with coupon failed: {res.text}"
    order_id = res.json()['order_ids'][0]
    print("Order placed with coupon.")
    
    # Verify Discount
    # Fetch order details (Customer or Admin)
    res = requests.get(f"{BASE_URL}/customer/orders", headers=customer_headers)
    orders = res.json()
    order = next(o for o in orders if o['id'] == order_id)
    
    # Total was 100. Discount 50% = 50. Final = 50.
    assert order['total_amount'] == 50.0, f"Discount not applied correctly. Expected 50.0, got {order['total_amount']}"
    assert order['discount_amount'] == 50.0, f"Discount amount wrong. Expected 50.0, got {order['discount_amount']}"
    print("Discount verified.")
    
    # 4. Invalid Coupon
    print("4. Invalid Coupon")
    order_data['coupon_code'] = "INVALID"
    res = requests.post(f"{BASE_URL}/orders", json=order_data, headers=customer_headers)
    assert res.status_code == 400, "Invalid coupon accepted"
    print("Invalid coupon rejected.")

    print("\nAll offer tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_offers()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
