import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Invoice for Order #{order.id}")
    
    # Details
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 705, f"Vendor: {order.vendor.shop_name}")
    p.drawString(100, 690, f"Customer: {order.customer.name}")
    p.drawString(100, 675, f"Payment Method: {order.payment_method}")
    p.drawString(100, 660, f"Status: {order.status}")

    # Items
    y = 630
    p.drawString(100, y, "Items:")
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(120, y, "Product")
    p.drawString(300, y, "Qty")
    p.drawString(400, y, "Price")
    p.drawString(500, y, "Total")
    
    y -= 20
    p.setFont("Helvetica", 10)
    
    for item in order.items:
        p.drawString(120, y, item.product.name[:30])
        p.drawString(300, y, str(item.quantity))
        p.drawString(400, y, f"${item.price:.2f}")
        p.drawString(500, y, f"${item.price * item.quantity:.2f}")
        y -= 15

    # Total
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y, "Grand Total:")
    p.drawString(500, y, f"${order.total_amount:.2f}")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
