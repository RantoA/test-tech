from fastapi.testclient import TestClient

from tests.conftest import API, DEFAULT_PASSWORD, csrf_headers


def test_get_profile(auth_client: TestClient) -> None:
    response = auth_client.get(f"{API}/users/me")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Alice Martin"
    assert data["email"] == "alice@example.com"


def test_update_profile(auth_client: TestClient) -> None:
    response = auth_client.put(
        f"{API}/users/me",
        json={"name": "Alice Dupont", "email": "alice.dupont@example.com"},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Profile updated successfully"
    assert body["data"]["name"] == "Alice Dupont"
    assert body["data"]["email"] == "alice.dupont@example.com"


def test_update_profile_email_conflict(auth_client: TestClient, other_client: TestClient) -> None:
    response = auth_client.put(
        f"{API}/users/me", json={"email": "bob@example.com"}, headers=csrf_headers(auth_client)
    )
    assert response.status_code == 409


def test_update_profile_validation(auth_client: TestClient) -> None:
    headers = csrf_headers(auth_client)
    assert auth_client.put(f"{API}/users/me", json={}, headers=headers).status_code == 422
    assert (
        auth_client.put(f"{API}/users/me", json={"email": "bad"}, headers=headers).status_code
        == 422
    )
    assert (
        auth_client.put(f"{API}/users/me", json={"role": "admin"}, headers=headers).status_code
        == 422
    )


def test_change_password(auth_client: TestClient) -> None:
    response = auth_client.patch(
        f"{API}/users/me/password",
        json={"current_password": DEFAULT_PASSWORD, "new_password": "NewPassword456"},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    auth_client.cookies.clear()
    old = auth_client.post(
        f"{API}/auth/login", json={"email": "alice@example.com", "password": DEFAULT_PASSWORD}
    )
    assert old.status_code == 401
    new = auth_client.post(
        f"{API}/auth/login", json={"email": "alice@example.com", "password": "NewPassword456"}
    )
    assert new.status_code == 200


def test_change_password_wrong_current(auth_client: TestClient) -> None:
    response = auth_client.patch(
        f"{API}/users/me/password",
        json={"current_password": "WrongPass123", "new_password": "NewPassword456"},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Current password is incorrect"


def test_change_password_weak_new_password(auth_client: TestClient) -> None:
    response = auth_client.patch(
        f"{API}/users/me/password",
        json={"current_password": DEFAULT_PASSWORD, "new_password": "abc"},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 422
