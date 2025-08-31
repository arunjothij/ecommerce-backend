from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app_extensions import mongo, jwt


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"msg": "User already exists"}), 400
    data["password"] = generate_password_hash(data["password"])
    mongo.db.users.insert_one(data)
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data["email"]})
    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": token})