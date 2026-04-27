"""
Unit tests for the Inventory Management Flask API.
Run with: pytest tests/
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Make sure the parent directory is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, inventory


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a test client and reset inventory before each test."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset inventory to a known state before each test
        inventory.clear()
        inventory.extend([
            {
                "id": 1,
                "product_name": "Test Milk",
                "brands": "Test Brand",
                "barcode": "1234567890",
                "ingredients_text": "Water, milk",
                "quantity": 10,
                "price": 2.99,
            },
            {
                "id": 2,
                "product_name": "Test Bread",
                "brands": "Baker Co",
                "barcode": "0987654321",
                "ingredients_text": "Flour, water, yeast",
                "quantity": 5,
                "price": 1.99,
            },
        ])
        yield client


# ---------------------------------------------------------------------------
# GET /inventory — Fetch all items
# ---------------------------------------------------------------------------

class TestGetAllItems:
    def test_returns_200(self, client):
        res = client.get("/inventory")
        assert res.status_code == 200

    def test_returns_all_items(self, client):
        res = client.get("/inventory")
        data = res.get_json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2

    def test_response_shape(self, client):
        res = client.get("/inventory")
        item = res.get_json()["data"][0]
        assert "id" in item
        assert "product_name" in item
        assert "quantity" in item
        assert "price" in item


# ---------------------------------------------------------------------------
# GET /inventory/<id> — Fetch single item
# ---------------------------------------------------------------------------

class TestGetOneItem:
    def test_existing_item_returns_200(self, client):
        res = client.get("/inventory/1")
        assert res.status_code == 200

    def test_returns_correct_item(self, client):
        res = client.get("/inventory/1")
        data = res.get_json()
        assert data["data"]["product_name"] == "Test Milk"

    def test_missing_item_returns_404(self, client):
        res = client.get("/inventory/999")
        assert res.status_code == 404

    def test_404_has_error_message(self, client):
        res = client.get("/inventory/999")
        data = res.get_json()
        assert data["status"] == "error"
        assert "not found" in data["message"]


# ---------------------------------------------------------------------------
# POST /inventory — Add item
# ---------------------------------------------------------------------------

class TestAddItem:
    def test_add_item_returns_201(self, client):
        payload = {"product_name": "New Juice", "brands": "Sunny", "quantity": 15, "price": 3.0}
        res = client.post("/inventory", json=payload)
        assert res.status_code == 201

    def test_added_item_appears_in_inventory(self, client):
        payload = {"product_name": "New Juice", "brands": "Sunny"}
        client.post("/inventory", json=payload)
        all_items = client.get("/inventory").get_json()["data"]
        names = [i["product_name"] for i in all_items]
        assert "New Juice" in names

    def test_missing_product_name_returns_400(self, client):
        res = client.post("/inventory", json={"brands": "Oops"})
        assert res.status_code == 400

    def test_empty_body_returns_400(self, client):
        res = client.post("/inventory", json={})
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /inventory/<id> — Update item
# ---------------------------------------------------------------------------

class TestUpdateItem:
    def test_update_returns_200(self, client):
        res = client.patch("/inventory/1", json={"quantity": 99})
        assert res.status_code == 200

    def test_quantity_is_updated(self, client):
        client.patch("/inventory/1", json={"quantity": 99})
        res = client.get("/inventory/1")
        assert res.get_json()["data"]["quantity"] == 99

    def test_price_is_updated(self, client):
        client.patch("/inventory/1", json={"price": 9.99})
        res = client.get("/inventory/1")
        assert res.get_json()["data"]["price"] == 9.99

    def test_update_nonexistent_item_returns_404(self, client):
        res = client.patch("/inventory/999", json={"quantity": 5})
        assert res.status_code == 404

    def test_id_cannot_be_changed(self, client):
        client.patch("/inventory/1", json={"id": 999})
        res = client.get("/inventory/1")
        assert res.status_code == 200  # item still accessible at id=1


# ---------------------------------------------------------------------------
# DELETE /inventory/<id> — Delete item
# ---------------------------------------------------------------------------

class TestDeleteItem:
    def test_delete_returns_200(self, client):
        res = client.delete("/inventory/1")
        assert res.status_code == 200

    def test_item_is_removed(self, client):
        client.delete("/inventory/1")
        res = client.get("/inventory/1")
        assert res.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/inventory/999")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /inventory/search — External API (mocked)
# ---------------------------------------------------------------------------

class TestExternalSearch:
    @patch("app.requests.get")
    def test_barcode_search_returns_200(self, mock_get, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Mocked Product",
                "brands": "Mock Brand",
                "ingredients_text": "Water, sugar"
            }
        }
        mock_get.return_value = mock_response

        res = client.get("/inventory/search?barcode=1234567890")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"

    @patch("app.requests.get")
    def test_name_search_returns_200(self, mock_get, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"products": [{"product_name": "Mocked Product"}]}
        mock_get.return_value = mock_response

        res = client.get("/inventory/search?name=milk")
        assert res.status_code == 200

    def test_no_params_returns_400(self, client):
        res = client.get("/inventory/search")
        assert res.status_code == 400

    @patch("app.requests.get")
    def test_api_failure_returns_502(self, mock_get, client):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError("API down")

        res = client.get("/inventory/search?barcode=999")
        assert res.status_code == 502