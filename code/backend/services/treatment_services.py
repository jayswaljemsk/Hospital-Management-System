from models import db, Treatment
from flask_security import current_user


class TreatmentService:

    @staticmethod
    def get_all_treatments():  
        treatments = Treatment.query.all()
        treatment_list = []
        for treatment in treatments:
            treatment_list.append({
                'appointment_id': treatment.appointment_id,
                'tests_done': treatment.tests_done,
                'diagnosis': treatment.diagnosis,
                'prescription': treatment.prescription,
                'medicines': treatment.medicines
            })
        return treatment_list, 200
    
    @staticmethod
    def get_treatment(appointment_id):
        try:
            treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
            
            if not treatment:
                return {'error': 'Treatment record not found.'}, 404
                
            data = {
                'appointment_id': treatment.appointment_id,
                'tests_done': treatment.tests_done,
                'diagnosis': treatment.diagnosis,
                'prescription': treatment.prescription,
                'medicines': treatment.medicines
            }
            
            return {'data': data, 'message': 'Treatment record found.'},  200
        except Exception as e:
            return {'error': f'Failed to retrieve treatment: {str(e)}'}, 500
    
    @staticmethod
    def update_treatment(appointment_id, treatment_data):
        try:
            treatment_record = Treatment.query.filter_by(appointment_id=appointment_id).first()

            if not treatment_record:
                return {'error': 'Treatment record not found.'}, 404
            
            appointment = treatment_record.appointment
            if current_user.id != appointment.doctor_id:
                return {'error': 'Unauthorized to update this treatment.'}, 403
            
            for key, value in treatment_data.items():
                if value is None:
                    continue
                setattr(treatment_record, key, value)

            db.session.commit()
            return {'message': 'Treatment updated successfully.'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update treatment: {str(e)}'}, 500
        
    @staticmethod
    def delete_treatment(appointment_id):
        try:
            treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()

            if not treatment:
                return {'error': 'Treatment record not found.'}, 404

            db.session.delete(treatment)
            db.session.commit()
            return {'message': 'Treatment deleted successfully.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete treatment: {str(e)}'}, 500