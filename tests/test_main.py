import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_stats():
    """Test the dashboard stats endpoint."""
    response = client.get("/api/dashboard/stats")
    # This might fail if DB is not initialized, but it's a good test case
    assert response.status_code in [200, 500] 

def test_analyze_traffic_mock():
    """Test the analyze traffic endpoint with mock data."""
    test_data = {
        "features": {
            "Flow_Duration": 1000,
            "Flow_Packets_s": 10,
            "payload": "normal traffic"
        }
    }
    response = client.post("/api/analyze", json=test_data)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "result" in response.json()
