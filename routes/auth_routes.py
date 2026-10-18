import jwt
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
#/////////////auth routes/////////////////////
#////outside because we need to use it in other routes/////////////////////
def verify_token(app):
    
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, jsonify({
            "error": "Authorization header is missing"
        }), 401

    if not auth_header.startswith("Bearer "):
        return None, jsonify({
            "error": "Invalid Authorization header"
        }), 401

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"]
        )

        return payload, None, None

    except jwt.ExpiredSignatureError:
        return None, jsonify({
            "error": "Token has expired"
        }), 401

    except jwt.InvalidTokenError:
        return None, jsonify({
            "error": "Invalid token"
        }), 401


def register_auth(app, db, User):
    auth_bp = Blueprint("auth", __name__)
    @auth_bp.get("/test-token")
    def test_token():
        payload, error, status = verify_token(app)

        if error:
            return error, status

        return jsonify({
            "message": "Token is valid",
            "user_id": payload["user_id"],
            "role": payload["role"]
        }), 200

    @auth_bp.post("/register")
    def register():
        data = request.get_json()
         
        if not isinstance(data, dict):
          return jsonify({
        "error": "Request body must be a JSON object"
         }), 400

        if "password" not in data or not isinstance(data["password"], str) or not data["password"]:
         return jsonify({
        "error": "Password is required"
          }), 400
         
        if "username" not in data:
         return jsonify({
        "error": "Username is required"
         }), 400

        if not isinstance(data["username"], str) or not data["username"].strip():
         return jsonify({
        "error": "Username must be a non-empty string"
         }), 400
         
        username = data["username"]
        password = data["password"]

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return jsonify({
                "error": "Username already exists"
            }), 409

        password_hash = generate_password_hash(password)

        user = User(
            username=username,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    @auth_bp.post("/login")
    def login():
        data = request.get_json()
        if not isinstance(data, dict):
          return jsonify({
        "error": "Request body must be a JSON object"
         }), 400

        if "username" not in data:
         return jsonify({
        "error": "Username is required"
         }), 400
        
        if not isinstance(data["username"], str) or not data["username"].strip():
          return jsonify({
        "error": "Username must be a non-empty string"
          }), 400
          
        if "password" not in data or not isinstance(data["password"], str) or not data["password"]:
         return jsonify({
        "error": "Password is required"
         }), 400
        username = data["username"]
        password = data["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        if not check_password_hash(
            user.password_hash,
            password
        ):
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        payload = {
            "user_id": user.id,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }

        token = jwt.encode(
            payload,
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256"
        )

        return jsonify({
            "message": "Login successful",
            "token": token
        }), 200
    
    app.register_blueprint(auth_bp)