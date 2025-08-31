from flask import Blueprint, request, jsonify
from app_extensions import mongo
from bson.objectid import ObjectId
import math

products_bp = Blueprint("products", __name__)

@products_bp.get("/categories")
def categories():
    cats = mongo.db.products.distinct("category")
    return jsonify(sorted([c for c in cats if c]))

@products_bp.get("/")
def get_all_products():
    q = request.args.get("q")
    min_price = request.args.get("minPrice", type=int)
    max_price = request.args.get("maxPrice", type=int)
    category = request.args.get("category")
    sort = request.args.get("sort")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=24, type=int)

    query = {}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}
    if category:
        query["category"] = category
    if min_price is not None or max_price is not None:
        price_cond = {}
        if min_price is not None: 
            price_cond["$gte"] = min_price
        if max_price is not None: 
            price_cond["$lte"] = max_price
        query["price"] = price_cond

    cursor = mongo.db.products.find(query)
    if sort == "price":
        cursor = cursor.sort("price", 1)
    elif sort == "new":
        cursor = cursor.sort("created_at", -1)

    # ✅ FIXED: use count_documents instead of cursor.count()
    total = mongo.db.products.count_documents(query)

    items = []
    for p in cursor.skip((page-1)*limit).limit(limit):
        p["_id"] = str(p["_id"])
        items.append(p)

    pages = max(1, math.ceil(total / limit))
    return jsonify({"items": items, "page": page, "pages": pages, "total": total})



@products_bp.get("/suggest")
def suggest():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])
    cur = mongo.db.products.find({"name": {"$regex": q, "$options": "i"}}).limit(10)
    return jsonify([{"_id": str(p["_id"]), "name": p.get("name", "")} for p in cur])

@products_bp.get("/<id>")
def get_product(id):
    product = None

    # 1) Try ObjectId lookup
    try:
        product = mongo.db.products.find_one({"_id": ObjectId(id)})
    except Exception:
        product = None

    # 2) Fallback to string _id (if seeded/imported as strings)
    if not product:
        product = mongo.db.products.find_one({"_id": id})

    if not product:
        return jsonify({"msg": "Product not found"}), 404

    # normalize for client
    if isinstance(product.get("_id"), ObjectId):
        product["_id"] = str(product["_id"])
    return jsonify(product)