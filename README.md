# Python-REST-API
# Inventory Management System

A Flask-based REST API with CLI interface for managing retail inventory, integrated with the [OpenFoodFacts API](https://world.openfoodfacts.org/).

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd inventory_app
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Flask server
```bash
python app.py
```
The API will be available at `http://127.0.0.1:5000`.

### 5. Run the CLI (in a separate terminal)
```bash
python cli.py
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/inventory` | Fetch all inventory items |
| GET | `/inventory/<id>` | Fetch a single item by ID |
| POST | `/inventory` | Add a new item |
| PATCH | `/inventory/<id>` | Update an existing item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/inventory/search?barcode=<barcode>` | Search OpenFoodFacts by barcode |
| GET | `/inventory/search?name=<name>` | Search OpenFoodFacts by product name |

### Example: Add an item
```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Orange Juice", "brands": "Tropicana", "quantity": 20, "price": 3.49}'
```

### Example: Update quantity
```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 75}'
```

---

## CLI Usage

Run `python cli.py` and use the numbered menu:

```
1. View all inventory items
2. View a single item by ID
3. Add a new item
4. Update an item (price / quantity)
5. Delete an item
6. Search OpenFoodFacts by barcode
7. Search OpenFoodFacts by product name
8. Exit
```

---

## Running Tests

```bash
pytest tests/
```

---

## Project Structure

```
inventory_app/
├── app.py              # Flask REST API
├── cli.py              # CLI interface
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── tests/
    └── test_app.py     # Unit tests
```
