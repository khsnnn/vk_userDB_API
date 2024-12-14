import pytest
from fastapi.testclient import TestClient
from app import app, AUTH_TOKEN, db_handler

TEST_TOKEN = AUTH_TOKEN
TEST_PASSWORD = db_handler

test_client = TestClient(app)

@pytest.fixture
def setup_test_user():
    user_data = {
        "id": 12345,
        "label": "User",
        "name": "John Doe",
        "screen_name": "Johny",
        "sex": 1,
        "city": "la",
        "follows": [],
        "subscribed": []
    }

    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = test_client.post("/nodes", json=user_data, headers=headers)
    if response.status_code != 200:
        pytest.fail(f"Failed to create test user: {response.json()}")
    return user_data

def test_fetch_user(setup_test_user):
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = test_client.get("/user/12345", headers=headers)
    assert response.status_code == 200, f"Failed to fetch user: {response.json()}"
    assert response.json() == {
        "id": 12345,
        "name": "John Doe",
        "screen_name": "Johny",
        "sex": 1,
        "city": "la"
    }

def test_fetch_top_users():
    response = test_client.get("/top-users")
    assert response.status_code == 200, f"Failed to fetch top users: {response.json()}"
    assert isinstance(response.json(), list)

def test_fetch_top_groups():
    response = test_client.get("/top-groups")
    assert response.status_code == 200, f"Failed to fetch top groups: {response.json()}"
    assert isinstance(response.json(), list)

def test_fetch_users_count():
    response = test_client.get("/users-count")
    assert response.status_code == 200, f"Failed to fetch users count: {response.json()}"
    assert "users_count" in response.json()

def test_fetch_groups_count():
    response = test_client.get("/groups-count")
    assert response.status_code == 200, f"Failed to fetch groups count: {response.json()}"
    assert "groups_count" in response.json()

def test_fetch_all_nodes():
    response = test_client.get("/nodes")
    assert response.status_code == 200, f"Failed to fetch all nodes: {response.json()}"
    assert isinstance(response.json(), list)

def test_delete_node_and_relations(setup_test_user):
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

    response = test_client.get("/user/12345", headers=headers)
    assert response.status_code == 200, f"Failed to fetch user before deletion: {response.json()}"
    response = test_client.delete("/nodes/User/12345", headers=headers)
    assert response.status_code == 200, f"Failed to delete node: {response.json()}"
    assert response.json() == {"status": "success"}
    response = test_client.get("/user/12345", headers=headers)
    assert response.status_code == 404, f"User still exists after deletion: {response.json()}"
