from fastapi.testclient import TestClient
from main import app

# Create a virtual client to send requests to our API
client = TestClient(app)

def test_pydantic_rejects_numbers_in_status():
    """Test that our regex pattern successfully blocks numbers in the status field."""
    
    # We deliberately send bad data (a number disguised as a string)
    response = client.post("/records", json={
        "status": "123", 
        "metric": 150.5
    })
    
    # We mathematically assert that the API MUST return a 422 Error
    assert response.status_code == 422

def test_pydantic_rejects_negative_metrics():
    """Test that the metric field rejects negative numbers."""
    
    response = client.post("/records", json={
        "status": "processed", 
        "metric": -50.0  # Invalid metric
    })
    
    # Again, we expect Pydantic to catch this and throw a 422 Error
    assert response.status_code == 422
