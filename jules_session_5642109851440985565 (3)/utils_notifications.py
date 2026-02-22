import logging
import os

# Configure logging
logging.basicConfig(filename='notifications.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def notify_order_placed(customer, orders):
    message = f"SMS/Email to {customer.mobile}: Your order(s) {[o.id for o in orders]} have been placed successfully."
    logging.info(message)
    print(f"NOTIFICATION SENT: {message}")

def notify_status_update(order, status):
    message = f"SMS/Email to {order.customer.mobile}: Your order #{order.id} status has been updated to {status}."
    logging.info(message)
    print(f"NOTIFICATION SENT: {message}")
