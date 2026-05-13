from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_required, roles_accepted

from services import SearchService


search_parser = reqparse.RequestParser()
search_parser.add_argument('name', type=str, location='args')
search_parser.add_argument('department', type=str, location='args')
search_parser.add_argument('id', type=int, location='args')


class SearchDoctorResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self):
        args = search_parser.parse_args()

        name = args.get('name', None)
        department = args.get('department', None)

        return SearchService.search_doctors(name=name, department=department)
    
class SearchPatientResource(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        args = search_parser.parse_args()

        patient_id = args.get('id', None)
        name = args.get('name', None)

        return SearchService.search_patients(id=patient_id, name=name)

class SearchDepartmentResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self):
        args = search_parser.parse_args()
        name = args.get('name', None)

        return SearchService.search_departments(name=name)
