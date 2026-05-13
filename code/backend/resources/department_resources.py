from flask import request
from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_required, roles_accepted, current_user
from services import DepartmentService

service = DepartmentService


parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('description', type=str)
# parser.add_argument('dept_id', type=int, location='args')

class DepartmentListResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self):

        response = service.get_all_departments()
        return response
    
    @auth_required('token')
    @roles_required('admin')
    def post(self):

        data = parser.parse_args()

        response = service.register_department(data)
        return response

class DepartmentResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self, dept_id):

        response = service.get_department_by_id(dept_id)
        return response
    @auth_required('token')
    @roles_required('admin')
    def put(self, dept_id):

        data = parser.parse_args()

        response = service.update_department(dept_id, data)
        return response
    
    @auth_required('token')
    @roles_required('admin')
    def patch(self, dept_id):

        data = request.get_json()

        response = service.update_department(dept_id, data)
        return response

    @auth_required('token')
    @roles_required('admin')
    def delete(self, dept_id):
        
        response = service.delete_department(dept_id)
        return response