from flask import Blueprint, request, jsonify, current_app, send_from_directory, g, send_file, Response
from models import db, SiteSettings, Product, Blog, User, Customer, Vendor, DeliveryBoy, Category, SubCategory, Order, OrderItem, Area, Banner, Address, Offer, Review, StaticPage
import os
import uuid
import json
import secrets
from functools import wraps
from utils import haversine, generate_invoice_pdf
from utils_notifications import notify_order_placed, notify_status_update
from datetime import datetime
import logging
import io
import csv
import zipfile

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Token storage: token -> {'id': user_id, 'role': 'role_name', 'username': username/mobile}
active_tokens = {}

# --- Auth Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                pass

        if not token or token not in active_tokens:
            return jsonify({'message': 'Token is missing or invalid!'}), 401

        token_data = active_tokens[token]
        # Make user info available to the route
        g.current_user = token_data
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.get('role') != 'admin':
             return jsonify({'message': 'Admin privilege required'}), 403
        return f(*args, **kwargs)
    return decorated

def vendor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.get('role') != 'vendor':
             return jsonify({'message': 'Vendor privilege required'}), 403
        return f(*args, **kwargs)
    return decorated

# --- Helper ---
def save_file(file):
    if not file:
        return None
    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    return f"/static/uploads/{filename}"

# --- Admin Dashboard ---
@api_bp.route('/admin/dashboard', methods=['GET'])
@token_required
@admin_required
def admin_dashboard():
    total_users = Customer.query.count()
    total_vendors = Vendor.query.count()
    total_delivery = DeliveryBoy.query.count()
    total_orders = Order.query.count()
    
    # Simple revenue calculation (sum of paid orders)
    paid_orders = Order.query.filter(Order.payment_status == 'Paid').all()
    total_revenue = sum(o.total_amount for o in paid_orders)
    
    return jsonify({
        "total_users": total_users,
        "total_vendors": total_vendors,
        "total_delivery_boys": total_delivery,
        "total_orders": total_orders,
        "total_revenue": total_revenue
    })

# --- Vendor Dashboard ---
@api_bp.route('/vendor/dashboard', methods=['GET'])
@token_required
@vendor_required
def vendor_dashboard():
    user = g.current_user
    vendor_id = user['id']
    
    orders = Order.query.filter_by(vendor_id=vendor_id).all()
    total_orders = len(orders)
    total_sales = sum(o.total_amount for o in orders if o.status == 'Delivered')
    total_customers = len(set(o.customer_id for o in orders))
    
    return jsonify({
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_customers": total_customers
    })

# --- Vendor Reports ---
@api_bp.route('/vendor/orders/export', methods=['GET'])
@token_required
@vendor_required
def export_vendor_orders():
    user = g.current_user
    vendor_id = user['id']
    orders = Order.query.filter_by(vendor_id=vendor_id).all()
    
    # Generate CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Order ID', 'Customer', 'Amount', 'Status', 'Date'])
    
    for order in orders:
        cw.writerow([
            order.id,
            order.customer.name,
            order.total_amount,
            order.status,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=orders.csv"}
    )

@api_bp.route('/vendor/transactions', methods=['GET'])
@token_required
@vendor_required
def get_vendor_transactions():
    user = g.current_user
    vendor_id = user['id']
    # Transactions = Orders that are paid or delivered
    orders = Order.query.filter_by(vendor_id=vendor_id).all()
    
    transactions = []
    for order in orders:
        transactions.append({
            'transaction_id': f"ORD-{order.id}",
            'date': order.created_at.isoformat(),
            'amount': order.total_amount,
            'status': order.payment_status,
            'customer': order.customer.name
        })
        
    return jsonify(transactions)

@api_bp.route('/vendor/invoices/bulk', methods=['GET'])
@token_required
@vendor_required
def bulk_download_invoices():
    user = g.current_user
    vendor_id = user['id']
    orders = Order.query.filter_by(vendor_id=vendor_id).all()
    
    # Create Zip
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for order in orders:
            pdf_buffer = generate_invoice_pdf(order)
            zf.writestr(f"invoice_{order.id}.pdf", pdf_buffer.read())
            
    memory_file.seek(0)
    return send_file(
        memory_file,
        as_attachment=True,
        download_name='bulk_invoices.zip',
        mimetype='application/zip'
    )

# --- Admin User Management ---
@api_bp.route('/admin/customers', methods=['GET'])
@token_required
@admin_required
def get_all_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@api_bp.route('/admin/customers/<int:id>/status', methods=['PUT'])
@token_required
@admin_required
def update_customer_status(id):
    customer = Customer.query.get_or_404(id)
    data = request.json
    
    if 'is_active' in data:
        customer.is_active = data['is_active']
        db.session.commit()
        return jsonify({"message": "Customer status updated", "user": customer.to_dict()})
        
    return jsonify({"message": "No changes"}), 400

@api_bp.route('/admin/users', methods=['POST'])
@token_required
@admin_required
def create_admin_user():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
        
    new_admin = User(username=data['username'])
    new_admin.set_password(data['password'])
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': 'Admin user created'}), 201

# --- Admin Vendor Management ---
@api_bp.route('/admin/vendors', methods=['GET'])
@token_required
@admin_required
def get_all_vendors():
    vendors = Vendor.query.all()
    return jsonify([v.to_dict() for v in vendors])

@api_bp.route('/admin/vendors/<int:id>/approve', methods=['PUT'])
@token_required
@admin_required
def approve_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    data = request.json
    
    if 'is_active' in data:
        vendor.is_active = data['is_active']
        db.session.commit()
        return jsonify({"message": "Vendor status updated", "vendor": vendor.to_dict()})
        
    return jsonify({"message": "No changes"}), 400

# --- Admin Delivery Boy Management ---
@api_bp.route('/admin/delivery_boys', methods=['GET'])
@token_required
@admin_required
def get_all_delivery_boys():
    boys = DeliveryBoy.query.all()
    return jsonify([b.to_dict() for b in boys])

@api_bp.route('/admin/delivery_boys/<int:id>/status', methods=['PUT'])
@token_required
@admin_required
def update_delivery_boy_status(id):
    boy = DeliveryBoy.query.get_or_404(id)
    data = request.json
    
    if 'is_active' in data:
        boy.is_active = data['is_active']
        db.session.commit()
        return jsonify({"message": "Delivery Boy status updated", "delivery_boy": boy.to_dict()})
        
    return jsonify({"message": "No changes"}), 400

# --- Admin Payment Management ---
@api_bp.route('/admin/payments', methods=['GET'])
@token_required
@admin_required
def get_payments():
    # Return basic payment info from orders
    orders = Order.query.all()
    payments = [{
        'order_id': o.id,
        'customer': o.customer.name,
        'amount': o.total_amount,
        'method': o.payment_method,
        'status': o.payment_status,
        'date': o.created_at.isoformat()
    } for o in orders]
    return jsonify(payments)

# --- Admin Notification Management ---
@api_bp.route('/admin/notifications', methods=['POST'])
@token_required
@admin_required
def send_notification():
    data = request.json
    message = data.get('message')
    recipient_group = data.get('group', 'all') # all, customers, vendors
    
    # Log notification
    logging.info(f"BROADCAST ({recipient_group}): {message}")
    
    return jsonify({"message": "Notification sent"}), 200

# --- Admin Review Management ---
@api_bp.route('/admin/reviews/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"})

# --- Static Pages ---
@api_bp.route('/pages/<slug>', methods=['GET'])
def get_page(slug):
    page = StaticPage.query.filter_by(slug=slug).first_or_404()
    return jsonify(page.to_dict())

@api_bp.route('/admin/pages', methods=['GET'])
@token_required
@admin_required
def get_all_pages():
    pages = StaticPage.query.all()
    return jsonify([p.to_dict() for p in pages])

@api_bp.route('/admin/pages/<slug>', methods=['PUT'])
@token_required
@admin_required
def update_page(slug):
    page = StaticPage.query.filter_by(slug=slug).first_or_404()
    data = request.json
    
    page.title = data.get('title', page.title)
    page.content = data.get('content', page.content)
    
    db.session.commit()
    return jsonify(page.to_dict())

# --- Admin Auth (Legacy Support) ---
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        token = secrets.token_hex(16)
        active_tokens[token] = {'id': user.id, 'role': 'admin', 'username': user.username}
        return jsonify({"message": "Login successful", "token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# --- Customer Auth ---
@api_bp.route('/customer/register', methods=['POST'])
def register_customer():
    data = request.json
    if Customer.query.filter_by(mobile=data.get('mobile')).first():
        return jsonify({'message': 'Mobile number already registered'}), 400
    
    new_customer = Customer(
        mobile=data['mobile'],
        name=data.get('name'),
        email=data.get('email')
    )
    new_customer.set_password(data['password'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer registered successfully'}), 201

@api_bp.route('/customer/login', methods=['POST'])
def login_customer():
    data = request.json
    customer = Customer.query.filter_by(mobile=data.get('mobile')).first()
    if customer and customer.check_password(data.get('password')):
        if not customer.is_active:
             return jsonify({"message": "Account is inactive"}), 403
        token = secrets.token_hex(16)
        active_tokens[token] = {'id': customer.id, 'role': 'customer', 'username': customer.mobile, 'wallet_balance': customer.wallet_balance}
        return jsonify({"message": "Login successful", "token": token, "user": customer.to_dict()}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@api_bp.route('/customer/profile', methods=['PUT'])
@token_required
def update_customer_profile():
    user = g.current_user
    if user['role'] != 'customer':
        return jsonify({'message': 'Unauthorized'}), 403
    
    customer = Customer.query.get(user['id'])
    data = request.json
    
    customer.name = data.get('name', customer.name)
    customer.email = data.get('email', customer.email)
    
    # Update password if provided
    if 'password' in data and data['password']:
        customer.set_password(data['password'])
        
    db.session.commit()
    return jsonify({"message": "Profile updated", "user": customer.to_dict()})

# --- Vendor Auth ---
@api_bp.route('/vendor/register', methods=['POST'])
def register_vendor():
    data = request.json
    if Vendor.query.filter_by(mobile=data.get('mobile')).first():
        return jsonify({'message': 'Mobile number already registered'}), 400
        
    new_vendor = Vendor(
        mobile=data['mobile'],
        shop_name=data['shop_name'],
        owner_name=data.get('owner_name'),
        address=data.get('address'),
        min_order_qty=data.get('min_order_qty', 1),
        is_active=True,
        area_id=data.get('area_id')
    )
    new_vendor.set_password(data['password'])
    db.session.add(new_vendor)
    db.session.commit()
    
    if 'lat' in data and 'long' in data:
        addr = Address(vendor_id=new_vendor.id, address_line=data.get('address', ''), lat=data['lat'], long=data['long'])
        db.session.add(addr)
        db.session.commit()

    return jsonify({'message': 'Vendor registered successfully'}), 201

@api_bp.route('/vendor/login', methods=['POST'])
def login_vendor():
    data = request.json
    vendor = Vendor.query.filter_by(mobile=data.get('mobile')).first()
    if vendor and vendor.check_password(data.get('password')):
        if not vendor.is_active:
             return jsonify({"message": "Account is not active"}), 403
        token = secrets.token_hex(16)
        active_tokens[token] = {'id': vendor.id, 'role': 'vendor', 'username': vendor.mobile}
        return jsonify({"message": "Login successful", "token": token, "user": vendor.to_dict()}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@api_bp.route('/vendor/profile', methods=['PUT'])
@token_required
@vendor_required
def update_vendor_profile():
    user = g.current_user
    vendor = Vendor.query.get(user['id'])
    data = request.json
    
    vendor.shop_name = data.get('shop_name', vendor.shop_name)
    vendor.address = data.get('address', vendor.address)
    vendor.min_order_qty = data.get('min_order_qty', vendor.min_order_qty)
    
    db.session.commit()
    return jsonify({"message": "Profile updated", "user": vendor.to_dict()})

# --- Delivery Boy Auth ---
@api_bp.route('/delivery/register', methods=['POST'])
def register_delivery():
    data = request.json
    if DeliveryBoy.query.filter_by(mobile=data.get('mobile')).first():
         return jsonify({'message': 'Mobile number already registered'}), 400
         
    new_boy = DeliveryBoy(
        mobile=data['mobile'],
        name=data['name'],
        vehicle_no=data.get('vehicle_no'),
        is_active=True,
        area_id=data.get('area_id')
    )
    new_boy.set_password(data['password'])
    db.session.add(new_boy)
    db.session.commit()
    return jsonify({'message': 'Delivery Boy registered successfully'}), 201

@api_bp.route('/delivery/login', methods=['POST'])
def login_delivery():
    data = request.json
    boy = DeliveryBoy.query.filter_by(mobile=data.get('mobile')).first()
    if boy and boy.check_password(data.get('password')):
        if not boy.is_active:
             return jsonify({"message": "Account is not active"}), 403
        token = secrets.token_hex(16)
        active_tokens[token] = {'id': boy.id, 'role': 'delivery', 'username': boy.mobile}
        return jsonify({"message": "Login successful", "token": token, "user": boy.to_dict()}), 200
    return jsonify({"message": "Invalid credentials"}), 401


# --- Settings ---
@api_bp.route('/settings', methods=['GET'])
def get_settings():
    settings = SiteSettings.query.first()
    return jsonify(settings.to_dict()) if settings else jsonify({})

@api_bp.route('/settings', methods=['PUT'])
@token_required
@admin_required
def update_settings():
    settings = SiteSettings.query.first()
    data = request.json
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)

    settings.brand_name = data.get('brand_name', settings.brand_name)
    settings.logo_url = data.get('logo_url', settings.logo_url)
    settings.seo_title = data.get('seo_title', settings.seo_title)
    settings.seo_meta_desc = data.get('seo_meta_desc', settings.seo_meta_desc)
    settings.hero_title = data.get('hero_title', settings.hero_title)
    settings.hero_subtitle = data.get('hero_subtitle', settings.hero_subtitle)
    settings.hero_video_url = data.get('hero_video_url', settings.hero_video_url)

    if 'navbar_links' in data:
        settings.navbar_links = json.dumps(data['navbar_links']) if isinstance(data['navbar_links'], list) else data['navbar_links']
    if 'footer_links' in data:
        settings.footer_links = json.dumps(data['footer_links']) if isinstance(data['footer_links'], list) else data['footer_links']

    db.session.commit()
    return jsonify({"message": "Settings updated", "settings": settings.to_dict()})

# --- Areas ---
@api_bp.route('/areas', methods=['GET'])
def get_areas():
    areas = Area.query.all()
    return jsonify([a.to_dict() for a in areas])

@api_bp.route('/areas', methods=['POST'])
@token_required
@admin_required
def add_area():
    data = request.json
    new_area = Area(
        name=data['name'],
        city=data['city'],
        pin_code=data.get('pin_code')
    )
    db.session.add(new_area)
    db.session.commit()
    return jsonify(new_area.to_dict()), 201

@api_bp.route('/areas/<int:id>', methods=['PUT'])
@token_required
@admin_required
def update_area(id):
    area = Area.query.get_or_404(id)
    data = request.json
    area.name = data.get('name', area.name)
    area.city = data.get('city', area.city)
    area.pin_code = data.get('pin_code', area.pin_code)
    db.session.commit()
    return jsonify(area.to_dict())

@api_bp.route('/areas/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_area(id):
    area = Area.query.get_or_404(id)
    db.session.delete(area)
    db.session.commit()
    return jsonify({"message": "Area deleted"})

# --- Banners ---
@api_bp.route('/banners', methods=['GET'])
def get_banners():
    type_filter = request.args.get('type')
    if type_filter:
        banners = Banner.query.filter_by(type=type_filter, is_active=True).all()
    else:
        banners = Banner.query.filter_by(is_active=True).all()
    return jsonify([b.to_dict() for b in banners])

@api_bp.route('/banners', methods=['POST'])
@token_required
@admin_required
def add_banner():
    data = request.json
    new_banner = Banner(
        image_url=data['image_url'],
        type=data.get('type', 'Home'),
        category_id=data.get('category_id'),
        is_active=data.get('is_active', True)
    )
    db.session.add(new_banner)
    db.session.commit()
    return jsonify(new_banner.to_dict()), 201

@api_bp.route('/banners/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    db.session.delete(banner)
    db.session.commit()
    return jsonify({"message": "Banner deleted"})

# --- Offers ---
@api_bp.route('/offers', methods=['GET'])
def get_offers():
    offers = Offer.query.filter_by(is_active=True).all()
    return jsonify([o.to_dict() for o in offers])

@api_bp.route('/offers', methods=['POST'])
@token_required
@admin_required
def add_offer():
    data = request.json
    valid_until = None
    if 'valid_until' in data:
        try:
            valid_until = datetime.fromisoformat(data['valid_until'])
        except ValueError:
            pass
            
    new_offer = Offer(
        code=data['code'],
        discount_percentage=data['discount_percentage'],
        max_amount=data.get('max_amount'),
        min_cart_value=data.get('min_cart_value', 0.0),
        valid_until=valid_until,
        is_active=data.get('is_active', True)
    )
    db.session.add(new_offer)
    db.session.commit()
    return jsonify(new_offer.to_dict()), 201

@api_bp.route('/offers/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_offer(id):
    offer = Offer.query.get_or_404(id)
    db.session.delete(offer)
    db.session.commit()
    return jsonify({"message": "Offer deleted"})

# --- Categories ---
@api_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])

@api_bp.route('/categories/<int:id>/subcategories', methods=['GET'])
def get_subcategories(id):
    subcategories = SubCategory.query.filter_by(category_id=id).all()
    return jsonify([s.to_dict() for s in subcategories])

# --- Products ---
@api_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in products])

@api_bp.route('/products/nearby', methods=['GET'])
def get_nearby_products():
    try:
        lat = float(request.args.get('lat'))
        long = float(request.args.get('long'))
        radius = float(request.args.get('radius', 10.0)) # km
    except (TypeError, ValueError):
        return jsonify({'message': 'Invalid latitude or longitude'}), 400

    nearby_products = []
    
    # Inefficient for large datasets, but works for MVP/SQLite
    # Iterate over all vendors with addresses
    vendors = Vendor.query.filter_by(is_active=True).all()
    
    nearby_vendor_ids = []
    for vendor in vendors:
        # Assuming one address per vendor for simplicity, or fetching from Address table
        v_addr = Address.query.filter_by(vendor_id=vendor.id).first()
        if v_addr and v_addr.lat is not None and v_addr.long is not None:
             dist = haversine(lat, long, v_addr.lat, v_addr.long)
             if dist <= radius:
                 nearby_vendor_ids.append(vendor.id)
    
    if nearby_vendor_ids:
        products = Product.query.filter(Product.vendor_id.in_(nearby_vendor_ids), Product.is_active == True).all()
        nearby_products = [p.to_dict() for p in products]
        
    return jsonify(nearby_products)

@api_bp.route('/vendor/products', methods=['GET'])
@token_required
@vendor_required
def get_vendor_products():
    user = g.current_user
    products = Product.query.filter_by(vendor_id=user['id']).all()
    return jsonify([p.to_dict() for p in products])

@api_bp.route('/admin/products', methods=['GET'])
@token_required
@admin_required
def get_all_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@api_bp.route('/products', methods=['POST'])
@token_required
def add_product():
    user = g.current_user
    data = request.json
    
    vendor_id = None
    if user['role'] == 'vendor':
        vendor_id = user['id']
    elif user['role'] == 'admin':
        if 'vendor_id' in data:
            vendor_id = data['vendor_id']
    else:
        return jsonify({'message': 'Unauthorized'}), 403
    
    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        image_url=data.get('image_url'),
        category_id=data.get('category_id'), 
        sub_category_id=data.get('sub_category_id'),
        vendor_id=vendor_id,
        is_active=data.get('is_active', True),
        quantity=data.get('quantity', 0)
    )
    
    # Handle legacy category string
    if 'category' in data and isinstance(data['category'], str) and not new_product.category_id:
         # Try to find category by name
         cat = Category.query.filter_by(name=data['category']).first()
         if cat:
             new_product.category_id = cat.id

    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

@api_bp.route('/products/<int:id>', methods=['PUT'])
@token_required
def update_product(id):
    product = Product.query.get_or_404(id)
    user = g.current_user
    
    if user['role'] == 'vendor':
        if product.vendor_id != user['id']:
            return jsonify({'message': 'Unauthorized'}), 403
    elif user['role'] == 'admin':
        pass
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.image_url = data.get('image_url', product.image_url)
    product.category_id = data.get('category_id', product.category_id)
    product.sub_category_id = data.get('sub_category_id', product.sub_category_id)
    product.is_active = data.get('is_active', product.is_active)
    product.quantity = data.get('quantity', product.quantity)
    
    db.session.commit()
    return jsonify(product.to_dict())

@api_bp.route('/products/<int:id>', methods=['DELETE'])
@token_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    user = g.current_user
    
    if user['role'] == 'vendor':
        if product.vendor_id != user['id']:
            return jsonify({'message': 'Unauthorized'}), 403
    elif user['role'] == 'admin':
        pass
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

@api_bp.route('/products/<int:id>/reviews', methods=['POST'])
@token_required
def add_review(id):
    user = g.current_user
    if user['role'] != 'customer':
        return jsonify({'message': 'Only customers can review'}), 403
        
    product = Product.query.get_or_404(id)
    
    # Check if customer has delivered order for this product
    has_ordered = False
    customer_orders = Order.query.filter_by(customer_id=user['id'], status="Delivered").all()
    for order in customer_orders:
        for item in order.items:
            if item.product_id == id:
                has_ordered = True
                break
        if has_ordered:
            break
            
    if not has_ordered:
        return jsonify({'message': 'You must purchase and receive this product to review it'}), 403
        
    data = request.json
    review = Review(
        customer_id=user['id'],
        product_id=id,
        vendor_id=product.vendor_id,
        rating=data['rating'],
        comment=data.get('comment')
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201

@api_bp.route('/products/<int:id>/reviews', methods=['GET'])
def get_product_reviews(id):
    reviews = Review.query.filter_by(product_id=id).all()
    return jsonify([r.to_dict() for r in reviews])

# --- Orders ---
@api_bp.route('/orders', methods=['POST'])
@token_required
def place_order():
    user = g.current_user
    if user['role'] != 'customer':
        return jsonify({'message': 'Only customers can place orders'}), 403
    
    data = request.json
    items = data.get('items', []) 
    payment_method = data.get('payment_method', 'COD')
    coupon_code = data.get('coupon_code')
    
    if not items:
        return jsonify({'message': 'No items in order'}), 400
        
    vendor_items = {}
    total_amount_by_vendor = {}
    
    # Validate stock and group by vendor
    for item in items:
        product = Product.query.get(item['product_id'])
        if not product or not product.is_active:
             return jsonify({'message': f'Product {item["product_id"]} unavailable'}), 400
        if product.quantity < item['quantity']:
             return jsonify({'message': f'Insufficient stock for {product.name}'}), 400
             
        v_id = product.vendor_id
        if v_id not in vendor_items:
            vendor_items[v_id] = []
            total_amount_by_vendor[v_id] = 0.0
            
        vendor_items[v_id].append({
            'product': product,
            'quantity': item['quantity'],
            'price': product.price
        })
        total_amount_by_vendor[v_id] += product.price * item['quantity']

    customer = Customer.query.get(user['id'])
    total_all = sum(total_amount_by_vendor.values())
    
    # Apply Offer
    discount_amount = 0.0
    if coupon_code:
        offer = Offer.query.filter_by(code=coupon_code, is_active=True).first()
        if not offer:
            return jsonify({'message': 'Invalid coupon code'}), 400
        if offer.valid_until and offer.valid_until < datetime.now():
            return jsonify({'message': 'Coupon expired'}), 400
        if total_all < offer.min_cart_value:
            return jsonify({'message': f'Minimum cart value of {offer.min_cart_value} required'}), 400
            
        discount = (total_all * offer.discount_percentage) / 100
        if offer.max_amount:
            discount = min(discount, offer.max_amount)
        discount_amount = discount
        
    final_total = total_all - discount_amount
    
    if payment_method == 'Wallet':
        if customer.wallet_balance < final_total:
             return jsonify({'message': 'Insufficient wallet balance'}), 400
        customer.wallet_balance -= final_total
        
    created_orders = []
    
    for v_id, v_items in vendor_items.items():
        v_total = total_amount_by_vendor[v_id]
        ratio = v_total / total_all if total_all > 0 else 0
        v_discount = discount_amount * ratio
        v_final_amount = v_total - v_discount
        
        new_order = Order(
            customer_id=customer.id,
            vendor_id=v_id,
            total_amount=v_final_amount,
            discount_amount=v_discount,
            status="Pending",
            payment_status="Paid" if payment_method == 'Wallet' else "Pending",
            payment_method=payment_method
        )
        db.session.add(new_order)
        db.session.flush() 
        
        for item in v_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
            item['product'].quantity -= item['quantity']
            
        created_orders.append(new_order)
        
    db.session.commit()
    
    # Notify (Simulated)
    notify_order_placed(customer, created_orders)
    
    return jsonify({'message': 'Order placed successfully', 'order_ids': [o.id for o in created_orders]}), 201

# --- Vendor Create Order (On behalf of Customer) ---
@api_bp.route('/vendor/orders', methods=['POST'])
@token_required
@vendor_required
def vendor_create_order():
    user = g.current_user
    vendor_id = user['id']
    data = request.json
    
    mobile = data.get('customer_mobile')
    items = data.get('items', [])
    
    if not mobile or not items:
        return jsonify({'message': 'Customer mobile and items are required'}), 400
        
    customer = Customer.query.filter_by(mobile=mobile).first()
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
        
    total_amount = 0.0
    order_items_data = []
    
    for item in items:
        product = Product.query.get(item['product_id'])
        if not product or product.vendor_id != vendor_id:
             return jsonify({'message': f'Invalid product {item["product_id"]}'}), 400
        if product.quantity < item['quantity']:
             return jsonify({'message': f'Insufficient stock for {product.name}'}), 400
             
        total_amount += product.price * item['quantity']
        order_items_data.append({'product': product, 'quantity': item['quantity'], 'price': product.price})
        
    new_order = Order(
        customer_id=customer.id,
        vendor_id=vendor_id,
        total_amount=total_amount,
        status="Pending",
        payment_status="Pending", # Assuming COD or Manual Pay for vendor created order
        payment_method="Vendor Created"
    )
    db.session.add(new_order)
    db.session.flush()
    
    for item in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item['product'].id,
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
        item['product'].quantity -= item['quantity']
        
    db.session.commit()
    notify_order_placed(customer, [new_order])
    
    return jsonify({'message': 'Order created successfully', 'order_id': new_order.id}), 201

@api_bp.route('/customer/orders', methods=['GET'])
@token_required
def get_customer_orders():
    user = g.current_user
    if user['role'] != 'customer':
         return jsonify({'message': 'Unauthorized'}), 403
    orders = Order.query.filter_by(customer_id=user['id']).all()
    return jsonify([o.to_dict() for o in orders])

@api_bp.route('/orders/<int:id>/invoice', methods=['GET'])
@token_required
def get_invoice(id):
    user = g.current_user
    order = Order.query.get_or_404(id)
    
    # Check permission
    if user['role'] == 'customer' and order.customer_id != user['id']:
        return jsonify({'message': 'Unauthorized'}), 403
    if user['role'] == 'vendor' and order.vendor_id != user['id']:
        return jsonify({'message': 'Unauthorized'}), 403
    if user['role'] == 'admin':
        pass
    
    pdf_buffer = generate_invoice_pdf(order)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'invoice_{order.id}.pdf',
        mimetype='application/pdf'
    )

# --- Order Management ---
@api_bp.route('/vendor/orders', methods=['GET'])
@token_required
@vendor_required
def get_vendor_orders():
    user = g.current_user
    orders = Order.query.filter_by(vendor_id=user['id']).all()
    return jsonify([o.to_dict() for o in orders])

@api_bp.route('/delivery/orders', methods=['GET'])
@token_required
def get_delivery_orders():
    user = g.current_user
    if user['role'] != 'delivery':
         return jsonify({'message': 'Unauthorized'}), 403
    orders = Order.query.filter_by(delivery_boy_id=user['id']).all()
    return jsonify([o.to_dict() for o in orders])

@api_bp.route('/admin/orders', methods=['GET'])
@token_required
@admin_required
def get_all_orders():
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders])

@api_bp.route('/orders/<int:id>/status', methods=['PUT'])
@token_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    user = g.current_user
    data = request.json
    new_status = data.get('status')
    
    # Validation logic based on role
    if user['role'] == 'vendor':
        if order.vendor_id != user['id']:
            return jsonify({'message': 'Unauthorized'}), 403
        if new_status not in ['Accepted', 'Rejected', 'Ready', 'Completed']: # Example statuses
             return jsonify({'message': 'Invalid status'}), 400
             
    elif user['role'] == 'delivery':
        if order.delivery_boy_id != user['id']:
            return jsonify({'message': 'Unauthorized'}), 403
        if new_status not in ['Picked Up', 'Out for Delivery', 'Delivered']:
             return jsonify({'message': 'Invalid status'}), 400

    elif user['role'] == 'customer':
         if order.customer_id != user['id']:
             return jsonify({'message': 'Unauthorized'}), 403
         if new_status == 'Cancelled' and order.status == 'Pending':
             pass
         else:
             return jsonify({'message': 'Cannot update status'}), 403
    
    elif user['role'] == 'admin':
        pass # Admin can set any status
        
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    order.status = new_status
    db.session.commit()
    
    # Notify (Simulated)
    notify_status_update(order, new_status)
    
    return jsonify({'message': 'Status updated', 'order': order.to_dict()})

@api_bp.route('/orders/<int:id>/assign', methods=['PUT'])
@token_required
def assign_order(id):
    order = Order.query.get_or_404(id)
    user = g.current_user
    
    if user['role'] not in ['admin', 'vendor']:
         return jsonify({'message': 'Unauthorized'}), 403
         
    if user['role'] == 'vendor' and order.vendor_id != user['id']:
         return jsonify({'message': 'Unauthorized'}), 403

    data = request.json
    delivery_boy_id = data.get('delivery_boy_id')
    
    boy = DeliveryBoy.query.get(delivery_boy_id)
    if not boy:
         return jsonify({'message': 'Delivery Boy not found'}), 404
         
    order.delivery_boy_id = delivery_boy_id
    db.session.commit()
    return jsonify({'message': 'Order assigned', 'order': order.to_dict()})

# --- Blogs ---
@api_bp.route('/blogs', methods=['GET'])
def get_blogs():
    blogs = Blog.query.filter_by(is_active=True).all()
    return jsonify([b.to_dict() for b in blogs])

@api_bp.route('/admin/blogs', methods=['GET'])
@token_required
@admin_required
def get_all_blogs():
    blogs = Blog.query.all()
    return jsonify([b.to_dict() for b in blogs])

@api_bp.route('/blogs', methods=['POST'])
@token_required
@admin_required
def add_blog():
    data = request.json
    new_blog = Blog(
        title=data['title'],
        content=data['content'],
        image_url=data.get('image_url'),
        video_url=data.get('video_url'),
        is_active=data.get('is_active', True)
    )
    db.session.add(new_blog)
    db.session.commit()
    return jsonify(new_blog.to_dict()), 201

@api_bp.route('/blogs/<int:id>', methods=['PUT'])
@token_required
@admin_required
def update_blog(id):
    blog = Blog.query.get_or_404(id)
    data = request.json
    blog.title = data.get('title', blog.title)
    blog.content = data.get('content', blog.content)
    blog.image_url = data.get('image_url', blog.image_url)
    blog.video_url = data.get('video_url', blog.video_url)
    blog.is_active = data.get('is_active', blog.is_active)
    db.session.commit()
    return jsonify(blog.to_dict())

@api_bp.route('/blogs/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()
    return jsonify({"message": "Blog deleted"})

# --- Upload ---
@api_bp.route('/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file:
        file_url = save_file(file)
        return jsonify({"url": file_url})
    return jsonify({"message": "Upload failed"}), 500

# --- Frontend Routes (Serve Static Files) ---
@api_bp.route('/', defaults={'path': ''})
@api_bp.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(current_app.static_folder + '/' + path):
        return send_from_directory(current_app.static_folder, path)
    else:
        pass
@api_bp.route('/customer/wallet', methods=['POST'])
@token_required
def add_money():
    user = g.current_user
    if user['role'] != 'customer':
        return jsonify({'message': 'Unauthorized'}), 403
    
    amount = request.json.get('amount')
    if not amount or amount <= 0:
        return jsonify({'message': 'Invalid amount'}), 400
        
    customer = Customer.query.get(user['id'])
    customer.wallet_balance += amount
    
    # Log transaction
    trans = WalletTransaction(
        customer_id=customer.id,
        amount=amount,
        type="Credit",
        description="Added money to wallet"
    )
    db.session.add(trans)
    db.session.commit()
    
    return jsonify({'message': 'Money added', 'balance': customer.wallet_balance})
