# from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from extensions import db
from config import Config
from flask_migrate import Migrate
app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
#/////////////user table access////////////////////
from models.user import User

#/////////////product table access////////////////////
from models.product import Product

#////////////order table////////////////////
from models.order import Order

#////////////order item table////////////////////
from models.orderitem import OrderItem

#/////////register auth routes/////////////////////
from routes.auth_routes import register_auth

#/////////register product routes/////////////////////
from routes.product_routes import register_product_routes
register_auth(app, db, User)
register_product_routes(app, db, Product)

#/////////register order routes/////////////////////
from routes.order_routes import register_order_routes
register_order_routes(app)
#////////////create database/////////////////////
# with app.app_context():
#     db.create_all()


if __name__ == "__main__":
    app.run(debug=True)