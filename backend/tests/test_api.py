"""
Test suite for Flask API endpoints
"""
import pytest
import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_returns_200(self):
        """Health endpoint should return 200"""
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
    
    def test_health_returns_healthy_status(self):
        """Health endpoint should return healthy status"""
        r = requests.get(f"{BASE_URL}/health")
        data = r.json()
        assert data["status"] == "healthy"


class TestModelsEndpoint:
    """Test models endpoint"""
    
    def test_models_returns_200(self):
        """Models endpoint should return 200"""
        r = requests.get(f"{BASE_URL}/api/models")
        assert r.status_code == 200
    
    def test_models_returns_dict(self):
        """Models endpoint should return models dict"""
        r = requests.get(f"{BASE_URL}/api/models")
        data = r.json()
        assert "models" in data
        assert len(data["models"]) > 0


class TestUploadEndpoint:
    """Test file upload endpoint"""
    
    def test_upload_csv_returns_200(self):
        """Upload CSV should return 200"""
        with open("data/Sample Superstore.csv", "rb") as f:
            r = requests.post(f"{BASE_URL}/api/upload", files={"file": f})
        assert r.status_code == 200
    
    def test_upload_returns_preview(self):
        """Upload should return data preview"""
        with open("data/Sample Superstore.csv", "rb") as f:
            r = requests.post(f"{BASE_URL}/api/upload", files={"file": f})
        data = r.json()
        assert "rows" in data
        assert "columns" in data
        assert "filepath" in data
        assert data["rows"] > 0
