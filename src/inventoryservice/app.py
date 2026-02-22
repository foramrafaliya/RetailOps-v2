from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventoryservice")

# In-memory inventory
inventory_db = {
    "OLJCESPC7Z": {"id": "OLJCESPC7Z", "name": "Sunglasses", "quantity": 50, "price": 19.99},
    "66VCHSJNUP": {"id": "66VCHSJNUP", "name": "Tank Top", "quantity": 100, "price": 18.99},
    "1YMWWN1N4O": {"id": "1YMWWN1N4O", "name": "Watch", "quantity": 30, "price": 109.99},
    "L9ECAV7KIM": {"id": "L9ECAV7KIM", "name": "Loafers", "quantity": 45, "price": 89.99},
    "2ZYFJ3GM2N": {"id": "2ZYFJ3GM2N", "name": "Hairdryer", "quantity": 25, "price": 24.99},
    "0PUK6V6EV0": {"id": "0PUK6V6EV0", "name": "Candle Holder", "quantity": 60, "price": 18.99},
    "LS4PSXUNUM": {"id": "LS4PSXUNUM", "name": "Salt & Pepper Shakers", "quantity": 80, "price": 18.49},
    "9SIQT8TOJO": {"id": "9SIQT8TOJO", "name": "Bamboo Glass Jar", "quantity": 40, "price": 5.49},
    "6E92ZMYYFZ": {"id": "6E92ZMYYFZ", "name": "Mug", "quantity": 200, "price": 8.99},
}


# ================== HEALTH ==================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "inventoryservice"}), 200

@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({"status": "ready"}), 200


# ================== API ENDPOINTS ==================

@app.route("/inventory", methods=["GET"])
def get_all_inventory():
    return jsonify({"total_products": len(inventory_db), "products": list(inventory_db.values())}), 200

@app.route("/inventory/<product_id>", methods=["GET"])
def get_inventory(product_id):
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Product not found"}), 404
    logger.info(f"Inventory check: {item['name']} — {item['quantity']} in stock")
    return jsonify(item), 200

@app.route("/inventory/<product_id>/reduce", methods=["POST"])
def reduce_inventory(product_id):
    data = request.get_json()
    amount = data.get("amount", 1)
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Product not found"}), 404
    if item["quantity"] < amount:
        return jsonify({"error": "Not enough stock", "available": item["quantity"]}), 400
    item["quantity"] -= amount
    logger.info(f"Stock reduced: {item['name']} -{amount}, remaining: {item['quantity']}")
    return jsonify({"message": "Stock reduced", "product": item}), 200

@app.route("/inventory/<product_id>/update", methods=["POST"])
def update_inventory(product_id):
    data = request.get_json()
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Product not found"}), 404
    if "quantity" in data:
        item["quantity"] = data["quantity"]
    if "price" in data:
        item["price"] = data["price"]
    logger.info(f"Stock updated: {item['name']} — qty: {item['quantity']}, price: ${item['price']}")
    return jsonify({"message": "Updated", "product": item}), 200

@app.route("/inventory/<product_id>/add", methods=["POST"])
def add_stock(product_id):
    data = request.get_json()
    amount = data.get("amount", 0)
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Product not found"}), 404
    item["quantity"] += amount
    logger.info(f"Stock added: {item['name']} +{amount}, total: {item['quantity']}")
    return jsonify({"message": "Stock added", "product": item}), 200


# ================== CUSTOMER VIEW ==================

@app.route("/", methods=["GET"])
def home():
    html = """<!DOCTYPE html>
<html>
<head><title>Inventory Service</title>
<style>
    body { font-family: Arial; max-width: 800px; margin: 50px auto; background: #f5f5f5; padding: 20px; }
    .header { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    th { background: #333; color: white; padding: 12px; text-align: left; }
    td { padding: 12px; border-bottom: 1px solid #eee; }
    .in-stock { color: #4CAF50; font-weight: bold; }
    .low-stock { color: #FF9800; font-weight: bold; }
    .out-of-stock { color: #f44336; font-weight: bold; }
    .admin-link { display: inline-block; margin-top: 15px; padding: 10px 20px; background: #333; color: white; text-decoration: none; border-radius: 6px; }
    .admin-link:hover { background: #555; }
</style>
</head>
<body>
    <div class="header">
        <h1>📦 Inventory Service</h1>
        <p>Real-time Stock Management</p>
        <a href="/admin" class="admin-link">🔐 Seller Admin Panel</a>
    </div>
    <table>
        <tr><th>Product</th><th>ID</th><th>Price</th><th>Stock</th><th>Status</th></tr>"""

    for pid, item in inventory_db.items():
        qty = item["quantity"]
        if qty > 20:
            cls, status = "in-stock", "✅ In Stock"
        elif qty > 0:
            cls, status = "low-stock", "⚠️ Low Stock"
        else:
            cls, status = "out-of-stock", "❌ Out of Stock"
        html += f'<tr><td>{item["name"]}</td><td><code>{pid}</code></td><td>${item["price"]}</td><td class="{cls}">{qty}</td><td>{status}</td></tr>'

    html += "</table></body></html>"
    return html


# ================== SELLER ADMIN PANEL ==================

@app.route("/admin", methods=["GET"])
def admin_panel():
    success_msg = request.args.get("success", "")
    error_msg = request.args.get("error", "")

    html = """<!DOCTYPE html>
<html>
<head><title>Seller Admin Panel</title>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; }

    .navbar {
        background: linear-gradient(135deg, #e53935, #d32f2f);
        color: white; padding: 20px 40px;
    }
    .navbar h1 { font-size: 24px; margin-bottom: 5px; }
    .navbar p { opacity: 0.8; font-size: 14px; }
    .navbar a { color: white; margin-left: 20px; text-decoration: none; opacity: 0.8; }

    .container { max-width: 1000px; margin: 0 auto; padding: 20px; }

    .alert-success {
        background: #d4edda; color: #155724; padding: 15px;
        border-radius: 8px; margin-bottom: 15px; border: 1px solid #c3e6cb;
        font-weight: bold;
    }
    .alert-error {
        background: #f8d7da; color: #721c24; padding: 15px;
        border-radius: 8px; margin-bottom: 15px; border: 1px solid #f5c6cb;
        font-weight: bold;
    }

    .product-card {
        background: white; border-radius: 10px; padding: 20px;
        margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 15px;
    }
    .product-info h3 { color: #333; margin-bottom: 5px; }
    .product-info p { color: #888; font-size: 14px; }

    .product-stats {
        display: flex; gap: 20px; align-items: center;
    }
    .stat {
        text-align: center;
    }
    .stat-value {
        font-size: 24px; font-weight: bold; display: block;
    }
    .stat-label { font-size: 12px; color: #888; }

    .in-stock { color: #4CAF50; }
    .low-stock { color: #FF9800; }
    .out-of-stock { color: #f44336; }

    .actions { display: flex; gap: 8px; flex-wrap: wrap; }

    .action-form {
        display: flex; align-items: center; gap: 5px;
    }
    .action-form input {
        width: 70px; padding: 8px; border: 2px solid #ddd;
        border-radius: 6px; font-size: 14px; text-align: center;
    }
    .action-form input:focus { border-color: #6C63FF; outline: none; }

    .btn {
        padding: 8px 16px; border: none; border-radius: 6px;
        font-size: 13px; font-weight: bold; cursor: pointer;
        color: white;
    }
    .btn-add { background: #4CAF50; }
    .btn-add:hover { background: #45a049; }
    .btn-set { background: #2196F3; }
    .btn-set:hover { background: #1e88e5; }
    .btn-price { background: #FF9800; }
    .btn-price:hover { background: #f57c00; }

    .summary {
        background: white; border-radius: 10px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex; justify-content: space-around; text-align: center;
    }
    .summary-item { }
    .summary-value { font-size: 28px; font-weight: bold; color: #333; }
    .summary-label { font-size: 13px; color: #888; }
</style>
</head>
<body>

    <div class="navbar">
        <h1>🏪 Seller Admin Panel</h1>
        <p>Manage your inventory — Add stock, update prices</p>
        <a href="/">← Back to Inventory</a>
    </div>

    <div class="container">
    """

    # Show success/error messages
    if success_msg:
        html += f'<div class="alert-success">✅ {success_msg}</div>'
    if error_msg:
        html += f'<div class="alert-error">❌ {error_msg}</div>'

    # Summary
    total_products = len(inventory_db)
    total_stock = sum(item["quantity"] for item in inventory_db.values())
    total_value = sum(item["quantity"] * item["price"] for item in inventory_db.values())
    low_stock = sum(1 for item in inventory_db.values() if 0 < item["quantity"] <= 20)
    out_of_stock = sum(1 for item in inventory_db.values() if item["quantity"] == 0)

    html += f"""
    <div class="summary">
        <div class="summary-item">
            <div class="summary-value">{total_products}</div>
            <div class="summary-label">Total Products</div>
        </div>
        <div class="summary-item">
            <div class="summary-value">{total_stock}</div>
            <div class="summary-label">Total Stock</div>
        </div>
        <div class="summary-item">
            <div class="summary-value">${total_value:,.2f}</div>
            <div class="summary-label">Inventory Value</div>
        </div>
        <div class="summary-item">
            <div class="summary-value" style="color: #FF9800;">{low_stock}</div>
            <div class="summary-label">Low Stock</div>
        </div>
        <div class="summary-item">
            <div class="summary-value" style="color: #f44336;">{out_of_stock}</div>
            <div class="summary-label">Out of Stock</div>
        </div>
    </div>
    """

    # Product cards
    for pid, item in inventory_db.items():
        qty = item["quantity"]
        if qty > 20:
            cls = "in-stock"
        elif qty > 0:
            cls = "low-stock"
        else:
            cls = "out-of-stock"

        html += f"""
    <div class="product-card">
        <div class="product-info">
            <h3>{item["name"]}</h3>
            <p>ID: {pid}</p>
        </div>

        <div class="product-stats">
            <div class="stat">
                <span class="stat-value {cls}">{qty}</span>
                <span class="stat-label">In Stock</span>
            </div>
            <div class="stat">
                <span class="stat-value">${item["price"]}</span>
                <span class="stat-label">Price</span>
            </div>
        </div>

        <div class="actions">
            <form class="action-form" action="/admin/add-stock" method="POST">
                <input type="hidden" name="product_id" value="{pid}">
                <input type="number" name="amount" placeholder="Qty" min="1" value="10" required>
                <button type="submit" class="btn btn-add">+ Add Stock</button>
            </form>

            <form class="action-form" action="/admin/set-stock" method="POST">
                <input type="hidden" name="product_id" value="{pid}">
                <input type="number" name="quantity" placeholder="Set" min="0" value="{qty}" required>
                <button type="submit" class="btn btn-set">Set Stock</button>
            </form>

            <form class="action-form" action="/admin/set-price" method="POST">
                <input type="hidden" name="product_id" value="{pid}">
                <input type="number" name="price" placeholder="Price" min="0" step="0.01" value="{item['price']}" required>
                <button type="submit" class="btn btn-price">Set Price</button>
            </form>
        </div>
    </div>
        """

    html += """
    </div>
</body>
</html>"""
    return html


@app.route("/admin/add-stock", methods=["POST"])
def admin_add_stock():
    product_id = request.form.get("product_id")
    amount = int(request.form.get("amount", 0))

    item = inventory_db.get(product_id)
    if not item:
        return redirect_admin(error=f"Product {product_id} not found")

    item["quantity"] += amount
    logger.info(f"ADMIN: Added {amount} stock to {item['name']}. Total: {item['quantity']}")

    return redirect_admin(success=f"Added {amount} units to {item['name']}. New stock: {item['quantity']}")


@app.route("/admin/set-stock", methods=["POST"])
def admin_set_stock():
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 0))

    item = inventory_db.get(product_id)
    if not item:
        return redirect_admin(error=f"Product {product_id} not found")

    old_qty = item["quantity"]
    item["quantity"] = quantity
    logger.info(f"ADMIN: Set stock for {item['name']}: {old_qty} → {quantity}")

    return redirect_admin(success=f"Stock for {item['name']} set to {quantity} (was {old_qty})")


@app.route("/admin/set-price", methods=["POST"])
def admin_set_price():
    product_id = request.form.get("product_id")
    price = float(request.form.get("price", 0))

    item = inventory_db.get(product_id)
    if not item:
        return redirect_admin(error=f"Product {product_id} not found")

    old_price = item["price"]
    item["price"] = price
    logger.info(f"ADMIN: Price for {item['name']}: ${old_price} → ${price}")

    return redirect_admin(success=f"Price for {item['name']} updated: ${old_price} → ${price}")


def redirect_admin(success="", error=""):
    from flask import redirect
    url = "/admin?"
    if success:
        url += f"success={success}"
    if error:
        url += f"error={error}"
    return redirect(url)


if __name__ == "__main__":
    logger.info("Inventory Service starting on port 8084")
    app.run(host="0.0.0.0", port=8084)