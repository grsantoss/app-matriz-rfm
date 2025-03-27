import pytest
import sys
import os
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
from database import Base, get_db
from main import app
from config.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION

# Create in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    # Override dependency to use test DB
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Return test client
    with TestClient(app) as client:
        yield client
    
    # Reset dependency override
    app.dependency_overrides = {}

@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    from database import User
    
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="hashed_password"  # In a real app, this would be hashed
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def token(test_user):
    """Generate a valid JWT token for the test user"""
    payload = {
        "sub": str(test_user.id),
        "email": test_user.email,
        "name": test_user.name,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION)
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

@pytest.fixture
def authorized_client(client, token):
    """Return a client with valid authorization"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return client 