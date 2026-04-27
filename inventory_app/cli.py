#!/usr/bin/env python3
"""
CLI tool for interacting with the Inventory Management REST API.
Make sure app.py is running before using this tool:
    python app.py
"""

import sys
import requests

BASE_URL = "http://127.0.0.1:5000/inventory"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_item(item):
    print(f"""
  ID        : {item['id']}
  Name      : {item['product_name']}
  Brand     : {item['brands']}
  Barcode   : {item['barcode']}
  Quantity  : {item['quantity']}
  Price     : ${item['price']:.2f}
  Ingredients: {item['ingredients_text']}
""")


def print_menu():
    print("""
========================================
   Inventory Management System - CLI
========================================
  1. View all inventory items
  2. View a single item by ID
  3. Add a new item
  4. Update an item (price / quantity)
  5. Delete an item
  6. Search OpenFoodFacts by barcode
  7. Search OpenFoodFacts by product name
  8. Exit
----------------------------------------""")


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def view_all():
    try:
        res = requests.get(BASE_URL)
        data = res.json()
        items = data.get("data", [])
        if not items:
            print("  No items in inventory.")
            return
        print(f"\n  Found {len(items)} item(s):\n")
        for item in items:
            print_item(item)
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect. Is app.py running?")


def view_one():
    item_id = input("  Enter item ID: ").strip()
    try:
        res = requests.get(f"{BASE_URL}/{item_id}")
        if res.status_code == 404:
            print(f"  Item {item_id} not found.")
            return
        print_item(res.json()["data"])
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect.")


def add_item():
    print("  Enter item details (press Enter to skip optional fields):\n")
    product_name = input("  Product name (required): ").strip()
    if not product_name:
        print("  Product name is required.")
        return
    brands = input("  Brand: ").strip() or "Unknown"
    barcode = input("  Barcode: ").strip()
    ingredients = input("  Ingredients: ").strip()
    quantity = input("  Quantity [0]: ").strip()
    price = input("  Price [0.00]: ").strip()

    payload = {
        "product_name": product_name,
        "brands": brands,
        "barcode": barcode,
        "ingredients_text": ingredients,
        "quantity": int(quantity) if quantity.isdigit() else 0,
        "price": float(price) if price else 0.0,
    }

    try:
        res = requests.post(BASE_URL, json=payload)
        if res.status_code == 201:
            print("  ✓ Item added successfully!")
            print_item(res.json()["data"])
        else:
            print(f"  Error: {res.json().get('message')}")
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect.")


def update_item():
    item_id = input("  Enter item ID to update: ").strip()
    print("  Enter new values (press Enter to skip):\n")

    updates = {}
    quantity = input("  New quantity: ").strip()
    price = input("  New price: ").strip()

    if quantity.isdigit():
        updates["quantity"] = int(quantity)
    if price:
        try:
            updates["price"] = float(price)
        except ValueError:
            print("  Invalid price — skipping.")

    if not updates:
        print("  No changes provided.")
        return

    try:
        res = requests.patch(f"{BASE_URL}/{item_id}", json=updates)
        if res.status_code == 200:
            print("  ✓ Item updated!")
            print_item(res.json()["data"])
        elif res.status_code == 404:
            print(f"  Item {item_id} not found.")
        else:
            print(f"  Error: {res.json().get('message')}")
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect.")


def delete_item():
    item_id = input("  Enter item ID to delete: ").strip()
    confirm = input(f"  Are you sure you want to delete item {item_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return
    try:
        res = requests.delete(f"{BASE_URL}/{item_id}")
        if res.status_code == 200:
            print(f"  ✓ Item {item_id} deleted.")
        elif res.status_code == 404:
            print(f"  Item {item_id} not found.")
        else:
            print(f"  Error: {res.json().get('message')}")
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect.")


def search_by_barcode():
    barcode = input("  Enter barcode: ").strip()
    try:
        res = requests.get(f"{BASE_URL}/search", params={"barcode": barcode})
        data = res.json().get("data", {})
        product = data.get("product", {})
        if not product:
            print("  No product found for that barcode.")
            return
        print(f"""
  Result from OpenFoodFacts:
  Name       : {product.get('product_name', 'N/A')}
  Brand      : {product.get('brands', 'N/A')}
  Ingredients: {product.get('ingredients_text', 'N/A')[:80]}...
""")
        add = input("  Add this product to inventory? (y/n): ").strip().lower()
        if add == "y":
            quantity = input("  Enter quantity: ").strip()
            price = input("  Enter price: ").strip()
            payload = {
                "product_name": product.get("product_name", "Unknown"),
                "brands": product.get("brands", "Unknown"),
                "barcode": barcode,
                "ingredients_text": product.get("ingredients_text", ""),
                "quantity": int(quantity) if quantity.isdigit() else 0,
                "price": float(price) if price else 0.0,
            }
            r = requests.post(BASE_URL, json=payload)
            if r.status_code == 201:
                print("  ✓ Added to inventory!")
                print_item(r.json()["data"])
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect.")


def search_by_name():
    name = input("  Enter product name to search: ").strip()
    try:
        res = requests.get(f"{BASE_URL}/search", params={"name": name})
        data = res.json().get("data", {})
        products = data.get("products", [])
        if not products:
            print("  No products found.")
            return
        print(f"\n  Top results for '{name}':\n")
        for i, p in enumerate(products[:5], 1):
            print(f"  {i}. {p.get('product_name', 'N/A')} — {p.get('brands', 'N/A')}")
    except requests.exceptions.ConnectionError:
        print("  ERROR: Could not connect.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    actions = {
        "1": view_all,
        "2": view_one,
        "3": add_item,
        "4": update_item,
        "5": delete_item,
        "6": search_by_barcode,
        "7": search_by_name,
    }

    while True:
        print_menu()
        choice = input("  Choose an option (1-8): ").strip()

        if choice == "8":
            print("\n  Goodbye!\n")
            sys.exit(0)
        elif choice in actions:
            actions[choice]()
        else:
            print("  Invalid choice. Please enter 1-8.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()