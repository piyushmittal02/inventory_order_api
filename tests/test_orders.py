from extensions import db
from models.product import Product
from decimal import Decimal

def test_create_order_without_token_returns_401(client):
    response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 401
  
def test_create_order_with_invalid_token_returns_401(client):
    response = client.post(
        "/orders",
        headers={
            "Authorization": "Bearer invalid_token"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 401
    
def test_get_orders_without_token_returns_401(client):
    response = client.get("/orders")

    assert response.status_code == 401
    
def test_get_orders_with_invalid_token_returns_401(client):
    response = client.get(
        "/orders",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401
    
def test_get_order_by_id_without_token_returns_401(client):
    response = client.get("/orders/1")

    assert response.status_code == 401
    
def test_create_order_with_valid_customer_token_returns_201(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_order_customer",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_order_customer",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]

    # Create an order containing the test product
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                }
            ]
        }
    )

    assert response.status_code == 201
    
    # Verify that product stock decreased
    product_response = client.get("/products/1")

    assert product_response.status_code == 200

    product_data = product_response.get_json()

    assert product_data["product"]["stock"] == 8
    
def test_get_orders_with_valid_customer_token_returns_200(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_get_orders_user",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_get_orders_user",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]

    # Create an order
    order_response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Retrieve the customer's orders
    response = client.get(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "orders" in data
    assert isinstance(data["orders"], list)
    assert len(data["orders"]) == 1
    assert data["orders"][0]["items"][0]["product_id"] == 1
    
    
def test_customer_cannot_view_another_customers_order(client):
    # Register Customer A
    client.post(
        "/register",
        json={
            "username": "pytest_owner_a",
            "password": "TestPassword123!"
        }
    )

    # Log in as Customer A
    login_a = client.post(
        "/login",
        json={
            "username": "pytest_owner_a",
            "password": "TestPassword123!"
        }
    )

    token_a = login_a.get_json()["token"]

    # Customer A creates an order
    order_response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Retrieve Customer A's order ID
    orders_response = client.get(
        "/orders",
        headers={
            "Authorization": f"Bearer {token_a}"
        }
    )

    assert orders_response.status_code == 200

    orders = orders_response.get_json()["orders"]
    order_id = orders[0]["id"]

    # Register Customer B
    client.post(
        "/register",
        json={
            "username": "pytest_owner_b",
            "password": "TestPassword123!"
        }
    )

    # Log in as Customer B
    login_b = client.post(
        "/login",
        json={
            "username": "pytest_owner_b",
            "password": "TestPassword123!"
        }
    )

    token_b = login_b.get_json()["token"]

    # Customer B attempts to view Customer A's order
    response = client.get(
        f"/orders/{order_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        }
    )

    assert response.status_code == 403
    
def test_customer_cannot_modify_another_customers_order(client):
    # Register Customer A
    client.post(
        "/register",
        json={
            "username": "pytest_modify_owner_a",
            "password": "TestPassword123!"
        }
    )

    # Log in as Customer A
    login_a = client.post(
        "/login",
        json={
            "username": "pytest_modify_owner_a",
            "password": "TestPassword123!"
        }
    )

    assert login_a.status_code == 200
    token_a = login_a.get_json()["token"]

    # Customer A creates an order
    order_response = client.post(
        "/orders",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Find Customer A's order ID
    orders_response = client.get(
        "/orders",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    assert orders_response.status_code == 200

    order_id = orders_response.get_json()["orders"][0]["id"]

    # Register Customer B
    client.post(
        "/register",
        json={
            "username": "pytest_modify_owner_b",
            "password": "TestPassword123!"
        }
    )

    # Log in as Customer B
    login_b = client.post(
        "/login",
        json={
            "username": "pytest_modify_owner_b",
            "password": "TestPassword123!"
        }
    )

    assert login_b.status_code == 200
    token_b = login_b.get_json()["token"]

    # Customer B attempts to cancel Customer A's order
    response = client.patch(
        f"/orders/{order_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"status": "cancelled"}
    )

    assert response.status_code == 403
    
def test_cancelling_order_restores_product_stock(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_cancel_order_user",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_cancel_order_user",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Initial stock should be 10
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 10

    # Create an order for 2 units
    order_response = client.post(
        "/orders",
        headers=headers,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Stock should decrease from 10 to 8
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 8

    # Find the customer's order ID
    orders_response = client.get("/orders", headers=headers)
    assert orders_response.status_code == 200

    order_id = orders_response.get_json()["orders"][0]["id"]

    # Cancel the order
    cancel_response = client.patch(
        f"/orders/{order_id}",
        headers=headers,
        json={"status": "cancelled"}
    )

    assert cancel_response.status_code == 200

    # Stock should be restored from 8 to 10
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_with_zero_quantity_returns_400(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_zero_quantity",
            "password": "TestPassword123!"
        }
    )

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_zero_quantity",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try creating an order with zero quantity
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 0
                }
            ]
        }
    )

    assert response.status_code == 400
    
def test_create_order_with_negative_quantity_returns_400(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_negative_quantity",
            "password": "TestPassword123!"
        }
    )

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_negative_quantity",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try creating an order with a negative quantity
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": -2
                }
            ]
        }
    )

    assert response.status_code == 400

    # Stock must remain unchanged
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_with_nonexistent_product_returns_404(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_missing_product",
            "password": "TestPassword123!"
        }
    )

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_missing_product",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try ordering a product that does not exist
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 404

    # The valid test product's stock must remain unchanged
    product_response = client.get("/products/1")

    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_with_insufficient_stock_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_insufficient_stock",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_insufficient_stock",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # The test product starts with stock = 10.
    # Request 11 units, which exceeds available stock.
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 11
                }
            ]
        }
    )

    assert response.status_code == 409

    # Verify that stock remains unchanged
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_with_empty_items_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_empty_order",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_empty_order",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try creating an order without any items
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": []
        }
    )

    assert response.status_code == 400

    # Stock must remain unchanged
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_without_items_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_missing_items",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_missing_items",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try creating an order without the items field
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={}
    )

    assert response.status_code == 400

    # Verify that product stock remains unchanged
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_item_without_product_id_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_missing_product_id",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_missing_product_id",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try creating an order item without product_id
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 400

    # Product stock must remain unchanged
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_item_without_quantity_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_missing_quantity",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_missing_quantity",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try creating an order item without quantity
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1
                }
            ]
        }
    )

    assert response.status_code == 400

    # Stock must remain unchanged
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_with_non_integer_quantity_returns_400(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_invalid_quantity_type",
            "password": "TestPassword123!"
        }
    )

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_invalid_quantity_type",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try ordering a fractional quantity
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1.5
                }
            ]
        }
    )

    assert response.status_code == 400

    # Stock should remain unchanged
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_create_order_with_invalid_items_type_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_invalid_items_type",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_invalid_items_type",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Send a string instead of a list
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": "product_id=1, quantity=1"
        }
    )

    assert response.status_code == 400

    # The request must not change stock
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_cancelling_order_twice_does_not_restore_stock_twice(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_double_cancel",
            "password": "TestPassword123!"
        }
    )

    # Log in
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_double_cancel",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order for 2 units
    order_response = client.post(
        "/orders",
        headers=headers,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                }
            ]
        }
    )

    assert order_response.status_code == 201

    orders_response = client.get("/orders", headers=headers)
    order_id = orders_response.get_json()["orders"][0]["id"]

    # First cancellation
    first_cancel = client.patch(
        f"/orders/{order_id}",
        headers=headers,
        json={"status": "cancelled"}
    )

    assert first_cancel.status_code == 200

    # Stock should be restored to 10
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 10

    # Attempt to cancel the same order again
    second_cancel = client.patch(
        f"/orders/{order_id}",
        headers=headers,
        json={"status": "cancelled"}
    )

    # A second cancellation should be rejected
    assert second_cancel.status_code == 409

    # Stock must remain 10, not increase to 12
    product_response = client.get("/products/1")
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_customers_only_see_their_own_orders(client):
    # Register Customer A
    client.post(
        "/register",
        json={
            "username": "pytest_list_customer_a",
            "password": "TestPassword123!"
        }
    )

    # Log in as Customer A
    login_a = client.post(
        "/login",
        json={
            "username": "pytest_list_customer_a",
            "password": "TestPassword123!"
        }
    )

    assert login_a.status_code == 200
    token_a = login_a.get_json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Customer A creates an order
    order_a = client.post(
        "/orders",
        headers=headers_a,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_a.status_code == 201
    order_id_a = order_a.get_json()["order"]["id"]

    # Register Customer B
    client.post(
        "/register",
        json={
            "username": "pytest_list_customer_b",
            "password": "TestPassword123!"
        }
    )

    # Log in as Customer B
    login_b = client.post(
        "/login",
        json={
            "username": "pytest_list_customer_b",
            "password": "TestPassword123!"
        }
    )

    assert login_b.status_code == 200
    token_b = login_b.get_json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Customer B creates an order
    order_b = client.post(
        "/orders",
        headers=headers_b,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_b.status_code == 201
    order_id_b = order_b.get_json()["order"]["id"]

    # Customer A retrieves their orders
    response_a = client.get("/orders", headers=headers_a)

    assert response_a.status_code == 200
    orders_a = response_a.get_json()["orders"]
    order_ids_a = [order["id"] for order in orders_a]

    assert order_id_a in order_ids_a
    assert order_id_b not in order_ids_a

    # Customer B retrieves their orders
    response_b = client.get("/orders", headers=headers_b)

    assert response_b.status_code == 200
    orders_b = response_b.get_json()["orders"]
    order_ids_b = [order["id"] for order in orders_b]

    assert order_id_b in order_ids_b
    assert order_id_a not in order_ids_b
    
    
def test_failed_multi_product_order_preserves_all_stock(client):
    # Create a second product with only 1 unit in stock
    limited_product = Product(
        name="Limited Stock Product",
        price=100,
        stock=1
    )

    db.session.add(limited_product)
    db.session.commit()

    limited_product_id = limited_product.id

    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_transaction_user",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_transaction_user",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Attempt an order containing two products.
    # Product 1 has 10 units; the second product has only 1.
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                },
                {
                    "product_id": limited_product_id,
                    "quantity": 2
                }
            ]
        }
    )

    # The second item exceeds available stock
    assert response.status_code == 409

    # Product 1 must still have all 10 units
    product_one_response = client.get("/products/1")

    assert product_one_response.status_code == 200
    assert product_one_response.get_json()["product"]["stock"] == 10

    # The second product must still have 1 unit
    limited_product_response = client.get(
        f"/products/{limited_product_id}"
    )

    assert limited_product_response.status_code == 200
    assert limited_product_response.get_json()["product"]["stock"] == 1
    

def test_order_total_is_calculated_correctly(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_order_total",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_order_total",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order for 2 units
    order_response = client.post(
        "/orders",
        headers=headers,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Retrieve the customer's orders
    response = client.get("/orders", headers=headers)

    assert response.status_code == 200

    orders = response.get_json()["orders"]

    assert len(orders) == 1

    order = orders[0]

    # Price = 1500 per unit; quantity = 2
    expected_total = Decimal("1500.00") * 2

    assert Decimal(str(order["total_amount"])) == expected_total
    
def test_create_order_with_string_quantity_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_string_quantity",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_string_quantity",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Try ordering with a string quantity
    response = client.post(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": "2"
                }
            ]
        }
    )

    assert response.status_code == 400

    # Stock must remain unchanged
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 10
    
def test_update_order_with_invalid_status_returns_400(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_invalid_order_status",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_invalid_order_status",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    order_response = client.post(
        "/orders",
        headers=headers,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Find the new order ID
    orders_response = client.get("/orders", headers=headers)

    assert orders_response.status_code == 200

    orders = orders_response.get_json()["orders"]
    order_id = orders[0]["id"]

    # Attempt an unsupported status change
    response = client.patch(
        f"/orders/{order_id}",
        headers=headers,
        json={"status": "shipped"}
    )

    assert response.status_code == 400

    # Verify the order remains pending
    orders_response = client.get("/orders", headers=headers)

    assert orders_response.status_code == 200

    order = orders_response.get_json()["orders"][0]

    assert order["status"] == "pending"

    # Verify stock remains reduced only by the original order
    product_response = client.get("/products/1")

    assert product_response.status_code == 200
    assert product_response.get_json()["product"]["stock"] == 9
    
def test_update_order_without_status_returns_400(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_missing_order_status",
            "password": "TestPassword123!"
        }
    )

    # Log in
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_missing_order_status",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    order_response = client.post(
        "/orders",
        headers=headers,
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert order_response.status_code == 201

    # Find the order ID
    orders_response = client.get("/orders", headers=headers)

    assert orders_response.status_code == 200
    order_id = orders_response.get_json()["orders"][0]["id"]

    # Attempt to update the order without specifying a status
    response = client.patch(
        f"/orders/{order_id}",
        headers=headers,
        json={}
    )

    assert response.status_code == 400

    # Verify that the order remains pending
    orders_response = client.get("/orders", headers=headers)

    assert orders_response.status_code == 200
    assert orders_response.get_json()["orders"][0]["status"] == "pending"
    
def test_customer_can_view_own_order(client):
    client.post("/register", json={
        "username": "pytest_own_order",
        "password": "TestPassword123!"
    })

    login = client.post("/login", json={
        "username": "pytest_own_order",
        "password": "TestPassword123!"
    })

    assert login.status_code == 200
    token = login.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    created = client.post("/orders", headers=headers, json={
        "items": [{"product_id": 1, "quantity": 1}]
    })

    assert created.status_code == 201

    # Find the order ID
    orders = client.get("/orders", headers=headers).get_json()["orders"]
    order_id = orders[0]["id"]

    # Retrieve that specific order
    response = client.get(f"/orders/{order_id}", headers=headers)

    assert response.status_code == 200
    
def test_cancel_order_without_token_returns_401(client):
    # Register and log in
    client.post("/register", json={
        "username": "pytest_cancel_no_token",
        "password": "TestPassword123!"
    })

    login = client.post("/login", json={
        "username": "pytest_cancel_no_token",
        "password": "TestPassword123!"
    })

    assert login.status_code == 200
    token = login.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    created = client.post("/orders", headers=headers, json={
        "items": [{"product_id": 1, "quantity": 1}]
    })

    assert created.status_code == 201

    # Find the order ID
    orders = client.get("/orders", headers=headers).get_json()["orders"]
    order_id = orders[0]["id"]

    # Attempt cancellation without a token
    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "cancelled"}
    )

    assert response.status_code == 401

    # Verify the order remains pending
    orders = client.get("/orders", headers=headers).get_json()["orders"]
    assert orders[0]["status"] == "pending"

    # Stock should remain reduced only by the original order
    product = client.get("/products/1").get_json()["product"]
    assert product["stock"] == 9
    
def test_cancel_order_with_invalid_token_returns_401(client):
    # Register and log in
    client.post("/register", json={
        "username": "pytest_invalid_cancel_token",
        "password": "TestPassword123!"
    })

    login = client.post("/login", json={
        "username": "pytest_invalid_cancel_token",
        "password": "TestPassword123!"
    })

    assert login.status_code == 200
    token = login.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an order
    created = client.post("/orders", headers=headers, json={
        "items": [{"product_id": 1, "quantity": 1}]
    })

    assert created.status_code == 201

    # Find the order ID
    orders = client.get("/orders", headers=headers).get_json()["orders"]
    order_id = orders[0]["id"]

    # Attempt cancellation with an invalid token
    response = client.patch(
        f"/orders/{order_id}",
        headers={"Authorization": "Bearer invalid_token"},
        json={"status": "cancelled"}
    )

    assert response.status_code == 401

    # Verify the order remains pending and stock remains 9
    orders = client.get("/orders", headers=headers).get_json()["orders"]
    assert orders[0]["status"] == "pending"

    product = client.get("/products/1").get_json()["product"]
    assert product["stock"] == 9