import os
import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import firebase_admin
from firebase_admin import credentials, auth

# ✅ ตั้งค่าแอป Flask
app = Flask(__name__)

# ✅ ตั้งค่าฐานข้อมูล SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://username:password@localhost/db_name"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ✅ ตั้งค่า JWT
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"
jwt = JWTManager(app)

# ✅ ค้นหาไฟล์ Firebase Admin SDK JSON
json_filename = "tb-care-plus-firebase-adminsdk-fbsvc-ca36e00a1a.json"
json_path = os.path.join(os.path.expanduser("~"), "Downloads", json_filename)

print(f"📂 Checking for Firebase JSON file at: {json_path}")

if os.path.exists(json_path):
    print("✅ Firebase credentials loaded from JSON file!")
    firebase_cred = credentials.Certificate(json_path)
elif os.getenv("FIREBASE_CREDENTIALS"):
    print("✅ Firebase credentials loaded from Environment Variables!")
    firebase_cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
else:
    raise FileNotFoundError(f"❌ ERROR: ไม่พบไฟล์ '{json_filename}' และไม่มี Environment Variable ที่กำหนด!")

# ✅ เริ่มต้น Firebase Admin SDK
firebase_admin.initialize_app(firebase_cred)
print("🚀 Firebase Admin SDK Initialized Successfully!")

# ✅ ตัวอย่าง Model ฐานข้อมูล
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# ✅ API ทดสอบ
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🚀 TB Care Plus API is running!"})

# ✅ API ลงทะเบียนผู้ใช้
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"message": "User created successfully!", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ✅ API ล็อกอิน
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth.get_user_by_email(email)
        return jsonify({"message": "Login successful!", "uid": user.uid})
    except Exception as e:
        return jsonify({"error": "Invalid credentials!"}), 401

# ✅ รันเซิร์ฟเวอร์
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

