from flask_restful import Resource, reqparse
from flask import request
from flask_security import auth_required, roles_required, roles_accepted, current_user
from models import Appointment
from services import AppointmentService
from resources import validate_date

service = AppointmentService

parser = reqparse.RequestParser()
parser.add_argument('doctor_id', type=int)
parser.add_argument('date', type=validate_date)
parser.add_argument('slot', type=str, choices=("morning", "afternoon", "evening"))
parser.add_argument('status', type=str)

class AppointmentListResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'doctor', 'patient')
    def get(self):

        response = service.get_all_appointments()
        return response
    
    @auth_required('token')
    @roles_required('patient')
    def post(self):

        data = parser.parse_args()

        response = service.create_appointment(data)
        return response

class AppointmentResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self, appointment_id):

        response = service.get_appointment_by_id(appointment_id)
        return response

    @auth_required('token')
    @roles_required('admin')
    def put(self, appointment_id):
        data = parser.parse_args()

        response = service.update_appointment(appointment_id, data)
        return response
    
    @auth_required('token')
    @roles_accepted('admin', 'patient', 'doctor')
    def patch(self, appointment_id):

        data = request.get_json() or {}

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {'error': 'Appointment not found.'}, 404

        if current_user.role == 'patient':
            if appointment.patient_id != current_user.id:
                return {'error': 'You are not authorized to update this appointment.'}, 403

            if appointment.status == 'completed':
                return {'error': 'Completed appointments cannot be cancelled.'}, 400

            if data.get('status') != 'cancelled':
                return {'error': 'Patients can only cancel appointments.'}, 400

        response = service.update_appointment(appointment_id, data)
        return response
