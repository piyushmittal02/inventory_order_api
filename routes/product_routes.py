from flask import request, jsonify
from flask import Blueprint
from services.product_service import create_products, get_all_products,get_product_by_id,delete_product
from services.product_service import update_product as update_product_service
from services.product_service import delete_product as delete_product_service
from routes.auth_routes import verify_token

def register_product_routes(app, db, Product):
    product_bp = Blueprint("products", __name__)
    @product_bp.post("/products")
    def create_product():
                # Verify JWT
        payload, error, status = verify_token(app)

        if error:
            return error, status

        # Only admins can create products
        if payload.get("role") != "admin":
            return jsonify({
                "error": "Only admins can create products"
            }), 403
        
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        if "name" not in data:
            return jsonify({
                "error": "Name is required"
            }), 400

        if not isinstance(data["name"], str):
            return jsonify({
                "error": "Name must be a string"
            }), 400

        if not data["name"].strip():
            return jsonify({
                "error": "Name cannot be empty"
            }), 400

        if "price" not in data:
            return jsonify({
                "error": "Price is required"
            }), 400

        if not isinstance(data["price"], (int, float)):
            return jsonify({
                "error": "Price must be a number"
            }), 400

        if data["price"] <= 0:
            return jsonify({
                "error": "Price must be greater than 0"
            }), 400

        if "stock" not in data:
            return jsonify({
                "error": "Stock is required"
            }), 400

        if not isinstance(data["stock"], int):
            return jsonify({
                "error": "Stock must be an integer"
            }), 400

        if data["stock"] < 0:
            return jsonify({
                "error": "Stock cannot be negative"
            }), 400

        try:
          product = create_products(
          data["name"],
          data["price"],
          data["stock"]
          )
        except Exception:
         return jsonify({
        "error": "Failed to create product"
        }), 500

        return jsonify({
            "message": "Product created successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock
            }
        }), 201

    @product_bp.get("/products")
    def get_products():
        products = get_all_products()

        return jsonify({
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "stock": product.stock
                }
                for product in products
            ]
        }), 200

    @product_bp.get("/products/<int:product_id>")
    def get_product(product_id):
        product = get_product_by_id(product_id)
        
        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        return jsonify({
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock
            }
        }), 200

    @product_bp.patch("/products/<int:product_id>")
    def update_product(product_id):
        payload, error, status = verify_token(app)

        if error:
            return error, status

        if payload.get("role") != "admin":
            return jsonify({
                "error": "Only admins can modify products"
            }), 403
        
        product = get_product_by_id(product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        if "name" in data:
            if not isinstance(data["name"], str):
                return jsonify({
                    "error": "Name must be a string"
                }), 400

            product.name = data["name"].strip()

        if "price" in data:
            if not isinstance(data["price"], (int, float)):
                return jsonify({
                    "error": "Price must be a number"
                }), 400

            product.price = data["price"]

        if "stock" in data:
            if not isinstance(data["stock"], int):
                return jsonify({
                    "error": "Stock must be an integer"
                }), 400

            product.stock = data["stock"]

        try:
          product = update_product_service(product,data)

        except Exception:
            import traceback
            traceback.print_exc()

            return jsonify({
                "error": "Failed to update product"
            }), 500
        
        return jsonify({
         "message": "Product updated successfully",
         "product": {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
          }}), 200

    @product_bp.delete("/products/<int:product_id>")
    def delete_products(product_id):
        payload, error, status = verify_token(app)

        if error:
            return error, status

        if payload.get("role") != "admin":
            return jsonify({
                "error": "Only admins can delete products"
            }), 403
        
        
        product = get_product_by_id(product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        try:
         deleted = delete_product_service(product)
    
        except Exception:
         return jsonify({
         "error": "Failed to delete product"
          }), 500
        
        if not deleted:
          return jsonify({
           "error": "Cannot delete a product referenced by existing orders"
           }), 409

        return jsonify({
            "message": "Product deleted successfully"
        }), 200
    
    app.register_blueprint(product_bp)