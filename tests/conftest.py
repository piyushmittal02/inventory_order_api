import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

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

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()