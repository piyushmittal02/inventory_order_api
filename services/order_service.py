from sqlalchemy.orm import selectinload
from extensions import db
from models.order import Order
from models.orderitem import OrderItem
from models.product import Product
from repositories.order_repository import find_order_by_id
from repositories.order_repository import find_orders
from repositories.order_repository import find_joined_order_rows
from repositories.order_repository import find_left_joined_order_rows
from repositories.order_repository import save_order_transaction
from repositories.product_repository import find_product_by_id
from repositories.order_repository import (
    commit_order_changes,
    rollback_order_changes
)

def calculate_total(products):
    total_amount = 0

    for product, quantity in products:
        total_amount += product.price * quantity

    return total_amount
  
def check_stock(products):
    for product, quantity in products:
        if quantity > product.stock:
            return {
                "product_id": product.id,
                "product_name": product.name,
                "requested": quantity,
                "available": product.stock
            }

    return None
  
def save_order(user_id, products, total_amount):
    try:
        return save_order_transaction(
            user_id, products, total_amount
        )

    except Exception:
        return None

def get_order_products(items):
    products = []

    for item in items:
        product_id = item["product_id"]
        product = find_product_by_id(product_id)
        
        if not product:
            return None, {
                "error": "Product not found",
                "product_id": product_id
            }

        products.append((product, item["quantity"]))

    return products, None

def change_order_status(order, user_id, role, new_status):

    allowed_statuses = [
        "pending",
        "confirmed",
        "completed",
        "cancelled"
    ]

    if new_status not in allowed_statuses:
        return "Invalid status", 400

    # Customer authorization
    if role == "customer":

        if order.user_id != user_id:
            return "You are not allowed to modify this order", 403

        if order.status != "pending":
            return "Only pending orders can be cancelled", 409

        if new_status != "cancelled":
            return "Customers can only cancel orders", 403

    # Admin authorization
    elif role == "admin":

        if order.status == "pending" and new_status != "confirmed":
            return "Pending order can only be confirmed", 409

        if order.status == "confirmed" and new_status != "completed":
            return "Confirmed order can only be completed", 409

        if order.status in ["completed", "cancelled"]:
            return "This order cannot be changed", 409

    else:
        return "Invalid user role", 403

    # Update status and restore stock if cancelled
    try:
        if new_status == "cancelled":
            for item in order.items:
                item.product.stock += item.quantity

        order.status = new_status

        commit_order_changes()

    except Exception:
        rollback_order_changes()
        return "Failed to update order", 500

    return None

def get_order_by_id(order_id):
    return find_order_by_id(order_id)

def list_orders(user_id, status_filter, sort_column,
                sort_order, page, per_page):

    return find_orders(
        user_id,
        status_filter,
        sort_column,
        sort_order,
        page,
        per_page
    )
def get_joined_order_rows(user_id):
    return find_joined_order_rows(user_id)
    
def get_left_joined_order_rows(user_id):
    return find_left_joined_order_rows(user_id)