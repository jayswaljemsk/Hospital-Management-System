from flask import request
from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_required, roles_accepted, current_user
from services import DoctorService
    
service = DoctorService

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('email', type=str)
parser.add_argument('password', type=str)
parser.add_argument('specialty', type=str)
parser.add_argument('phone_number', type=str)
parser.add_argument('department_id', type=int)

class DoctorListResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self):

        response = service.get_all_doctors()
        return response

    @auth_required('token')
    @roles_required('admin')
    def post(self):

        data = parser.parse_args()

        response = service.register_doctor(data)
        return response
    
class DoctorResource(Resource):

    @auth_required('token')
    def get(self, user_id):

        if (current_user.role == 'doctor' and current_user.id != user_id):
            return {'error': 'You are not authorized to view this user.'}, 403
        response = service.get_doctor_by_id(user_id)
        return response
    
    @auth_required('token')
    @roles_accepted('admin','doctor')
    def put(self, user_id):

        data = parser.parse_args()

        if (current_user.role == 'doctor' and current_user.id != user_id):
            return {'error': 'You are not authorized to update this doctor.'}, 403

        response = service.update_doctor(user_id, data)
        return response
    
    @auth_required('token')
    @roles_accepted('admin','doctor')
    def patch(self, user_id):

        data = request.get_json()

        if (current_user.role == 'doctor' and current_user.id != user_id):
            return {'error': 'You are not authorized to update this doctor.'}, 403

        response = service.update_doctor(user_id, data)
        return response
    
    @auth_required('token')
    @roles_required('admin')
    def delete(self, user_id):

        response = service.delete_doctor(user_id)
        return response
    
class DoctorAvailabilityResource(Resource):

    @auth_required('token')
    def get(self, user_id):

        if (current_user.role == 'doctor' and current_user.id != user_id):
            return {'error': 'You are not authorized to view this doctor availability.'}, 403

        response = service.get_doctor_availability(user_id)
        return response

    @auth_required('token')
    @roles_accepted('admin','doctor')
    def put(self, user_id):

        availability_data = request.get_json()    

        if (current_user.role == 'doctor' and current_user.id != user_id):
            return {'error': 'You are not authorized to update this doctor availability.'}, 403

        response = service.update_availability(user_id, availability_data)
        return response
    