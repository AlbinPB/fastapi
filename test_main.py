import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.declarative import declarative_base
from database import Base, get_db

# Setup the Test Database
TEST_DATABASE_URL = "sqlite:///./unittest.db"  # Use a different DB for testing

# Create a new engine and session for the test database
TestEngine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TestEngine)

@pytest.fixture(scope="module")
def alembic_config():
    """Provide the Alembic configuration for migrations."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)  # Use test DB URL
    return config

@pytest.fixture(scope="module")
def apply_migrations(alembic_config):
    """Apply migrations to the test database."""
    command.upgrade(alembic_config, "head")  # Apply all migrations
    yield
    command.downgrade(alembic_config, "base")  # Downgrade to base after tests

@pytest.fixture(scope="function")
def db_session(apply_migrations):
    """Provide a new database session for each test."""
    connection = TestEngine.connect()
    transaction = connection.begin()  # Start a transaction
    session = TestSessionLocal(bind=connection)  # Use the test engine for session

    yield session

    session.close()  # Close the session
    transaction.rollback()  # Rollback the transaction
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client that uses the test database session."""
    # Override the dependency for getting the database session
    def override_get_db():
        yield db_session

    # Apply the override to the FastAPI app
    app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    with TestClient(app) as client:
        yield client

    # Clear the overrides after the test
    app.dependency_overrides.clear()

# Test POST user creation
def test_create_user(client):
    # Create the database schema before running the test

    response = client.post("/users", json={"name": "John Doe", "email": "john@example.com", "age": 30})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["age"] == 30


def test_get_users(client):
    client.post("/users", json={"name": "Jane Doe", "email": "jane@example.com", "age": 28})
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Jane Doe"

def test_get_user(client):
    response = client.post("/users", json={"name": "John Smith", "email": "johnsmith@example.com", "age": 25})
    user_id = response.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["email"] == "johnsmith@example.com"

def test_update_user(client):
    response = client.post("/users", json={"name": "Michael", "email": "michael@example.com", "age": 32})
    user_id = response.json()["id"]
    updated_user = {"name": "Michael Jackson", "email": "michaeljackson@example.com", "age": 33}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Michael Jackson"
    assert data["email"] == "michaeljackson@example.com"
    assert data["age"] == 33

def test_delete_user(client):
    response = client.post("/users", json={"name": "Sam", "email": "sam@example.com", "age": 35})
    user_id = response.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User deleted successfully"


def test_post_role(client):
    response = client.post("/roles", json={"name": "Admin"})
    assert response.status_code == 200
    assert response.json()["name"] == "Admin"


def test_get_roles(client):
    response = client.post("/roles", json={"name": "Admin"})
    response = client.get("/roles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Admin"

def test_put_role(client):
    response = client.post("/roles", json={"name": "Admin"})
    role_id = response.json()["id"]
    updated_role = {"name": "Super Admin"}
    response = client.put(f"/roles/{role_id}", json=updated_role)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Super Admin"

def test_delete_role(client):
    response = client.post("/roles", json={"name": "Admin"})
    role_id = response.json()["id"]
    response = client.delete(f"/roles/{role_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Role deleted successfully"

def test_assign_role(client):
    response = client.post("/users", json={"name": "John Smith", "email": "johnsmith@example.com", "age": 25})
    response_role = client.post("/roles", json={"name": "Admin"})
    user_id = response.json()["id"]
    role_id = response_role.json()["id"]
    response_assign = client.post(f"/user_roles", json={"user_id": user_id, "role_id": role_id})
    assert response_assign.status_code == 200
    assert response_assign.json()["user_id"] == user_id