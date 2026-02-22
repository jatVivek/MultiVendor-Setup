from playwright.sync_api import sync_playwright
import time

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Home Page
        print("Navigating to Home...")
        page.goto("http://127.0.0.1:5000/")
        # Wait for dynamic content loading in app.js
        page.wait_for_selector("text=Featured Products")
        page.screenshot(path="verification/home.png")
        print("Home screenshot taken.")
        
        # 2. Product Listing (PLP)
        print("Navigating to PLP...")
        page.evaluate("app.router('products')")
        page.wait_for_selector("text=FILTERS")
        page.screenshot(path="verification/plp.png")
        print("PLP screenshot taken.")
        
        # 3. Product Detail (PDP)
        print("Navigating to PDP...")
        # Use ID 1 which is seeded
        page.evaluate("app.router('product/1')")
        page.wait_for_selector("text=ADD TO BAG")
        page.screenshot(path="verification/pdp.png")
        print("PDP screenshot taken.")
        
        # 4. Cart (Empty)
        print("Navigating to Cart...")
        page.evaluate("app.router('cart')")
        page.wait_for_selector("text=feels so light")
        page.screenshot(path="verification/cart.png")
        print("Cart screenshot taken.")
        
        browser.close()

if __name__ == "__main__":
    verify_frontend()
