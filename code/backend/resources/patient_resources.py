from flask import request
from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_required, roles_accepted, current_user
from resources import validate_date
from services import PatientService, ExportService

service = PatientService
export_service = ExportService

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('email', type=str)
parser.add_argument('password', type=str)
parser.add_argument('active', type=bool)
parser.add_argument('date_of_birth', type=validate_date)
parser.add_argument('gender', type=str)
parser.add_argument('phone_number', type=str)
parser.add_argument('address', type=str)

class PatientListResource(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):

        response = service.get_all_patients()
        return response

class PatientResource(Resource):
    
    @auth_required('token')
    def get(self, user_id):

        if (current_user.role == 'patient' and current_user.id != user_id):
            return {'error': 'You are not authorized to view this user.'}, 403
        response = service.get_patient_by_id(user_id)
        return response
    
    @auth_required('token')
    @roles_accepted('admin','patient')
    def put(self, user_id):

        data = parser.parse_args()

        if (current_user.role == 'patient' and current_user.id != user_id):
            return {'error': 'You are not authorized to update this patient.'}, 403
        
        response = service.update_patient(user_id, data)
        return response

    @auth_required('token')
    @roles_accepted('admin','patient')
    def patch(self, user_id):

        data = request.get_json()

        if (current_user.role == 'patient' and current_user.id != user_id):
            return {'error': 'You are not authorized to update this patient.'}, 403

        response = service.update_patient(user_id, data)
        return response

    @auth_required('token')
    @roles_required('admin')
    def delete(self, user_id):

        response = service.delete_patient(user_id)
        return response

class PatientExportCSVResource(Resource):

    @auth_required('token')
    @roles_accepted('patient', 'admin')
    def post(self, user_id):
        if current_user.role == 'patient' and current_user.id != user_id:
            return {'error': 'You are not authorized to export this patient data.'}, 403

        return export_service.trigger_patient_export(user_id)

class PatientExportCSVStatusResource(Resource):

    @auth_required('token')
    @roles_accepted('patient', 'admin')
    def get(self, user_id, task_id):
        if current_user.role == 'patient' and current_user.id != user_id:
            return {'error': 'You are not authorized to view this export task.'}, 403

        return export_service.get_export_status(user_id, task_id)

class PatientExportCSVDownloadResource(Resource):

    @auth_required('token')
    @roles_accepted('patient', 'admin')
    def get(self, user_id, task_id):
        if current_user.role == 'patient' and current_user.id != user_id:
            return {'error': 'You are not authorized to download this export.'}, 403

        return export_service.download_export_file(user_id, task_id)