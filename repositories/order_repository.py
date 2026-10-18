from extensions import db
from models.order import Order
from sqlalchemy.orm import selectinload
from models.product import Product
from models.orderitem import OrderItem

def find_order_by_id(order_id):
    return db.session.get(Order, order_id)
  
def find_orders(user_id, status_filter, sort_column,
                sort_order, page, per_page):

    query = Order.query.filter_by(user_id=user_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    total = query.count()

    sort_expression = (
        sort_column.desc()
        if sort_order == "desc"
        else sort_column.asc()
    )

    orders = (
        query
        .options(selectinload(Order.items))
        .order_by(sort_expression, Order.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return total, orders
  
def find_joined_order_rows(user_id):
    return (
        db.session.query(
            Order.id.label("order_id"),
            Order.total_amount,
            Product.name.label("product_name"),
            OrderItem.quantity,
            OrderItem.price
        )
        .join(OrderItem, Order.id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(Order.user_id == user_id)
        .all()
    )

def find_left_joined_order_rows(user_id):
    return (
        db.session.query(
            Order.id.label("order_id"),
            Order.total_amount,
            OrderItem.product_id,
            Product.name.label("product_name"),
            OrderItem.quantity,
            OrderItem.price
        )
        .outerjoin(OrderItem, Order.id == OrderItem.order_id)
        .outerjoin(Product, OrderItem.product_id == Product.id)
        .filter(Order.user_id == user_id)
        .all()
    )
    
def save_order_transaction(user_id, products, total_amount):
    try:
        order = Order(
            user_id=user_id,
            total_amount=total_amount
        )

        db.session.add(order)

        for product, quantity in products:
            order_item = OrderItem(
                order=order,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )
            db.session.add(order_item)

        for product, quantity in products:
            product.stock -= quantity

        db.session.commit()
        return order

    except Exception:
        db.session.rollback()
        raise
      
def commit_order_changes():
    db.session.commit()


def rollback_order_changes():
    db.session.rollback()