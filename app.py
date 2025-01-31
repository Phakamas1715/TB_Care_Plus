from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, messaging
import json
import random
import string

app = Flask(__name__)
CORS(app)

# 🔹 เชื่อมต่อฐานข้อมูล MySQL ผ่าน phpMyAdmin
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:8888/TBCare"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_secret_key"

jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

# ✅ โหลด Firebase Admin SDK
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

# ✅ ฟังก์ชันสร้างรหัสสมาชิก (เช่น A123, D456, N789)
def generate_user_id(role):
    prefix = {
        "Admin": "A",
        "Doctor": "D",
        "Nurse": "N",
        "Staff": "S"
    }.get(role, "U")  # U = User ทั่วไป
    number = ''.join(random.choices(string.digits, k=3))
    return f"{prefix}{number}"

# ✅ โมเดลฐานข้อมูล
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    subdistrict = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False, default="ขอนแก่น")
    role = db.Column(db.Enum("Admin", "Doctor", "Nurse", "Staff"), nullable=False)

class DeviceToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# ✅ API สมัครสมาชิก
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(key in data for key in ("username", "email", "password", "subdistrict", "district", "province", "role")):
        return jsonify({"message": "กรุณากรอกข้อมูลให้ครบ"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "อีเมลนี้ถูกใช้ไปแล้ว"}), 400

    user_id = generate_user_id(data["role"])
    hashed_password = generate_password_hash(data["password"], method="sha256")

    new_user = User(
        user_id=user_id,
        username=data["username"],
        email=data["email"],
        password=hashed_password,
        subdistrict=data["subdistrict"],
        district=data["district"],
        province=data["province"],
        role=data["role"]
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "ลงทะเบียนสำเร็จ!", "user_id": new_user.user_id}), 201

# ✅ API ล็อกอิน
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "อีเมลหรือรหัสผ่านไม่ถูกต้อง"}), 401

    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"message": "เข้าสู่ระบบสำเร็จ!", "user_id": user.user_id, "access_token": access_token}), 200

# ✅ API ดึงข้อมูลตำบล-อำเภอ
@app.route('/api/districts', methods=['GET'])
def get_districts():
    with open("districts.json", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data), 200

# ✅ API ส่ง Push Notification
@app.route('/api/send-notification', methods=['POST'])
def send_notification():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")
    message = data.get("message")

    tokens = [t.token for t in DeviceToken.query.filter_by(user_id=user_id).all()]
    if not tokens:
        return jsonify({"message": "ไม่พบอุปกรณ์ที่ลงทะเบียน"}), 404

    notification = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=message),
        tokens=tokens,
    )

    response = messaging.send_multicast(notification)
    return jsonify({"message": "ส่งการแจ้งเตือนสำเร็จ!", "success_count": response.success_count}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5501, debug=False)
