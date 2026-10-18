import pytest
from app import app
from extensions import db
from models.product import Product

@pytest.fixture

def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        test_product = Product(
            name="Test Keyboard",
            price=1500,
            stock=10
        )

        db.session.add(test_product)
        db.session.commit()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def test_get_products_returns_200(client):
    response = client.get("/products")

    assert response.status_code == 200

    data = response.get_json()

    assert "products" in data
    assert isinstance(data["products"], list)
    
def test_get_missing_product_returns_404(client):
    response = client.get("/products/999999")

    assert response.status_code == 404
    
def test_get_existing_product_returns_200(client):
    response = client.get("/products/1")

    assert response.status_code == 200

    data = response.get_json()

    assert "product" in data
    assert data["product"]["id"] == 1

def test_get_existing_product_contains_expected_fields(client):
    response = client.get("/products/1")

    assert response.status_code == 200

    data = response.get_json()
    product = data["product"]

    assert "id" in product
    assert "name" in product
    assert "price" in product
    assert "stock" in product
    
def test_create_product_without_token_returns_401(client):
    response = client.post(
        "/products",
        json={
            "name": "Unauthorized Product",
            "price": 100,
            "stock": 5
        }
    )

    assert response.status_code == 401
    
# def test_create_product_with_customer_token_returns_403(client):
#     response = client.post(
#         "/products",
#         headers={
#             "Authorization": "Bearer invalid_customer_token"
#         },
#         json={
#             "name": "Unauthorized Product",
#             "price": 100,
#             "stock": 5
#         }
#     )

#     assert response.status_code == 403
def test_create_product_with_invalid_token_returns_401(client):
    response = client.post(
        "/products",
        headers={
            "Authorization": "Bearer invalid_token"
        },
        json={
            "name": "Invalid Token Product",
            "price": 100,
            "stock": 5
        }
    )

    assert response.status_code == 401
    
def test_update_product_without_token_returns_401(client):
    response = client.patch(
        "/products/1",
        json={
            "stock": 20
        }
    )

    assert response.status_code == 401
    
def test_delete_product_without_token_returns_401(client):
    response = client.delete("/products/1")

    assert response.status_code == 401
    
def test_update_product_with_invalid_token_returns_401(client):
    response = client.patch(
        "/products/1",
        headers={
            "Authorization": "Bearer invalid_token"
        },
        json={
            "stock": 20
        }
    )

    assert response.status_code == 401
    
def test_delete_product_with_invalid_token_returns_401(client):
    response = client.delete(
        "/products/1",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401

def test_create_product_with_invalid_token_returns_401(client):
    response = client.post(
        "/products",
        headers={
            "Authorization": "Bearer invalid_token"
        },
        json={
            "name": "Invalid Token Product",
            "price": 100,
            "stock": 5
        }
    )

    assert response.status_code == 401
    
def test_products_uses_test_database(client):
    response = client.get("/products")

    assert response.status_code == 200

    data = response.get_json()
    products = data["products"]

    assert len(products) == 1
    assert products[0]["name"] == "Test Keyboard"
    
    
def test_customer_token_cannot_create_product_returns_403(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_customer_auth",
            "password": "TestPassword123!"
        }
    )

    # Log in to obtain a real JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_customer_auth",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]

    # Try creating a product as a customer
    response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Customer Test Product",
            "price": 100,
            "stock": 5
        }
    )

    assert response.status_code == 403
    
def test_customer_token_cannot_update_product_returns_403(client):
    # Register a customer
    client.post(
        "/register",
        json={
            "username": "pytest_customer_update",
            "password": "TestPassword123!"
        }
    )

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_customer_update",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]

    # Try updating a product as a customer
    response = client.patch(
        "/products/1",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "stock": 20
        }
    )

    assert response.status_code == 403
    
def test_customer_token_cannot_delete_product_returns_403(client):
    # Register a customer
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_customer_delete",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in to obtain a valid JWT
    login_response = client.post(
        "/login",
        json={
            "username": "pytest_customer_delete",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["token"]

    # Try deleting a product as a customer
    response = client.delete(
        "/products/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403