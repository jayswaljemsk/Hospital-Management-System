from flask import Blueprint
from flask_restful import Api

from .auth_resources import LoginResource, RegisterResource, validate_date
from .doctor_resources import DoctorListResource, DoctorResource, DoctorAvailabilityResource
from .department_resources import DepartmentListResource, DepartmentResource
from .patient_resources import 	PatientListResource, PatientResource, PatientExportCSVResource, PatientExportCSVStatusResource, PatientExportCSVDownloadResource
from .appointment_resources import AppointmentListResource, AppointmentResource
from .treatment_resources import TreatmentResource, TreatmentListResource
from .search_resources import SearchDoctorResource, SearchPatientResource, SearchDepartmentResource

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')
api = Api(api_bp)

api.add_resource(LoginResource, '/login')
api.add_resource(RegisterResource, '/register')

api.add_resource(PatientListResource, '/patients')
api.add_resource(PatientResource, '/patients/<int:user_id>')
api.add_resource(PatientExportCSVResource, '/patients/<int:user_id>/export-csv')
api.add_resource(PatientExportCSVStatusResource, '/patients/<int:user_id>/export-csv/<string:task_id>')
api.add_resource(PatientExportCSVDownloadResource, '/patients/<int:user_id>/export-csv/<string:task_id>/download')
api.add_resource(SearchPatientResource, '/patients/search')

api.add_resource(DoctorListResource, '/doctors')
api.add_resource(DoctorResource, '/doctors/<int:user_id>')
api.add_resource(DoctorAvailabilityResource, '/doctors/<int:user_id>/availability')
api.add_resource(SearchDoctorResource, '/doctors/search')

api.add_resource(DepartmentListResource, '/departments')
api.add_resource(DepartmentResource, '/departments/<int:dept_id>')
api.add_resource(SearchDepartmentResource, '/departments/search')

api.add_resource(AppointmentListResource, '/appointments')
api.add_resource(AppointmentResource, '/appointments/<int:appointment_id>')

api.add_resource(TreatmentListResource, '/treatments')
api.add_resource(TreatmentResource, '/treatments/<int:appointment_id>')
