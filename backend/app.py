from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from datetime import datetime
import os
import re
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/tb_care_plus.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('TB Care Plus startup')

# Load configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///tb_care_plus.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    API_KEY = os.getenv('API_KEY', 'your-api-key-here')

app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# API Key Authentication
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == app.config['API_KEY']:
            return f(*args, **kwargs)
        return jsonify({'error': 'Invalid API key'}), 401
    return decorated

# Define Patient model with additional validation
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hn = db.Column(db.String(20), unique=True)
    id_card = db.Column(db.String(13))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    appointment_date = db.Column(db.String(50), nullable=False)
    medication_taken = db.Column(db.Boolean, default=False)
    treatment_status = db.Column(db.String(20), default='กำลังรักษา')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Patient {self.name}>'

class PatientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Patient
        include_fk = True
        load_instance = True

patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)

def validate_patient_data(data):
    errors = {}
    
    # Required fields validation
    required_fields = ['name', 'appointment_date']
    for field in required_fields:
        if not data.get(field):
            errors[field] = f'กรุณาระบุ{field}'
    
    # ID card validation
    if data.get('id_card'):
        if not re.match(r'^[0-9]{13}$', data['id_card']):
            errors['id_card'] = 'เลขบัตรประชาชนไม่ถูกต้อง'
    
    # Phone number validation
    if data.get('phone'):
        cleaned_phone = re.sub(r'[- ]', '', data['phone'])
        if not re.match(r'^[0-9]{10}$', cleaned_phone):
            errors['phone'] = 'เบอร์โทรศัพท์ไม่ถูกต้อง'
    
    # HN validation (if provided)
    if data.get('hn'):
        if Patient.query.filter(Patient.hn == data['hn']).first():
            errors['hn'] = 'HN นี้มีอยู่ในระบบแล้ว'
    
    # Treatment status validation
    valid_statuses = ['กำลังรักษา', 'รักษาหาย', 'ย้ายโรงพยาบาล', 'เสียชีวิต']
    if data.get('treatment_status') and data['treatment_status'] not in valid_statuses:
        errors['treatment_status'] = 'สถานะการรักษาไม่ถูกต้อง'

    return errors

@app.route('/patients', methods=['GET'])
@require_api_key
def get_patients():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Limit max per_page
        search = request.args.get('search', '')
        status = request.args.get('status', '')

        query = Patient.query

        if search:
            search = f"%{search}%"
            query = query.filter(
                db.or_(
                    Patient.name.ilike(search),
                    Patient.hn.ilike(search),
                    Patient.id_card.ilike(search),
                    Patient.phone.ilike(search)
                )
            )

        if status:
            query = query.filter(Patient.treatment_status == status)

        # Order by created_at descending
        query = query.order_by(Patient.created_at.desc())

        patients = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'patients': patients_schema.dump(patients.items),
            'total': patients.total,
            'page': patients.page,
            'per_page': patients.per_page,
            'total_pages': patients.pages
        })

    except Exception as e:
        app.logger.error(f'Error getting patients: {str(e)}')
        return jsonify({'error': 'เกิดข้อผิดพลาดในการดึงข้อมูล'}), 500

@app.route('/patients', methods=['POST'])
@require_api_key
def add_patient():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'ไม่พบข้อมูลที่ส่งมา'}), 400

        # Validate data
        errors = validate_patient_data(data)
        if errors:
            return jsonify({
                'error': 'ข้อมูลไม่ถูกต้อง',
                'details': errors
            }), 400

        new_patient = Patient(
            name=data['name'],
            hn=data.get('hn'),
            id_card=data.get('id_card'),
            phone=data.get('phone'),
            address=data.get('address'),
            appointment_date=data['appointment_date'],
            medication_taken=data.get('medication_taken', False),
            treatment_status=data.get('treatment_status', 'กำลังรักษา'),
            notes=data.get('notes')
        )

        db.session.add(new_patient)
        db.session.commit()

        app.logger.info(f'New patient added: {new_patient.name}')
        return jsonify({
            'message': 'เพิ่มข้อมูลผู้ป่วยสำเร็จ',
            'patient': patient_schema.dump(new_patient)
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding patient: {str(e)}')
        return jsonify({'error': 'เกิดข้อผิดพลาดในการเพิ่มข้อมูล'}), 500

@app.route('/patients/<int:patient_id>', methods=['PUT'])
@require_api_key
def update_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'ไม่พบข้อมูลที่ต้องการแก้ไข'}), 400

        # Validate data
        errors = validate_patient_data(data)
        if errors:
            return jsonify({
                'error': 'ข้อมูลไม่ถูกต้อง',
                'details': errors
            }), 400

        # Update fields
        for field in ['name', 'hn', 'id_card', 'phone', 'address', 
                     'appointment_date', 'medication_taken', 'treatment_status', 'notes']:
            if field in data:
                setattr(patient, field, data[field])

        db.session.commit()
        app.logger.info(f'Patient updated: {patient.name}')

        return jsonify({
            'message': 'แก้ไขข้อมูลผู้ป่วยสำเร็จ',
            'patient': patient_schema.dump(patient)
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating patient: {str(e)}')
        return jsonify({'error': 'เกิดข้อผิดพลาดในการแก้ไขข้อมูล'}), 500

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
@require_api_key
def delete_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        
        app.logger.info(f'Patient deleted: {patient.name}')
        return jsonify({'message': 'ลบข้อมูลผู้ป่วยสำเร็จ'})

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting patient: {str(e)}')
        return jsonify({'error': 'เกิดข้อผิดพลาดในการลบข้อมูล'}), 500

# Global error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {request.url}')
    return jsonify({'error': 'ไม่พบข้อมูลที่ต้องการ'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'เกิดข้อผิดพลาดในระบบ'}), 500

if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    with app.app_context():
        db.create_all()
    
    app.run(debug=False)  # Set debug=False in production


