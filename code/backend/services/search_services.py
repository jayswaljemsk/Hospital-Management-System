from models import Doctor, Department, Patient, User
from services.doctor_services import DoctorService
from services.patient_services import PatientService


class SearchService:

    @staticmethod
    def search_doctors(name, department):
        try:
            query = Doctor.query.join(User).join(Department)
            filters = []

            if name:
                filters.append(User.name.ilike(f"%{name}%"))

            if department:
                filters.append(Department.name.ilike(f"%{department}%"))

            if filters:
                query = query.filter(*filters)

            doctors = query.all()

            doctor_list = []
            for doctor in doctors:
                doctor_list.append(DoctorService.doctor_json(doctor.user))

            return {
                'data': doctor_list,
                'message': 'Doctor search completed successfully.'
            }, 200

        except Exception as e:
            return {'error': f'Failed to search doctors: {str(e)}'}, 500

    @staticmethod
    def search_patients(id, name):
        try:
            query = Patient.query.join(User)
            filters = []

            if id:
                filters.append(Patient.user_id == id)

            if name:
                filters.append(User.name.ilike(f"%{name}%"))

            if filters:
                query = query.filter(*filters)
            patients = query.all()

            patient_list = []
            for patient in patients:
                patient_list.append(PatientService.patient_json(patient.user))

            return {
                'data': patient_list,
                'message': 'Patient search completed successfully.'
            }, 200

        except Exception as e:
            return {'error': f'Failed to search patients: {str(e)}'}, 500