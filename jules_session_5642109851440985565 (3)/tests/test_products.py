import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_products():
    print("Testing Product & Category Management...")
    
    # 1. Login as Vendor
    print("1. Login as Vendor")
    # Using the sample vendor created in database.py
    res = requests.post(f"{BASE_URL}/vendor/login", json={"mobile": "9876543210", "password": "vendor123"})
    assert res.status_code == 200, f"Vendor login failed: {res.text}"
    token = res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Vendor login successful.")
    
    # 2. Get Categories
    print("2. Get Categories")
    res = requests.get(f"{BASE_URL}/categories")
    assert res.status_code == 200, f"Get Categories failed: {res.text}"
    categories = res.json()
    assert len(categories) > 0, "No categories found"
    cat_id = categories[0]['id']
    print(f"Categories found. Using ID {cat_id}")

    # 3. Add Product
    print("3. Add Product")
    new_product = {
        "name": "Vendor Coffee",
        "description": "Premium",
        "price": 10.0,
        "category_id": cat_id,
        "quantity": 50,
        "is_active": True
    }
    res = requests.post(f"{BASE_URL}/products", json=new_product, headers=headers)
    assert res.status_code == 201, f"Add Product failed: {res.text}"
    product_id = res.json()["id"]
    print(f"Product created with ID {product_id}.")
    
    # 4. Get Vendor Products
    print("4. Get Vendor Products")
    res = requests.get(f"{BASE_URL}/vendor/products", headers=headers)
    assert res.status_code == 200, f"Get Vendor Products failed: {res.text}"
    products = res.json()
    assert any(p['id'] == product_id for p in products), "New product not found in vendor list"
    print("Vendor products retrieved.")
    
    # 5. Update Product
    print("5. Update Product")
    res = requests.put(f"{BASE_URL}/products/{product_id}", json={"price": 12.0}, headers=headers)
    assert res.status_code == 200, f"Update Product failed: {res.text}"
    updated_product = res.json()
    assert updated_product['price'] == 12.0, "Price not updated"
    print("Product updated.")
    
    # 6. Delete Product
    print("6. Delete Product")
    res = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    assert res.status_code == 200, f"Delete Product failed: {res.text}"
    
    res = requests.get(f"{BASE_URL}/vendor/products", headers=headers)
    products = res.json()
    assert not any(p['id'] == product_id for p in products), "Product still in vendor list"
    print("Product deleted.")

    print("\nAll product tests passed!")

if __name__ == "__main__":
    try:
        time.sleep(2)
        test_products()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        exit(1)
