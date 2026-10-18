from extensions import db
from models.product import Product
from models.orderitem import OrderItem

def save_product(product):
    try:
        db.session.add(product)
        db.session.commit()
        return product

    except Exception:
        db.session.rollback()
        raise

def find_all_products():
    return Product.query.all()

def find_product_by_id(product_id):
    return db.session.get(Product, product_id)
  
def save_product_changes(product):
    try:
        db.session.commit()
        return product

    except Exception:
        db.session.rollback()
        raise
      
def remove_product(product):
    try:
        db.session.delete(product)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise


def product_has_order_items(product_id):
    return (
        db.session.query(OrderItem.id)
        .filter_by(product_id=product_id)
        .first()
        is not None
    )