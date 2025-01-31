import os
import base64
import cv2
import numpy as np
import dlib
import random
import string
from datetime import datetime
import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ==============================
# 🔹 ตั้งค่าแอป & ฐานข้อมูล
# ==============================
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:8889/tb_care"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")

jwt = JWTManager(app)
db = SQLAlchemy(app)

# ✅ ฟังก์ชันช่วยสร้างรหัสสมาชิกอัตโนมัติ
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
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("Admin", "Doctor", "Nurse", "Staff"), nullable=False)
    subdistrict = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False, default="ขอนแก่น")
    face_image = db.Column(db.Text, nullable=True)

# ✅ ตั้งค่า AI Face Recognition
detector = dlib.get_frontal_face_detector()

def decode_base64_image(encoded_data):
    try:
        img_data = base64.b64decode(encoded_data)
        np_arr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except:
        return None

def face_match(known_face, unknown_face):
    try:
        known_img = decode_base64_image(known_face)
        unknown_img = decode_base64_image(unknown_face)
        
        if known_img is None or unknown_img is None:
            return False

        known_faces = detector(known_img)
        unknown_faces = detector(unknown_img)
        
        return len(known_faces) > 0 and len(unknown_faces) > 0
    except:
        return False

# ==============================
# 🔹 API Routes
# ==============================

# ✅ API สมัครสมาชิก
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not all(key in data for key in ("name", "email", "password", "role", "subdistrict", "district", "province")):
            return jsonify({"message": "กรุณากรอกข้อมูลให้ครบ"}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"message": "อีเมลนี้ถูกใช้ไปแล้ว"}), 400

        user_id = generate_user_id(data["role"])
        hashed_password = generate_password_hash(data["password"], method="sha256")
        face_image_base64 = data.get("face_image")

        new_user = User(
            user_id=user_id,
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            password=hashed_password,
            role=data["role"],
            subdistrict=data["subdistrict"],
            district=data["district"],
            province=data["province"],
            face_image=face_image_base64
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "ลงทะเบียนสำเร็จ!", "userID": user_id}), 201
    except Exception as e:
        return jsonify({"message": "เกิดข้อผิดพลาด!", "error": str(e)}), 500

# ✅ API ล็อกอิน
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(user_id=data["user_id"]).first()

        if not user or not check_password_hash(user.password, data["password"]):
            return jsonify({"message": "รหัสผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"}), 401

        if "face_image" in data and user.face_image:
            if not face_match(user.face_image, data["face_image"]):
                return jsonify({"message": "การตรวจสอบใบหน้าล้มเหลว"}), 403
        
        access_token = create_access_token(identity={"id": user.user_id, "role": user.role})
        return jsonify({"message": "เข้าสู่ระบบสำเร็จ!", "userID": user.user_id, "role": user.role, "access_token": access_token}), 200
    except Exception as e:
        return jsonify({"message": "เกิดข้อผิดพลาด!", "error": str(e)}), 500

# ✅ API ดึงข้อมูลตำบล-อำเภอ
@app.route('/api/districts', methods=['GET'])
def get_districts():
    with open("districts.json", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data), 200

# ==============================
# 🔹 เริ่มต้นระบบ
# ==============================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ ฐานข้อมูลถูกสร้างสำเร็จแล้ว!")
    app.run(host="0.0.0.0", port=5500, debug=True)
