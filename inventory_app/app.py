from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Mock database — an in-memory list that simulates a real database.
# Each item mirrors the kind of data OpenFoodFacts returns.
# ---------------------------------------------------------------------------
inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "0025293004320",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt",
        "quantity": 50,
        "price": 3.99,
    },
    {
        "id": 2,
        "product_name": "Whole Grain Bread",
        "brands": "Nature's Own",
        "barcode": "0072250007321",
        "ingredients_text": "Whole wheat flour, water, yeast, salt",
        "quantity": 30,
        "price": 2.49,
    },
    {
        "id": 3,
        "product_name": "Greek Yogurt",
        "brands": "Chobani",
        "barcode": "0818290001011",
        "ingredients_text": "Cultured nonfat milk, live active cultures",
        "quantity": 80,
        "price": 1.29,
    },
]

next_id = 4  # Auto-increment counter for new items


# ---------------------------------------------------------------------------
# Helper — find an item by id; returns the item dict or None
# ---------------------------------------------------------------------------
def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)


# ---------------------------------------------------------------------------
# GET /inventory — Return all inventory items
# ---------------------------------------------------------------------------
@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify({"status": "success", "data": inventory}), 200


# ---------------------------------------------------------------------------
# GET /inventory/<id> — Return a single item by id
# ---------------------------------------------------------------------------
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"status": "error", "message": f"Item {item_id} not found"}), 404
    return jsonify({"status": "success", "data": item}), 200


# ---------------------------------------------------------------------------
# POST /inventory — Add a new item
# ---------------------------------------------------------------------------
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    body = request.get_json()

    # Validate required fields
    if not body or "product_name" not in body:
        return jsonify({"status": "error", "message": "product_name is required"}), 400

    new_item = {
        "id": next_id,
        "product_name": body.get("product_name"),
        "brands": body.get("brands", "Unknown"),
        "barcode": body.get("barcode", ""),
        "ingredients_text": body.get("ingredients_text", ""),
        "quantity": body.get("quantity", 0),
        "price": body.get("price", 0.0),
    }

    inventory.append(new_item)
    next_id += 1

    return jsonify({"status": "success", "data": new_item}), 201


# ---------------------------------------------------------------------------
# PATCH /inventory/<id> — Update selected fields of an existing item
# ---------------------------------------------------------------------------
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"status": "error", "message": f"Item {item_id} not found"}), 404

    body = request.get_json()
    if not body:
        return jsonify({"status": "error", "message": "No update data provided"}), 400

    # Only allow updating these fields
    allowed_fields = {"product_name", "brands", "barcode", "ingredients_text", "quantity", "price"}
    for key, value in body.items():
        if key in allowed_fields:
            item[key] = value

    return jsonify({"status": "success", "data": item}), 200


# ---------------------------------------------------------------------------
# DELETE /inventory/<id> — Remove an item
# ---------------------------------------------------------------------------
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"status": "error", "message": f"Item {item_id} not found"}), 404

    inventory.remove(item)
    return jsonify({"status": "success", "message": f"Item {item_id} deleted"}), 200


# ---------------------------------------------------------------------------
# GET /inventory/search?barcode=<barcode> — Fetch from OpenFoodFacts API
# and optionally add the result to the inventory
# ---------------------------------------------------------------------------
@app.route("/inventory/search", methods=["GET"])
def search_external():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    elif name:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={name}&json=1"
    else:
        return jsonify({"status": "error", "message": "Provide barcode or name query param"}), 400

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"External API error: {str(e)}"}), 502

    return jsonify({"status": "success", "data": data}), 200


# ---------------------------------------------------------------------------
# Run the app
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)