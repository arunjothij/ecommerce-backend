from flask import Blueprint, jsonify, request
from app_extensions import mongo
from bson.objectid import ObjectId

admin_orders_bp = Blueprint("admin_orders", __name__, url_prefix="/api/admin/orders")

# ✅ Get all orders
@admin_orders_bp.get("/")
def list_orders():
    orders = []
    for o in mongo.db.orders.find().sort("created_at", -1):
        o["_id"] = str(o["_id"])
        orders.append(o)
    return jsonify(orders)

# ✅ Update order status (e.g., mark as delivered)
@admin_orders_bp.put("/<id>")
def update_order(id):
    new_status = request.json.get("status")
    if new_status not in ["created", "processing", "shipped", "delivered", "cancelled"]:
        return jsonify({"msg": "Invalid status"}), 400

    result = mongo.db.orders.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": new_status}}
    )

    if result.matched_count == 0:
        return jsonify({"msg": "Order not found"}), 404

    return jsonify({"msg": "Order updated", "status": new_status})
