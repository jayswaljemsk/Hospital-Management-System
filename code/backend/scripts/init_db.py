from flask_security import hash_password

def initialize_database(app):
    from extensions import db

    with app.app_context():
        # db.drop_all()
        db.create_all()

        datastore = app.datastore
        admin_role = datastore.find_or_create_role(name='admin', description='Administrator')
        doctor_role = datastore.find_or_create_role(name='doctor', description='Doctor')
        patient_role = datastore.find_or_create_role(name='patient', description='Patient')

        try:
            db.session.commit()
            print("roles created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing roles: {e}")
        
        if not datastore.find_user(email='admin@gmail.com'):
            admin_user = datastore.create_user(
                name='Admin',
                email='admin@gmail.com',
                password=hash_password('123'),
            )
            datastore.add_role_to_user(admin_user, admin_role)

        try:
            db.session.commit()
            print("admin created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing default users: {e}")