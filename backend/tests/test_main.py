import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)

def test_get_detections_empty(client):
    response = client.get("/api/detections")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0

def test_create_detection(client):
    # Create test image file
    test_image = "test_image.jpg"
    with open(test_image, "wb") as f:
        f.write(b"fake image content")

    try:
        # Test data
        data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "title": "Test Detection",
            "description": "Test Description"
        }
        
        # Send multipart form data with file
        with open(test_image, "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = client.post("/api/detect", data=data, files=files)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["author_name"] == "Test Author"
        assert response_data["title"] == "Test Detection"
        assert response_data["status"] == "completed"
        assert response_data["number_of_persons"] == 1  # Current dummy value

    finally:
        # Cleanup test image
        if os.path.exists(test_image):
            os.remove(test_image)

def test_get_detection_not_found(client):
    response = client.get("/api/detections/999")
    assert response.status_code == 404

def test_search_and_sort(client):
    # Create multiple detections first
    test_image = "test_image.jpg"
    with open(test_image, "wb") as f:
        f.write(b"fake image content")

    try:
        # Create two test detections
        authors = ["Alice", "Bob"]
        for author in authors:
            data = {
                "author_name": author,
                "title": f"Test by {author}"
            }
            with open(test_image, "rb") as f:
                files = {"file": ("test_image.jpg", f, "image/jpeg")}
                client.post("/api/detect", data=data, files=files)

        # Test search
        response = client.get("/api/detections", params={"search": "Alice"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["author_name"] == "Alice"

        # Test sorting
        response = client.get(
            "/api/detections",
            params={"sort_by": "author_name", "order": "desc"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["author_name"] == "Bob"

    finally:
        # Cleanup test image
        if os.path.exists(test_image):
            os.remove(test_image) 