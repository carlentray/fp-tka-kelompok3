from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timezone
import uuid
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["orderdb"]
orders_col = db["orders"]

orders_col.create_index([("created_at", DESCENDING)])
orders_col.create_index([("order_id", 1)], unique=True)

@app.route("/order", methods=["POST"])
def create_order():
    d = request.get_json() or {}
    if not d.get("product") or not d.get("quantity") or not d.get("price"):
        return jsonify({"error": "product, quantity, price wajib diisi"}), 400

    order = {
        "order_id":   str(uuid.uuid4()),
        "product":    d["product"],
        "quantity":   int(d["quantity"]),
        "price":      float(d["price"]),
        "total":      int(d["quantity"]) * float(d["price"]),
        "status":     "pending",
        "created_at": datetime.now(timezone.utc),
    }
    orders_col.insert_one(order)
    order.pop("_id", None)
    order["created_at"] = order["created_at"].isoformat()
    return jsonify(order), 201

@app.route("/order/<order_id>", methods=["GET"])
def get_order(order_id):
    doc = orders_col.find_one({"order_id": order_id}, {"_id": 0})
    if not doc:
        return jsonify({"error": "Order not found"}), 404
    doc["created_at"] = doc["created_at"].isoformat()
    return jsonify(doc)

@app.route("/orders", methods=["GET"])
def get_orders():
    docs = list(orders_col.find({}, {"_id": 0}).sort("created_at", DESCENDING))
    for d in docs:
        d["created_at"] = d["created_at"].isoformat()
    return jsonify(docs)

@app.route("/order/<order_id>", methods=["PUT"])
def update_order(order_id):
    d = request.get_json() or {}
    if not d.get("status"):
        return jsonify({"error": "status wajib diisi"}), 400

    result = orders_col.update_one(
        {"order_id": order_id},
        {"$set": {"status": d["status"]}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"order_id": order_id, "status": d["status"]})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)