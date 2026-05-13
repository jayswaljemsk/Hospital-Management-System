from services import TreatmentService
from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_accepted

service = TreatmentService

parser = reqparse.RequestParser()
parser.add_argument('tests_done', type=str)
parser.add_argument('diagnosis', type=str)
parser.add_argument('prescription', type=str)
parser.add_argument('medicines', type=str)


class TreatmentResource(Resource):
    
    @auth_required('token')
    @roles_accepted('admin', 'doctor', 'patient')
    def get(self, appointment_id):

        response = service.get_treatment(appointment_id)
        return response
    
    @auth_required('token')
    @roles_accepted('doctor')
    def put(self, appointment_id):

        data = parser.parse_args()

        response = service.update_treatment(appointment_id, data)
        return response
    
    @auth_required('token')
    @roles_accepted('patient', 'doctor')
    def delete(self, appointment_id):
        
        response = service.delete_treatment(appointment_id)
        return response

class TreatmentListResource(Resource):
    
    @auth_required('token')
    @roles_accepted('admin', 'doctor')
    def get(self):

        response = service.get_all_treatments()
        return response