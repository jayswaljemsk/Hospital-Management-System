from flask_security import hash_password, current_user
from models import Patient, User, db


class PatientService:

    @staticmethod
    def patient_json(user):

        history = []
        for appointment in user.patient.appointments:
            treatment = appointment.treatment

            if appointment.status != 'completed':
                continue

            history.append({
                'id': appointment.id,
                'date': str(appointment.date),
                'doctor_name': appointment.doctor.user.name,
                'department': appointment.doctor.department.name,
                'tests_done': treatment.tests_done ,
                'diagnosis': treatment.diagnosis ,
                'prescription': treatment.prescription ,
                'medicines': treatment.medicines 
            })

        patient_info = {
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'date_of_birth': str(user.patient.date_of_birth),
            'gender': user.patient.gender,
            'phone_number': user.patient.phone_number,
            'address': user.patient.address,
            'history': history
        }

        if current_user.role == 'admin':
            patient_info['active'] = user.active
        
        return patient_info

    @staticmethod
    def get_patient_by_id(user_id):
        try:
            patient = Patient.query.filter_by(user_id=user_id).first()

            if not patient:
                return {'error': 'Patient not found.'}, 404
            
            user = User.query.get(patient.user_id)
            patient_info = PatientService.patient_json(user)

            return {'data': patient_info, 'message': 'Patient retrieved successfully.'}, 200
        except Exception as e:
            return {'error': f'Failed to retrieve patient: {str(e)}'}, 500

    @staticmethod
    def get_all_patients():
        try:
            patients = Patient.query.all()
            patient_list = []

            for patient in patients:
                user = User.query.get(patient.user_id)
                patient_info = PatientService.patient_json(user)
                patient_list.append(patient_info)

            return {'data': patient_list, 'message': 'Patients retrieved successfully.'}, 200
        except Exception as e:
            return {'error': f'Failed to retrieve patients: {str(e)}'}, 500

    @staticmethod
    def update_patient(user_id, data):
        try:
            user = User.query.get(user_id)
            patient = Patient.query.filter_by(user_id=user_id).first()

            if not user or not patient:
                return {'error': 'Patient not found.'}, 404

            user_cols = ['name', 'email', 'password']
            patient_cols = ['date_of_birth', 'gender', 'phone_number', 'address']

            for key, value in data.items():
                if value is None:
                    continue
                if key in user_cols:
                    if key == 'password':
                        user.password = hash_password(value)
                    else:
                        setattr(user, key, value)

                elif key in patient_cols:
                    setattr(patient, key, value)

                elif key == 'active' and current_user.role == 'admin':
                    user.active = value

            db.session.commit()  
            return {'message': 'Patient updated successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update patient: {str(e)}'}, 500

    @staticmethod
    def delete_patient(user_id):
        try:
            user = User.query.get(user_id)

            if not user:
                return {'error': 'Patient not found.'}, 404

            db.session.delete(user)
            db.session.commit()
            return {'message': 'Patient deleted successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete patient: {str(e)}'}, 500