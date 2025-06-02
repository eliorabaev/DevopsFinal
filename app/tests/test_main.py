import pytest
from fastapi.testclient import TestClient
from main import app, url_database

# Create test client
client = TestClient(app)


def setup_function():
    """Clear database before each test"""
    url_database.clear()


class TestURLShortener:

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "URL Shortener Service" in response.json()["message"]

    def test_shorten_url_basic(self):
        """Test basic URL shortening"""
        url_data = {"url": "https://www.google.com"}
        response = client.post("/shorten", json=url_data)

        assert response.status_code == 200
        data = response.json()
        assert "short_url" in data
        assert "short_code" in data
        assert data["original_url"] == "https://www.google.com/"
        assert len(data["short_code"]) == 6  # default length

    def test_shorten_url_custom_code(self):
        """Test URL shortening with custom code"""
        url_data = {"url": "https://www.github.com", "custom_code": "github"}
        response = client.post("/shorten", json=url_data)

        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == "github"
        assert data["original_url"] == "https://www.github.com/"

    def test_shorten_url_duplicate_custom_code(self):
        """Test error when using duplicate custom code"""
        url_data = {"url": "https://www.example.com", "custom_code": "test"}

        # First request should succeed
        response1 = client.post("/shorten", json=url_data)
        assert response1.status_code == 200

        # Second request with same custom code should fail
        response2 = client.post("/shorten", json=url_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_redirect_valid_code(self):
        """Test redirecting with valid short code"""
        # First create a shortened URL
        url_data = {"url": "https://www.python.org", "custom_code": "python"}
        create_response = client.post("/shorten", json=url_data)
        assert create_response.status_code == 200

        # Then test redirect
        redirect_response = client.get("/python", allow_redirects=False)
        assert redirect_response.status_code == 301
        assert redirect_response.headers["location"] == "https://www.python.org/"

    def test_redirect_invalid_code(self):
        """Test redirecting with invalid short code"""
        response = client.get("/nonexistent", allow_redirects=False)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "urls_created_total" in response.text
        assert "redirects_total" in response.text

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_urls" in data
        assert "total_redirects" in data
        assert "total_urls_created" in data

    def test_invalid_url_format(self):
        """Test error handling for invalid URL format"""
        url_data = {"url": "not-a-valid-url"}
        response = client.post("/shorten", json=url_data)
        assert response.status_code == 422  # Validation error

    def test_metrics_increment(self):
        """Test that metrics are properly incremented"""
        # Get initial stats
        initial_stats = client.get("/stats").json()

        # Create a URL
        url_data = {"url": "https://www.example.com"}
        client.post("/shorten", json=url_data)

        # Check stats increased
        new_stats = client.get("/stats").json()
        assert (
            new_stats["total_urls_created"] == initial_stats["total_urls_created"] + 1
        )
        assert new_stats["total_urls"] == initial_stats["total_urls"] + 1


if __name__ == "__main__":
    pytest.main([__file__])
