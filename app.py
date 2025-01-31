from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from firebase_admin import credentials, auth, initialize_app
import os

# Initialize Flask app
app = Flask(__name__)

# Load Firebase Admin SDK
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase-adminsdk.json")
if not os.path.exists(FIREBASE_CREDENTIALS):
    raise FileNotFoundError(f"Firebase credential file '{FIREBASE_CREDENTIALS}' not found!")
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
initialize_app(cred)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:8889/tb_care_plus'
db = SQLAlchemy(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
jwt = JWTManager(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Authentication Route
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.password == data['password']:  # NOTE: Hashing required
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"username": user.username, "email": user.email})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=5500)


