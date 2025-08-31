from flask import Blueprint, jsonify
from bson.objectid import ObjectId
from app_extensions import mongo

users_bp = Blueprint("users", __name__)

@users_bp.route("/<id>", methods=["GET"])
def get_user(id):
    user = mongo.db.users.find_one({"_id": ObjectId(id)})
    if user:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        return jsonify(user)
    return jsonify({"msg": "User not found"}), 404