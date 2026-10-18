from extensions import db
from models.product import Product
from repositories.product_repository import save_product
from repositories.product_repository import find_all_products
from repositories.product_repository import find_product_by_id
from repositories.product_repository import save_product_changes
from repositories.product_repository import remove_product
from repositories.product_repository import product_has_order_items

def create_products(name, price, stock):
    product = Product(
        name=name,
        price=price,
        stock=stock
    )

    return save_product(product)
      
def get_all_products():
    return find_all_products()

def get_product_by_id(product_id):
    return find_product_by_id(product_id)

def update_product(product, data):
    for field in ("name", "price", "stock"):
        if field in data:
            setattr(product, field, data[field])

    return save_product_changes(product)
      
def delete_product(product):
    if product_has_order_items(product.id):
        return False

    remove_product(product)
    return True