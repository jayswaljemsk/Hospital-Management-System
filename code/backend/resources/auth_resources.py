from flask_restful import Resource, reqparse
from services import AuthService 

def validate_date(date_str):
    from datetime import datetime
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")
    
login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)

register_parser = reqparse.RequestParser()
register_parser.add_argument('email', type=str, required=True)
register_parser.add_argument('password', type=str, required=True)
register_parser.add_argument('name', type=str, required=True)
register_parser.add_argument('date_of_birth', type=validate_date, required=True)
register_parser.add_argument('gender', type=str, required=True)
register_parser.add_argument('phone_number', type=str, required=True)
register_parser.add_argument('address', type=str, required=True)

class LoginResource(Resource):
    def post(self):
        data = login_parser.parse_args()

        if not data.get('email') or not data.get('password'):
            return {'error': 'Email and password are required.'}, 400
             
        return AuthService.login(data)

class RegisterResource(Resource):

    def post(self):
        data = register_parser.parse_args()

        if not data.get('email') or not data.get('password'):
            return {'error': 'Email and password are required.'}, 400

        return AuthService.register(data)
    

