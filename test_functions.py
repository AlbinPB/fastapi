import pytest
from fastapi.testclient import TestClient
from main import app, SessionLocal, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Role, UserRole
# from database import Base  # Assuming you have Base defined in your database module
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.declarative import declarative_base

# Setup the Test Database
TEST_DATABASE_URL = "sqlite:///./unittest.db"  # Use a different DB for testing

@pytest.fixture(scope="module")
def alembic_config():
    """Provide the Alembic configuration for migrations."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)  # Use test DB URL
    return config

@pytest.fixture(scope="module")
def engine_create():
    """Create and drop tables in the test database."""
    engine = create_engine(TEST_DATABASE_URL)
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)  # Ensure tables are created explicitly before migrations
    yield engine
    Base.metadata.drop_all(bind=engine)  # Clean up after tests

@pytest.fixture(scope="module")
def connection(engine):
    """Create a database connection."""
    connection = engine.connect()
    yield connection
    connection.close()

@pytest.fixture(scope="function", autouse=True)
def migrate_db(engine, alembic_config):
    """Run migrations before each test and ensure the database is in the correct state."""
    alembic_config.attributes["connection"] = engine.connect()  # Pass the engine connection to Alembic
    command.stamp(alembic_config, "head")  # Stamp the current revision in the database
    command.upgrade(alembic_config, "head")  # Apply all migrations
    yield
    command.downgrade(alembic_config, "base")  # Downgrade to base after each test


@pytest.fixture(scope="function")
def db_session(connection):
    """Provide a new database session for each test."""
    transaction = connection.begin()  # Start a transaction
    SessionLocal = sessionmaker(bind=connection)  # Use the test engine for session
    session = SessionLocal()

    yield session

    session.close()  # Close the session
    transaction.rollback()  # Rollback the transaction


@pytest.fixture
def client(db_session):
    """Create a test client that uses the test database session."""
    # Override the dependency for getting the database session
    def override_get_db():
        yield db_session

    # Apply the override to the FastAPI app
    app.dependency_overrides[SessionLocal] = override_get_db

    # Create the test client
    with TestClient(app) as client:
        yield client

    # Clear the overrides after the test
    app.dependency_overrides.clear()



@pytest.fixture
def db():
    # Test database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





# Test POST user creation
def test_create_user(client):
    # Create the database schema before running the test

    response = client.post("/users", json={"name": "John Doe", "email": "john@example.com", "age": 30})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["age"] == 30

'''
# Test GET all users
def test_get_users(client):
    client.post("/users", json={"name": "Jane Doe", "email": "jane@example.com", "age": 28})
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[1]["name"] == "Jane Doe"


# Test GET a user by ID
def test_get_user(client):
    response = client.post("/users", json={"name": "John Smith", "email": "johnsmith@example.com", "age": 25})
    user_id = response.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["email"] == "johnsmith@example.com"


# Test PUT update user
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


# Test DELETE user
def test_delete_user(client):
    response = client.post("/users", json={"name": "Sam", "email": "sam@example.com", "age": 35})
    user_id = response.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User deleted successfully"


# Test POST role creation
def test_create_role(client):
    response = client.post("/roles", json={"name": "Admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Admin"


# Test GET roles
def test_get_roles(client):
    response = client.post("/roles", json={"name": "User"})
    response = client.get("/roles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[1]["name"] == "User"


# Test POST user_role assignment
def test_assign_role_to_user(client):
    # Create a user and role
    client.post("/users", json={"name": "Alex", "email": "alex@example.com", "age": 29})
    client.post("/roles", json={"name": "Editor"})
    response_user = client.get("/users")
    response_role = client.get("/roles")
    
    user_id = response_user.json()[0]["id"]
    role_id = response_role.json()[0]["id"]
    
    response = client.post("/user_roles", json={"user_id": user_id, "role_id": role_id})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["role_id"] == role_id


# Test GET roles for a user
def test_get_roles_for_user(client):
    # Create a user and role, then assign role to the user
    client.post("/users", json={"name": "Alice", "email": "alice@example.com", "age": 26})
    client.post("/roles", json={"name": "Manager"})
    
    response_user = client.get("/users")
    response_role = client.get("/roles")
    
    user_id = response_user.json()[5]["id"]
    role_id = response_role.json()[3]["id"]
    
    client.post("/user_roles", json={"user_id": user_id, "role_id": role_id})
    
    response = client.get(f"/user_roles/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["user_id"] == user_id
    assert data[0]["role_name"] == "Manager"
'''