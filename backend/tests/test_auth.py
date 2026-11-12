from fastapi.testclient import TestClient

from tests.conftest import API, DEFAULT_PASSWORD, csrf_headers, register_user


def test_register_creates_account_and_session(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/register",
        json={"name": "Alice Martin", "email": "Alice@Example.com", "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == 201
    assert body["message"] == "Account created successfully"
    assert body["data"]["user"]["email"] == "alice@example.com"
    assert "password" not in body["data"]["user"]
    assert "hashed_password" not in body["data"]["user"]
    assert "access_token" in response.cookies
    assert "csrf_token" in response.cookies
    set_cookie = response.headers.get_list("set-cookie")
    assert any("access_token" in c and "HttpOnly" in c for c in set_cookie)


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    register_user(client)
    response = client.post(
        f"{API}/auth/register",
        json={"name": "Other", "email": "ALICE@example.com", "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 409
    assert response.json() == {
        "status": 409,
        "message": "An account with this email already exists",
        "data": None,
    }


def test_register_validation_errors(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/register", json={"name": "A", "email": "not-an-email", "password": "short"}
    )
    assert response.status_code == 422
    body = response.json()
    assert body["message"] == "Validation error"
    fields = {error["field"] for error in body["data"]["errors"]}
    assert {"name", "email", "password"} <= fields


def test_login_success(client: TestClient) -> None:
    register_user(client)
    client.cookies.clear()
    response = client.post(
        f"{API}/auth/login", json={"email": "alice@example.com", "password": DEFAULT_PASSWORD}
    )
    assert response.status_code == 200
    assert response.json()["data"]["access_token"]
    assert client.get(f"{API}/users/me").status_code == 200


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    register_user(client)
    response = client.post(
        f"{API}/auth/login", json={"email": "alice@example.com", "password": "WrongPass123"}
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid email or password"


def test_login_unknown_email_returns_401(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/login", json={"email": "ghost@example.com", "password": DEFAULT_PASSWORD}
    )
    assert response.status_code == 401


def test_protected_route_requires_authentication(client: TestClient) -> None:
    response = client.get(f"{API}/users/me")
    assert response.status_code == 401
    assert response.json()["status"] == 401


def test_invalid_token_is_rejected(client: TestClient) -> None:
    response = client.get(f"{API}/users/me", headers={"Authorization": "Bearer not.a.valid.token"})
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid or expired token"


def test_bearer_token_authentication(client: TestClient) -> None:
    token = register_user(client)["access_token"]
    client.cookies.clear()
    response = client.get(f"{API}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_cookie_mutation_without_csrf_token_is_forbidden(auth_client: TestClient) -> None:
    response = auth_client.put(f"{API}/users/me", json={"name": "New Name"})
    assert response.status_code == 403
    assert response.json()["message"] == "Invalid or missing CSRF token"
    ok = auth_client.put(
        f"{API}/users/me", json={"name": "New Name"}, headers=csrf_headers(auth_client)
    )
    assert ok.status_code == 200


def test_logout_clears_session(auth_client: TestClient) -> None:
    response = auth_client.post(f"{API}/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
    assert auth_client.get(f"{API}/users/me").status_code == 401
