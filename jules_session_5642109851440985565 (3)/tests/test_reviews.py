import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_reviews():
    print("Testing Reviews & Ratings...")
    
    # Login Customer
    res = requests.post(f"{BASE_URL}/customer/login", json={"mobile": "1234567890", "password": "customer123"})
    customer_token = res.json().get("token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Login Vendor
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    vendor_token = res.json().get("token")
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
    
    # Login Delivery
    res = requests.post(f"{BASE_URL}/delivery/login", json={"mobile": "5555555555", "password": "delivery123"})
    delivery_token = res.json().get("token")
    delivery_headers = {"Authorization": f"Bearer {delivery_token}"}
    
    # Add Product
    res = requests.post(f"{BASE_URL}/products", json={"name": "Review Product", "price": 10.0, "quantity": 10}, headers=vendor_headers)
    product_id = res.json()['id']
    
    # 1. Try to review without purchase
    print("1. Review without purchase")
    review_data = {"rating": 5, "comment": "Great!"}
    res = requests.post(f"{BASE_URL}/products/{product_id}/reviews", json=review_data, headers=customer_headers)
    assert res.status_code == 403, "Allowed review without purchase"
    print("Blocked review without purchase.")
    
    # 2. Purchase and Deliver
    print("2. Purchase and Deliver")
    res = requests.post(f"{BASE_URL}/orders", json={"items": [{"product_id": product_id, "quantity": 1}], "payment_method": "COD"}, headers=customer_headers)
    order_id = res.json()['order_ids'][0]
    
    # Vendor Accept & Assign
    requests.put(f"{BASE_URL}/orders/{order_id}/status", json={"status": "Accepted"}, headers=vendor_headers)
    # Corrected method to POST for login to get delivery ID
    delivery_res = requests.post(f"{BASE_URL}/delivery/login", json={"mobile": "5555555555", "password": "delivery123"})
    delivery_id = delivery_res.json()['user']['id']
    requests.put(f"{BASE_URL}/orders/{order_id}/assign", json={"delivery_boy_id": delivery_id}, headers=vendor_headers)
    
    # Delivery Boy Deliver
    requests.put(f"{BASE_URL}/orders/{order_id}/status", json={"status": "Delivered"}, headers=delivery_headers)
    print("Order delivered.")
    
    # 3. Add Review
    print("3. Add Review")
    res = requests.post(f"{BASE_URL}/products/{product_id}/reviews", json=review_data, headers=customer_headers)
    assert res.status_code == 201, f"Review failed: {res.text}"
    print("Review added.")
    
    # 4. Get Reviews
    print("4. Get Reviews")
    res = requests.get(f"{BASE_URL}/products/{product_id}/reviews")
    assert res.status_code == 200
    reviews = res.json()
    assert len(reviews) == 1
    assert reviews[0]['rating'] == 5
    print("Reviews retrieved.")

    print("\nAll review tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_reviews()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
