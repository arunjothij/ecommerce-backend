from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app_extensions import mongo
from datetime import datetime
from bson.objectid import ObjectId

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("", methods=["POST"])
@orders_bp.route("/", methods=["POST"])
def place_order():
    data = request.get_json(force=True)
    items = data.get("items", [])
    address = data.get("address", "")
    contact = data.get("contact", {})

    if not items:
        return jsonify({"msg": "Cart is empty"}), 400

    total = sum((i.get("price", 0) or 0) * (i.get("qty", 0) or 0) for i in items)

    order = {
        "items": items,
        "address": address,
        "contact": contact,
        "amount": total,
        "status": "created",
        "created_at": datetime.utcnow()
    }

    result = mongo.db.orders.insert_one(order)
    return jsonify({
        "orderId": str(result.inserted_id),
        "status": "created",
        "amount": total
    }), 201


@orders_bp.get("/<id>")
def get_order(id):
    try:
        order = mongo.db.orders.find_one({"_id": ObjectId(id)})
        if not order:
            return jsonify({"msg": "Order not found"}), 404
        order["_id"] = str(order["_id"])
        return jsonify(order)
    except Exception:
        return jsonify({"msg": "Invalid ID"}), 400

@orders_bp.get("/")
def list_orders():
    orders = []
    for o in mongo.db.orders.find().sort("created_at", -1):
        o["_id"] = str(o["_id"])
        orders.append(o)
    return jsonify(orders)
