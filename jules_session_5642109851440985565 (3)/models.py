from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json

db = SQLAlchemy()

# --- Core Models ---

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(100), default="Zenbrew")
    logo_url = db.Column(db.String(255), nullable=True)
    seo_title = db.Column(db.String(255), default="Zenbrew - Coffee & Joy")
    seo_meta_desc = db.Column(db.String(500), default="Experience the joy of exceptional coffee.")
    navbar_links = db.Column(db.Text, default='[{"name": "Home", "url": "/"}, {"name": "Menu", "url": "#menu"}, {"name": "Blog", "url": "#blog"}]')
    footer_links = db.Column(db.Text, default='[{"name": "Contact", "url": "#contact"}, {"name": "Privacy", "url": "#privacy"}]')
    hero_title = db.Column(db.String(255), default="Coffee & Joy")
    hero_subtitle = db.Column(db.String(255), default="Experience the joy of exceptional coffee in our cozy space.")
    hero_video_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "brand_name": self.brand_name,
            "logo_url": self.logo_url,
            "seo_title": self.seo_title,
            "seo_meta_desc": self.seo_meta_desc,
            "navbar_links": json.loads(self.navbar_links),
            "footer_links": json.loads(self.footer_links),
            "hero_title": self.hero_title,
            "hero_subtitle": self.hero_subtitle,
            "hero_video_url": self.hero_video_url
        }

class User(db.Model):
    """Admin User"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- New Models for Vendor System ---

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(20), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "pin_code": self.pin_code
        }

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default="Home") # Home, Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "type": self.type,
            "category_id": self.category_id,
            "is_active": self.is_active
        }

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    max_amount = db.Column(db.Float, nullable=True)
    min_cart_value = db.Column(db.Float, default=0.0)
    valid_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "discount_percentage": self.discount_percentage,
            "max_amount": self.max_amount,
            "min_cart_value": self.min_cart_value,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_active": self.is_active
        }

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(255), nullable=True)
    wallet_balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "mobile": self.mobile,
            "name": self.name,
            "email": self.email,
            "profile_pic": self.profile_pic,
            "wallet_balance": self.wallet_balance,
            "is_active": self.is_active
        }

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    shop_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(255), nullable=True)
    gst_number = db.Column(db.String(50), nullable=True)
    shop_logo = db.Column(db.String(255), nullable=True)
    min_order_qty = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=False) # Requires approval
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "mobile": self.mobile,
            "shop_name": self.shop_name,
            "owner_name": self.owner_name,
            "address": self.address,
            "gst_number": self.gst_number,
            "shop_logo": self.shop_logo,
            "min_order_qty": self.min_order_qty,
            "is_active": self.is_active,
            "area_id": self.area_id
        }

class DeliveryBoy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    vehicle_no = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False) # Requires approval
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "mobile": self.mobile,
            "name": self.name,
            "vehicle_no": self.vehicle_no,
            "is_active": self.is_active,
            "area_id": self.area_id
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "image_url": self.image_url}

class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    category = db.relationship('Category', backref=db.backref('sub_categories', lazy=True))

    def to_dict(self):
        return {"id": self.id, "category_id": self.category_id, "name": self.name, "image_url": self.image_url}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Relationships
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    sub_category_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'), nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)

    vendor = db.relationship('Vendor', backref=db.backref('products', lazy=True))
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    sub_category = db.relationship('SubCategory', backref=db.backref('products', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "old_price": self.old_price,
            "quantity": self.quantity,
            "image_url": self.image_url,
            "category_id": self.category_id,
            "sub_category_id": self.sub_category_id,
            "is_active": self.is_active
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    delivery_boy_id = db.Column(db.Integer, db.ForeignKey('delivery_boy.id'), nullable=True)
    
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default="Pending") # Pending, Accepted, Picked Up, Out for Delivery, Delivered, Cancelled
    payment_status = db.Column(db.String(50), default="Pending") # Pending, Paid
    payment_method = db.Column(db.String(50), default="COD")
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    vendor = db.relationship('Vendor', backref=db.backref('orders', lazy=True))
    delivery_boy = db.relationship('DeliveryBoy', backref=db.backref('orders', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "vendor_id": self.vendor_id,
            "delivery_boy_id": self.delivery_boy_id,
            "total_amount": self.total_amount,
            "discount_amount": self.discount_amount,
            "status": self.status,
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat()
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # Price at time of order

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "quantity": self.quantity,
            "price": self.price
        }

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    long = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "address_line": self.address_line,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "lat": self.lat,
            "long": self.long
        }

class WalletTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False) # Credit, Debit
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    customer = db.relationship('Customer', backref=db.backref('reviews', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer.name,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat()
        }

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "video_url": self.video_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

class StaticPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False) # e.g., 'privacy-policy'
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "slug": self.slug,
            "title": self.title,
            "content": self.content,
            "updated_at": self.updated_at.isoformat()
        }
