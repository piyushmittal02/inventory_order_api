def test_register_user_returns_201(client):
    response = client.post(
        "/register",
        json={
            "username": "pytest_user",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 201

def test_login_with_valid_credentials_returns_200(client):
    # First, register a user
    client.post(
        "/register",
        json={
            "username": "pytest_login_user",
            "password": "TestPassword123!"
        }
    )

    # Then, log in with the same credentials
    response = client.post(
        "/login",
        json={
            "username": "pytest_login_user",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200
    data = response.get_json()

    assert "token" in data
    assert isinstance(data["token"], str)
    assert data["token"]
    
def test_login_with_invalid_password_returns_401(client):
    # Register a user
    client.post(
        "/register",
        json={
            "username": "pytest_wrong_password_user",
            "password": "CorrectPassword123!"
        }
    )

    # Attempt login with the wrong password
    response = client.post(
        "/login",
        json={
            "username": "pytest_wrong_password_user",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    
def test_login_with_nonexistent_user_returns_401(client):
    response = client.post(
        "/login",
        json={
            "username": "unknown_pytest_user",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 401
    
def test_register_does_not_return_password_data(client):
    response = client.post(
        "/register",
        json={
            "username": "pytest_security_user",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "password" not in data
    assert "password_hash" not in data
    
def test_register_duplicate_username_returns_409(client):
    payload = {
        "username": "duplicate_test_user",
        "password": "TestPassword123!"
    }

    # Register the username for the first time
    first_response = client.post(
        "/register",
        json=payload
    )

    assert first_response.status_code == 201

    # Try registering the same username again
    second_response = client.post(
        "/register",
        json=payload
    )

    assert second_response.status_code == 409
    
def test_register_without_password_returns_400(client):
    response = client.post(
        "/register",
        json={
            "username": "pytest_missing_password_user"
        }
    )

    assert response.status_code == 400
    
def test_register_without_username_returns_400(client):
    response = client.post(
        "/register",
        json={
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400

def test_register_with_empty_username_returns_400(client):
    response = client.post(
        "/register",
        json={
            "username": "   ",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400
    
def test_register_with_empty_password_returns_400(client):
    response = client.post(
        "/register",
        json={
            "username": "pytest_empty_password_user",
            "password": ""
        }
    )

    assert response.status_code == 400
    

def test_register_with_non_string_password_returns_400(client):
    response = client.post(
        "/register",
        json={
            "username": "pytest_invalid_password_type",
            "password": 12345678
        }
    )

    assert response.status_code == 400
    
def test_register_with_non_string_username_returns_400(client):
    response = client.post(
        "/register",
        json={
            "username": 12345,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400
    
def test_login_without_password_returns_400(client):
    # Register a user first
    client.post(
        "/register",
        json={
            "username": "pytest_missing_login_password",
            "password": "TestPassword123!"
        }
    )

    # Attempt login without providing a password
    response = client.post(
        "/login",
        json={
            "username": "pytest_missing_login_password"
        }
    )

    assert response.status_code == 400
    
def test_login_without_username_returns_400(client):
    response = client.post(
        "/login",
        json={
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400
    
def test_login_with_empty_username_returns_400(client):
    response = client.post(
        "/login",
        json={
            "username": "   ",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400
    
def test_login_with_empty_password_returns_400(client):
    # Register a user first
    register_response = client.post(
        "/register",
        json={
            "username": "pytest_empty_login_password",
            "password": "CorrectPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Attempt login with an empty password
    response = client.post(
        "/login",
        json={
            "username": "pytest_empty_login_password",
            "password": ""
        }
    )

    assert response.status_code == 400
    
def test_login_with_non_string_password_returns_400(client):
    # Register a user with a valid password
    client.post(
        "/register",
        json={
            "username": "pytest_password_type_user",
            "password": "CorrectPassword123!"
        }
    )

    # Attempt login with a numeric password
    response = client.post(
        "/login",
        json={
            "username": "pytest_password_type_user",
            "password": 12345678
        }
    )

    assert response.status_code == 400

def test_login_with_non_string_username_returns_400(client):
    response = client.post(
        "/login",
        json={
            "username": 12345,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400