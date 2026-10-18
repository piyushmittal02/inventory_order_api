# Inventory and Order Management API

A RESTful backend API built with Flask and SQLAlchemy for managing products, inventory, user authentication, and customer orders.

The project demonstrates backend development concepts including REST APIs, JWT authentication, role-based access control, database operations, inventory management, and automated testing with Pytest.

## Features

* **User Authentication:** Register users and log in using username and password.
* **JWT Authentication:** Protect API endpoints using JSON Web Tokens.
* **Product Management:** Retrieve, create, update, and delete products.
* **Inventory Management:** Track product stock and update inventory when orders are placed or cancelled.
* **Order Management:** Create orders, retrieve order information, and manage order status.
* **Authorization:** Restrict product-management operations and enforce order ownership checks.
* **Database Migrations:** Manage database schema changes using Flask-Migrate and Alembic.
* **Automated Testing:** Test API endpoints, authentication, input validation, order processing, and inventory behavior using Pytest.

## Technology Stack

* Python
* Flask
* Flask-SQLAlchemy
* SQLAlchemy
* Flask-Migrate
* Alembic
* PyJWT
* Pytest
* SQLite for local development by default

## Project Structure

```text
inventory_order_api/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── .env
├── .gitignore
├── migrations/
│   └── versions/
├── models/
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   └── orderitem.py
├── repositories/
│   ├── user_repository.py
│   ├── product_repository.py
│   └── order_repository.py
├── routes/
│   ├── auth_routes.py
│   ├── product_routes.py
│   └── order_routes.py
├── services/
│   ├── order_service.py
│   └── product_service.py
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_products.py
    └── test_orders.py
```

### Architecture Overview

* **Routes:** Handle incoming HTTP requests and return API responses.
* **Services:** Implement business logic, including product and order operations.
* **Repositories:** Encapsulate database-access operations.
* **Models:** Define database entities and their relationships.
* **Migrations:** Track database schema changes.
* **Tests:** Verify expected API behavior and help prevent regressions.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/piyushmittal02/inventory_order_api.git
cd inventory_order_api
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the environment

Review `config.py` and provide any required environment variables in a local `.env` file.

The application uses SQLite by default when `DATABASE_URL` is not set. A different database can be configured through the application's database settings.

Keep secret keys and other sensitive configuration out of version control. The `.env` file is excluded by `.gitignore`.

### 5. Apply database migrations

With the environment configured, run:

```powershell
flask --app app db upgrade
```

### 6. Run the application

```powershell
python app.py
```

The development server will display its local address in the terminal.

## API Endpoints

The following endpoints are provided by the application:

| Method | Endpoint                 | Purpose                                  |
| ------ | ------------------------ | ---------------------------------------- |
| POST   | `/register`              | Register a user                          |
| POST   | `/login`                 | Authenticate a user and obtain a JWT     |
| GET    | `/products`              | Retrieve products                        |
| GET    | `/products/<product_id>` | Retrieve a specific product              |
| POST   | `/products`              | Create a product                         |
| PATCH  | `/products/<product_id>` | Update a product                         |
| DELETE | `/products/<product_id>` | Delete a product                         |
| POST   | `/orders`                | Create an order                          |
| GET    | `/orders`                | Retrieve the authenticated user's orders |
| GET    | `/orders/<order_id>`     | Retrieve a specific order                |
| PATCH  | `/orders/<order_id>`     | Update order status                      |

Protected endpoints require a valid JWT in the authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

Product-management permissions and order ownership are checked by the API. The exact response codes depend on the outcome of each request.

## Running Tests

Run the complete test suite from the project root:

```powershell
python -m pytest -v --tb=short
```

The tests cover authentication, product operations, input validation, order creation, authorization, stock adjustments, order cancellation, and other important business rules.

The test fixture uses an in-memory SQLite database to isolate test data from the normal development database.

## Key Backend Concepts

This project provides practical experience with:

* RESTful API design and HTTP status codes
* Authentication versus authorization
* JWT-based authentication
* Password hashing and credential validation
* Role-based access control
* SQLAlchemy ORM and database models
* Repository and service-layer separation
* Database migrations
* Input validation and error handling
* Order processing and inventory consistency
* Automated testing with Pytest

## Repository

GitHub: https://github.com/piyushmittal02/inventory_order_api
