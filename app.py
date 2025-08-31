# app.py
from flask import Flask, request, jsonify, send_from_directory, current_app
from flask_cors import CORS
from dotenv import load_dotenv
import os
from app_extensions import mongo, jwt
import cloudinary

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure     = True
)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# === uploads config ===
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

mongo.init_app(app)
with app.app_context():
    try:
        mongo.db.command("ping")
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

jwt.init_app(app)

@app.get("/api/ping")
def ping():
    return {"ok": True}

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

# --- blueprints ---
from routes.products import products_bp
from routes.auth import auth_bp
from routes.orders import orders_bp
from routes.users import users_bp
from routes.admin import admin_bp
from routes.admin_orders import admin_orders_bp

app.register_blueprint(products_bp, url_prefix="/api/products")
app.register_blueprint(auth_bp,     url_prefix="/api/auth")
app.register_blueprint(orders_bp,   url_prefix="/api/orders")
app.register_blueprint(users_bp,    url_prefix="/api/users")
app.register_blueprint(admin_bp,    url_prefix="/api/admin")
app.register_blueprint(admin_orders_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

