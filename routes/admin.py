# routes/admin.py
from flask import Blueprint, request, jsonify, current_app, url_for
from app_extensions import mongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os
import cloudinary.uploader as uploader

admin_bp = Blueprint("admin", __name__)

# helper to safely remove old file if it exists
def _delete_local_file_by_url(image_url: str):
    try:
        if not image_url:
            return
        # image_url looks like http://localhost:5000/uploads/filename.jpg
        filename = image_url.rsplit("/", 1)[-1]
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass


@admin_bp.post("/products")
def create_product():
    data = request.form.to_dict()
    image_url = None

    file = request.files.get("image")  # the uploaded file
    if file:
        res = uploader.upload(file, folder="varun_store/products")
        image_url = res.get("secure_url")  # permanent hosted URL

    product = {
        "name": data.get("name"),
        "price": float(data.get("price", 0)),
        "category": data.get("category"),
        "stock": int(data.get("stock", 0)),
        "imageUrl": image_url,
        "description": data.get("description", "")
    }
    mongo.db.products.insert_one(product)
    product["_id"] = str(product["_id"])
    return jsonify({"msg": "Product created", "product": product})


@admin_bp.get("/products")
def list_products():
    docs = []
    for p in mongo.db.products.find().sort("_id", -1):
        p["_id"] = str(p["_id"])
        docs.append(p)
    return jsonify(docs)

@admin_bp.put("/products/<id>")
def update_product(id):
    data = request.form.to_dict()
    file = request.files.get("image")

    # fetch old product to know previous image
    old = mongo.db.products.find_one({"_id": ObjectId(id)})
    if not old:
        return jsonify({"msg": "Product not found"}), 404

    image_url = data.get("imageUrl", old.get("imageUrl"))
    if file:
        # replace image
        _delete_local_file_by_url(old.get("imageUrl"))
        filename = secure_filename(file.filename)
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        image_url = url_for("uploaded_file", filename=filename, _external=True)

    update = {
        "name": data.get("name", old.get("name")),
        "price": float(data.get("price", old.get("price", 0))),
        "category": data.get("category", old.get("category")),
        "stock": int(data.get("stock", old.get("stock", 0))),
        "imageUrl": image_url,
        "description": data.get("description", old.get("description", "")),
    }

    mongo.db.products.update_one({"_id": ObjectId(id)}, {"$set": update})
    return jsonify({"msg": "Product updated"})

@admin_bp.delete("/products/<id>")
def delete_product(id):
    p = mongo.db.products.find_one({"_id": ObjectId(id)})
    if not p:
        return jsonify({"msg": "Product not found"}), 404
    _delete_local_file_by_url(p.get("imageUrl"))
    mongo.db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "Product deleted"})
