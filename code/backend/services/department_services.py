from models import db, Department


class DepartmentService:

    @staticmethod
    def dept_json(department):
        dept_info = {
            'id': department.id,
            'name': department.name,
            'description': department.description,
            'doctors': [{'id': doc.user_id, 'name': doc.user.name} for doc in department.doctors]
        }
        return dept_info

    @staticmethod
    def register_department(data):
        try:
            new_department = Department(
                name=data.get('name'),
                description=data.get('description')
            )
            db.session.add(new_department)
            db.session.commit()
            return {'message': 'Department created successfully.', 'department_id': new_department.id}, 201

        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to create department: {str(e)}'}, 500

    @staticmethod
    def get_all_departments():
        departments = Department.query.all()

        if not departments:
            return {'error': 'No departments found.'}, 404

        try:
            dept_list = []
            for dept in departments:
                dept_list.append(DepartmentService.dept_json(dept))

            return {'data': dept_list, 'message': 'Departments retrieved successfully.'}, 200

        except Exception as e:
            return {'error': f'Failed to retrieve departments: {str(e)}'}, 500

    @staticmethod
    def get_department_by_id(dept_id):  
        department = Department.query.get(dept_id)
        if not department:
            return {'error': 'Department not found.'}, 404
        
        try:
            dept_data = DepartmentService.dept_json(department)

            return {'data': dept_data, 'message': 'Department retrieved successfully.'}, 200

        except Exception as e:
            return {'error': f'Failed to retrieve department: {str(e)}'}, 500

    @staticmethod
    def update_department(dept_id, data):
        department = Department.query.get(dept_id)
        if not department:
            return {'error': 'Department not found.'}, 404

        try:
            for key, value in data.items():
                if value is None:
                    continue
                setattr(department, key, value)
                
            db.session.commit()
            return {'message': 'Department updated successfully.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update department: {str(e)}'}, 500
    
    @staticmethod
    def delete_department(dept_id):
        department = Department.query.get(dept_id)

        if not department:
            return {'error': 'Department not found.'}, 404

        doctors = department.doctors

        try:
            for doctor in doctors:
                user = doctor.user
                db.session.delete(user)
            
            db.session.delete(department)
            db.session.commit()
            return {'message': 'Department deleted successfully.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete department: {str(e)}'}, 500
