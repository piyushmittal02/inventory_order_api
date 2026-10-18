from flask import request, jsonify, Blueprint
from sqlalchemy.orm import selectinload
from extensions import db
from models.product import Product
from models.order import Order
from models.orderitem import OrderItem
from routes.auth_routes import verify_token
from services.order_service import (
    calculate_total,
    check_stock,
    save_order,
    get_order_products,
    change_order_status,
    get_order_by_id,
    list_orders,
    get_joined_order_rows,
    get_left_joined_order_rows
)

def register_order_routes(app):
    order_bp = Blueprint("orders", __name__)
    
    @order_bp.post("/orders")
    def create_order():

        # JWT → User Identification
        payload, error, status = verify_token(app)

        if error:
            return error, status

        user_id = payload["user_id"]

        # Request Validation
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        if "items" not in data:
            return jsonify({
                "error": "Items are required"
            }), 400

        if not isinstance(data["items"], list):
            return jsonify({
                "error": "Items must be a list"
            }), 400

        if len(data["items"]) == 0:
            return jsonify({
                "error": "Order must contain at least one item"
            }), 400

        for item in data["items"]:

            if not isinstance(item, dict):
                return jsonify({
                    "error": "Each item must be an object"
                }), 400

            if "product_id" not in item:
                return jsonify({
                    "error": "Product ID is required"
                }), 400

            if not isinstance(item["product_id"], int):
                return jsonify({
                    "error": "Product ID must be an integer"
                }), 400

            if "quantity" not in item:
                return jsonify({
                    "error": "Quantity is required"
                }), 400

            if not isinstance(item["quantity"], int):
                return jsonify({
                    "error": "Quantity must be an integer"
                }), 400

            if item["quantity"] <= 0:
                return jsonify({
                    "error": "Quantity must be greater than 0"
                }), 400

        # Find Products
        products, product_error = get_order_products(data["items"])

        if product_error:
          return jsonify(product_error), 404

        # Check Stock
        stock_check = check_stock(products)
        if stock_check:
            return jsonify({
                "error": "Insufficient stock",
                **stock_check
            }), 409
           

        # Calculate Total
        total_amount = calculate_total(products)

        # Create Order + OrderItems + Reduce Inventory
        order = save_order(user_id, products, total_amount)

        if order is None:
         return jsonify({
        "error": "Failed to create order"
         }), 500

        return jsonify({
            "message": "Order created successfully",
            "order": {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_amount": order.total_amount
            }
        }), 201

    @order_bp.get("/orders")
    def get_orders():

        # JWT verification
        payload, error, status = verify_token(app)

        if error:
            return error, status

        user_id = payload["user_id"]

        # Read pagination parameters
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))

        except ValueError:
            return jsonify({
                "error": "Page and per_page must be integers"
            }), 400

        # Validate pagination
        if page < 1:
            return jsonify({
                "error": "Page must be at least 1"
            }), 400

        if per_page < 1 or per_page > 100:
            return jsonify({
                "error": "per_page must be between 1 and 100"
            }), 400

        # Read and validate status filter
        status_filter = request.args.get("status")

        if status_filter:
            allowed_statuses = [
                "pending",
                "confirmed",
                "completed",
                "cancelled"
            ]

            if status_filter not in allowed_statuses:
                return jsonify({
                    "error": "Invalid status filter"
                }), 400

        # Read and validate sorting parameters
        sort_by = request.args.get("sort_by", "id")
        sort_order = request.args.get(
            "sort_order", "desc"
        ).lower()

        allowed_sort_fields = {
            "id": Order.id,
            "total_amount": Order.total_amount,
            "status": Order.status
        }

        if sort_by not in allowed_sort_fields:
            return jsonify({
                "error": "Invalid sort field"
            }), 400

        if sort_order not in ["asc", "desc"]:
            return jsonify({
                "error": "sort_order must be asc or desc"
            }), 400

        sort_column = allowed_sort_fields[sort_by]

        # Fetch orders through the Service Layer
        total, orders = list_orders(
            user_id,
            status_filter,
            sort_column,
            sort_order,
            page,
            per_page
        )

        # Return response
        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": total,
            "orders": [
                {
                    "id": order.id,
                    "user_id": order.user_id,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "items": [
                        {
                            "product_id": item.product_id,
                            "quantity": item.quantity,
                            "price": item.price
                        }
                        for item in order.items
                    ]
                }
                for order in orders
            ]
        }), 200
    @order_bp.get("/orders/<int:order_id>")
    def get_order(order_id):
     
        payload, error, status = verify_token(app)

        if error:
            return error, status

        user_id = payload["user_id"]

        order = get_order_by_id(order_id)
        
        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        if order.user_id != user_id:
            return jsonify({
                "error": "You are not allowed to view this order"
            }), 403

        return jsonify({
            "order": {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_amount": order.total_amount,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in order.items
                ]
            }
        }), 200


    @order_bp.patch("/orders/<int:order_id>")
    def update_order_status(order_id):

        payload, error, status = verify_token(app)

        if error:
            return error, status

        user_id = payload["user_id"]
        role = payload["role"]

        order = get_order_by_id(order_id)

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        if "status" not in data:
            return jsonify({
                "error": "Status is required"
            }), 400

        new_status = data["status"]

        error = change_order_status(
         order, user_id, role, new_status
         )

        if error:
         message, status_code = error

         return jsonify({
        "error": message
          }), status_code

        return jsonify({
        "message": "Order status updated successfully",
        "order": {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount
         }
        }), 200   
             
    @order_bp.get("/orders/joined")
    def get_orders_joined():

     payload, error, status = verify_token(app)

     if error:
        return error, status

     user_id = payload["user_id"]

     rows = get_joined_order_rows(user_id)
     return jsonify({
        "items": [
            {
                "order_id": row.order_id,
                "total_amount": row.total_amount,
                "product_name": row.product_name,
                "quantity": row.quantity,
                "price": row.price
            }
            for row in rows
        ]
    }), 200
     
    @order_bp.get("/orders/left-joined")
    def get_orders_left_joined():

     payload, error, status = verify_token(app)

     if error:
        return error, status

     user_id = payload["user_id"]

     rows = get_left_joined_order_rows(user_id)

     return jsonify({
        "orders": [
            {
                "order_id": row.order_id,
                "total_amount": row.total_amount,
                "product_id": row.product_id,
                "product_name": row.product_name,
                "quantity": row.quantity,
                "price": row.price
            }
            for row in rows
        ]
    }), 200
    
    app.register_blueprint(order_bp)