from flask import current_app as app
from datetime import date, timedelta
from models import DoctorAvailability, db, User, Doctor, Appointment, Treatment
from flask_security import hash_password, current_user


class DoctorService:

    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    SLOTS = ["morning", "afternoon", "evening"]

    @staticmethod
    def _normalize_availability_for_today(availability_dict):
        if not isinstance(availability_dict, dict):
            return {
                day: {slot: (False if day == 'Sunday' else True) for slot in DoctorService.SLOTS}
                for day in DoctorService.WEEKDAYS
            }, True

        today_name = date.today().strftime('%A')
        today_index = DoctorService.WEEKDAYS.index(today_name)
        changed = False

        normalized = {
            day: (dict(availability_dict.get(day, {})) if isinstance(availability_dict.get(day, {}), dict) else {})
            for day in DoctorService.WEEKDAYS
        }

        for day in DoctorService.WEEKDAYS:
            if day not in availability_dict:
                changed = True
            for slot in DoctorService.SLOTS:
                if slot not in normalized[day]:
                    normalized[day][slot] = False if day == 'Sunday' else True
                    changed = True

        for index, day in enumerate(DoctorService.WEEKDAYS):
            if day == 'Sunday':
                for slot in DoctorService.SLOTS:
                    if normalized[day][slot] is not False:
                        normalized[day][slot] = False
                        changed = True
                continue

            if index < today_index:
                for slot in DoctorService.SLOTS:
                    if normalized[day][slot] is not True:
                        normalized[day][slot] = True
                        changed = True

        return normalized, changed

    @staticmethod
    def doctor_json(user):
        doctor_info = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'specialty': user.doctor.specialty,
            'phone_number': user.doctor.phone_number,
            'department': user.doctor.department.name,
        }
        if current_user.role == 'admin':
            doctor_info['active'] = user.active
        return doctor_info

    @staticmethod
    def register_doctor(data):
        try:
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            specialty = data.get('specialty')
            phone_number = data.get('phone_number')
            department_id = data.get('department_id')

            datastore = app.datastore

            new_user = datastore.create_user(
                name=name, 
                email=email, 
                password=hash_password(password)
            )
            
            datastore.add_role_to_user(new_user, 'doctor')

            db.session.flush()  # Ensure new_user.id is available

            new_doctor = Doctor(
                user_id=new_user.id,
                specialty=specialty,
                phone_number=phone_number,
                department_id=department_id
            )

            avail_dict = {
                "Monday": {"morning": True, "afternoon": True, "evening": True},
                "Tuesday": {"morning": True, "afternoon": True, "evening": True},
                "Wednesday": {"morning": True, "afternoon": True, "evening": True},
                "Thursday": {"morning": True, "afternoon": True, "evening": True},
                "Friday": {"morning": True, "afternoon": True, "evening": True},
                "Saturday": {"morning": True, "afternoon": True, "evening": True},
                "Sunday": {"morning": False, "afternoon": False, "evening": False}
            }

            new_availability = DoctorAvailability(
                doctor_id=new_doctor.user_id,
                availability=avail_dict
            )

            db.session.add(new_doctor)
            db.session.add(new_availability)
            db.session.commit()
            return {'message': 'Doctor registration successful.', 'user_id': new_user.id}, 201

        except Exception as e:
            db.session.rollback()
            return {'error': f'Registration failed: {str(e)}'}, 500

    @staticmethod
    def get_doctor_by_id(user_id):
        try:
            doctor = Doctor.query.filter_by(user_id=user_id).first()

            if not doctor:
                return {'error': 'Doctor not found.'}, 404
                    
            user = User.query.get(doctor.user_id)
            doc_info = DoctorService.doctor_json(user)

            return {'data': doc_info, 'message': 'Doctor retrieved successfully.'}, 200

        except Exception as e:
            return {'error': f'Failed to retrieve doctor: {str(e)}'}, 500

    @staticmethod
    def get_all_doctors():
        try:
            doctors = Doctor.query.all()
            doctor_list = []

            for doc in doctors:
                user = User.query.get(doc.user_id)
                doc_info = DoctorService.doctor_json(user)
                doctor_list.append(doc_info)

            if not doctor_list:
                return {'error': 'No doctors found.'}, 404

            return {'data': doctor_list, 'message': 'Doctors retrieved successfully.'}, 200

        except Exception as e:
            return {'error': f'Failed to retrieve doctors: {str(e)}'}, 500

    @staticmethod
    def get_doctor_availability(user_id):
        try:
            availability_record = DoctorAvailability.query.filter_by(doctor_id=user_id).first()
            
            if not availability_record:
                return {'error': 'Doctor availability record not found.'}, 404

            normalized_availability, changed = DoctorService._normalize_availability_for_today(
                availability_record.availability
            )
            if changed:
                availability_record.availability = normalized_availability
                db.session.commit()

            availability_data = {
                day: dict(day_slots) if isinstance(day_slots, dict) else {}
                for day, day_slots in availability_record.availability.items()
            }

            today = date.today()
            window_end = today + timedelta(days=6)
            booked_appointments = Appointment.query.filter(
                Appointment.doctor_id == user_id,
                Appointment.status == 'booked',
                Appointment.date >= today,
                Appointment.date <= window_end,
            ).all()

            for appointment in booked_appointments:
                appointment_day = appointment.date.strftime('%A')
                if appointment_day in availability_data and appointment.slot in availability_data[appointment_day]:
                    availability_data[appointment_day][appointment.slot] = False

            data = {}
            data["availability"] = availability_data


            return {'data': data, 'message': 'Availability retrieved successfully.'}, 200
        
        except Exception as e:
            return {'error': f'Failed to retrieve availability: {str(e)}'}, 500

    @staticmethod
    def update_doctor(user_id, data):
        try:
            user = User.query.get(user_id)
            doctor = Doctor.query.filter_by(user_id=user_id).first()

            if not user or not doctor:
                return {'error': 'Doctor not found.'}, 404

            user_cols = ['name', 'email', 'password']
            doctor_cols = ['specialty', 'phone_number', 'department_id']

            for key, value in data.items():
                if value is None:
                    continue
                if key in user_cols:
                    if key == 'password':
                        if isinstance(value, str) and value.strip():
                            user.password = hash_password(value)
                    else:
                        setattr(user, key, value)

                elif key in doctor_cols:
                    setattr(doctor, key, value)
                    
                elif key == 'active' and current_user.role == 'admin':
                    user.active = value

            db.session.commit()
            return {'message': 'Doctor updated successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update doctor: {str(e)}'}, 500

    @staticmethod
    def update_availability(user_id, availability_data):
        try:
            doctor = Doctor.query.filter_by(user_id=user_id).first()
            
            if not doctor:
                return {'error': 'Doctor not found.'}, 404
            
            availability_record = DoctorAvailability.query.filter_by(doctor_id=user_id).first()
            
            if not availability_record:
                return {'error': 'Doctor availability record not found.'}, 404

            normalized_availability, _ = DoctorService._normalize_availability_for_today(availability_data)
            availability_record.availability = normalized_availability
            
            db.session.commit()
            return {'message': 'Availability updated successfully.', 'data': availability_record.availability}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update availability: {str(e)}'}, 500
    
    @staticmethod
    def update_treatment(appointment_id, treatment_data):
        try:
            treatment_record = Treatment.query.join(Appointment).filter(Appointment.id==appointment_id).first()
            
            if not treatment_record:
                return {'error': 'Treatment record not found.'}, 404
            
            for key, value in treatment_data.items():
                if value is None:
                    continue
                setattr(treatment_record, key, value)

            db.session.commit()
            return {'message': 'Treatment updated successfully.'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update treatment: {str(e)}'}, 500

    @staticmethod
    def delete_doctor(user_id):
        try:
            user = User.query.get(user_id)

            if not user:
                return {'error': 'Doctor not found.'}, 404

            db.session.delete(user)
            db.session.commit()
            return {'message': 'Doctor deleted successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete doctor: {str(e)}'}, 500
