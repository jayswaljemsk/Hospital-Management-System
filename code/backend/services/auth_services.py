from flask import current_app as app
from flask_security import hash_password, verify_password

from models import Patient, User, db

class AuthService:

    @staticmethod
    def login(data):
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and verify_password(password, user.password):
            if not user.active:
                return {'error': 'Your account has been blocked. Please contact admin.'}, 403

            auth_token = user.get_auth_token()
            return {
                'message': 'Login successful.',
                'user_id': user.id,
                'access_token': auth_token,
                'role': user.role,
                'name': user.name
            }, 200
        else:
            return {'error': 'Invalid email or password.'}, 401

    @staticmethod
    def register(data):
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender')
        phone_number = data.get('phone_number')
        address = data.get('address')

        if User.query.filter_by(email=email).first():
            return {'error': 'Email already registered.'}, 400

        datastore = app.datastore
        try:
            new_user = datastore.create_user(name=name, email=email, password=hash_password(password))
            datastore.add_role_to_user(new_user, 'patient')
            db.session.flush()

            new_patient = Patient(
                user_id=new_user.id,
                date_of_birth=date_of_birth,
                gender=gender,
                phone_number=phone_number,
                address=address
            )
            db.session.add(new_patient)
            db.session.commit()
            return {'message': 'Registration successful.', 'user_id': new_user.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Registration failed: {e}'}, 500