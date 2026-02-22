from flask import Flask
from config import Config
from models import db, SiteSettings, User, Product, Blog, Customer, Vendor, DeliveryBoy, Category, SubCategory, Area, Banner, Address, Offer, Review, StaticPage
import json
from datetime import datetime, timedelta

def init_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Create default settings if not exists
        if not SiteSettings.query.first():
            settings = SiteSettings(
                brand_name="Zenbrew",
                logo_url="/static/uploads/logo.svg", # Placeholder
                seo_title="Zenbrew - Coffee & Joy",
                seo_meta_desc="Experience the joy of exceptional coffee.",
                navbar_links=json.dumps([
                    {"name": "Home", "url": "/"},
                    {"name": "Menu", "url": "#products"},
                    {"name": "Blog", "url": "#blogs"},
                    {"name": "About", "url": "#about"}
                ]),
                footer_links=json.dumps([
                    {"name": "Contact", "url": "#contact"},
                    {"name": "Privacy", "url": "#privacy"}
                ]),
                hero_title="Coffee & Joy",
                hero_subtitle="Experience the joy of exceptional coffee in our cozy space.",
                hero_video_url="https://www.w3schools.com/html/mov_bbb.mp4" # Placeholder
            )
            db.session.add(settings)
            print("Default settings created.")

        # Create admin user if not exists
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("Admin user created (admin/admin123).")

        # Create Areas
        if not Area.query.first():
            area1 = Area(name="Downtown", city="Metropolis", pin_code="10001")
            area2 = Area(name="Uptown", city="Metropolis", pin_code="10002")
            db.session.add_all([area1, area2])
            db.session.commit()
            print("Areas created.")

        # Create Categories
        if not Category.query.first():
            cat1 = Category(name="Beverages", image_url="/static/uploads/cat-bev.png")
            cat2 = Category(name="Snacks", image_url="/static/uploads/cat-snack.png")
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            sub1 = SubCategory(category_id=cat1.id, name="Coffee", image_url="/static/uploads/sub-coffee.png")
            sub2 = SubCategory(category_id=cat1.id, name="Tea", image_url="/static/uploads/sub-tea.png")
            sub3 = SubCategory(category_id=cat2.id, name="Pastries", image_url="/static/uploads/sub-pastry.png")
            db.session.add_all([sub1, sub2, sub3])
            db.session.commit()
            print("Categories created.")

        # Create Banners
        if not Banner.query.first():
            b1 = Banner(image_url="/static/uploads/banner1.jpg", type="Home")
            b2 = Banner(image_url="/static/uploads/banner2.jpg", type="Category", category_id=cat1.id)
            db.session.add_all([b1, b2])
            db.session.commit()
            print("Banners created.")

        # Create Vendor
        if not Vendor.query.first():
            area = Area.query.filter_by(name="Downtown").first()
            vendor = Vendor(
                mobile="9876543210",
                shop_name="Zenbrew Main Branch",
                owner_name="John Doe",
                address="123 Coffee St",
                is_active=True,
                area_id=area.id
            )
            vendor.set_password("vendor123")
            db.session.add(vendor)
            db.session.commit()
            
            # Add Vendor Address with Lat/Long
            v_addr = Address(vendor_id=vendor.id, address_line="123 Coffee St", city="Metropolis", lat=40.7128, long=-74.0060)
            db.session.add(v_addr)
            db.session.commit()
            
            print("Vendor created (9876543210/vendor123).")

        # Create Customer
        if not Customer.query.first():
            customer = Customer(
                mobile="1234567890",
                name="Alice Wonder",
                email="alice@example.com",
                wallet_balance=100.0
            )
            customer.set_password("customer123")
            db.session.add(customer)
            db.session.commit()
            
            # Add Customer Address
            c_addr = Address(customer_id=customer.id, address_line="456 Maple Ave", city="Metropolis", lat=40.7138, long=-74.0070) # Nearby
            db.session.add(c_addr)
            db.session.commit()
            
            print("Customer created (1234567890/customer123).")

        # Create Delivery Boy
        if not DeliveryBoy.query.first():
            area = Area.query.filter_by(name="Downtown").first()
            dboy = DeliveryBoy(
                mobile="5555555555",
                name="Bob Builder",
                vehicle_no="AB-12-3456",
                is_active=True,
                area_id=area.id
            )
            dboy.set_password("delivery123")
            db.session.add(dboy)
            db.session.commit()
            print("Delivery Boy created (5555555555/delivery123).")

        # Create sample products linked to vendor and category
        if not Product.query.first():
            vendor = Vendor.query.first()
            cat = Category.query.filter_by(name="Beverages").first()
            sub = SubCategory.query.filter_by(name="Coffee").first()
            
            products = [
                Product(name="Espresso", description="Rich and bold shot of coffee", price=3.30, 
                        vendor_id=vendor.id, category_id=cat.id, sub_category_id=sub.id, image_url="/static/uploads/coffee-1.png", quantity=100),
                Product(name="Cappuccino", description="Espresso with steamed milk and foam", price=4.50, 
                        vendor_id=vendor.id, category_id=cat.id, sub_category_id=sub.id, image_url="/static/uploads/coffee-2.png", quantity=50),
            ]
            db.session.add_all(products)
            print("Sample products created.")

        # Create sample offers
        if not Offer.query.first():
            offer = Offer(
                code="WELCOME10",
                discount_percentage=10.0,
                max_amount=50.0,
                min_cart_value=100.0,
                valid_until=datetime.now() + timedelta(days=30)
            )
            db.session.add(offer)
            print("Sample offer created.")

        # Create sample blogs
        if not Blog.query.first():
            blogs = [
                Blog(title="Our Journey", content="Founded in 2000, Zenbrew started as a small café...", image_url="/static/uploads/blog-1.jpg", video_url="https://www.youtube.com/embed/dQw4w9WgXcQ"),
                Blog(title="Brewing Tips", content="How to make the perfect cup at home...", image_url="/static/uploads/blog-2.jpg")
            ]
            db.session.add_all(blogs)
            print("Sample blogs created.")

        # Create static pages
        if not StaticPage.query.first():
            p1 = StaticPage(slug="privacy-policy", title="Privacy Policy", content="Your privacy is important to us...")
            p2 = StaticPage(slug="terms-conditions", title="Terms & Conditions", content="By using our app, you agree to...")
            p3 = StaticPage(slug="faqs", title="FAQs", content="Q: How to order? A: Just click!")
            db.session.add_all([p1, p2, p3])
            db.session.commit()
            print("Static pages created.")

        db.session.commit()
        print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
