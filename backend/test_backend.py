#backend/test_backend.py
import unittest
import os
from fastapi.testclient import TestClient

# Mock the environment variable BEFORE importing the app
os.environ["API_KEY"] = "test_secret_key"

from backend.app import app

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("model_loaded", data)

    def test_predict_unauthorized(self):
        response = self.client.post(
            "/predict",
            json={"text": "Hello world"},
            headers={"x-api-key": "wrong_key"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized: Invalid API Key")

    def test_predict_authorized(self):
        response = self.client.post(
            "/predict",
            json={"text": "This is great"},
            headers={"x-api-key": "test_secret_key"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("positive", data)
        self.assertIn("negative", data)
        self.assertIsInstance(data["positive"], float)
        self.assertIsInstance(data["negative"], float)

    def test_predict_empty_text(self):
        response = self.client.post(
            "/predict",
            json={"text": "   "},
            headers={"x-api-key": "test_secret_key"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Text cannot be empty.")

if __name__ == "__main__":
    unittest.main()
