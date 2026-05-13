from datetime import date
from models import Appointment, Treatment, Doctor, DoctorAvailability, db
from flask_security import current_user

class AppointmentService:

    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    SLOTS = ["morning", "afternoon", "evening"]

    @staticmethod
    def _normalize_availability_for_today(availability_dict):
        if not isinstance(availability_dict, dict):
            return {
                day: {slot: (False if day == 'Sunday' else True) for slot in AppointmentService.SLOTS}
                for day in AppointmentService.WEEKDAYS
            }, True

        today_name = date.today().strftime('%A')
        today_index = AppointmentService.WEEKDAYS.index(today_name)
        changed = False

        normalized = {
            day: (dict(availability_dict.get(day, {})) if isinstance(availability_dict.get(day, {}), dict) else {})
            for day in AppointmentService.WEEKDAYS
        }

        for day in AppointmentService.WEEKDAYS:
            if day not in availability_dict:
                changed = True
            for slot in AppointmentService.SLOTS:
                if slot not in normalized[day]:
                    normalized[day][slot] = False if day == 'Sunday' else True
                    changed = True

        for index, day in enumerate(AppointmentService.WEEKDAYS):
            if day == 'Sunday':
                for slot in AppointmentService.SLOTS:
                    if normalized[day][slot] is not False:
                        normalized[day][slot] = False
                        changed = True
                continue

            if index < today_index:
                for slot in AppointmentService.SLOTS:
                    if normalized[day][slot] is not True:
                        normalized[day][slot] = True
                        changed = True

        return normalized, changed

    @staticmethod
    def appointment_json(appointment):
        appointments = Appointment.query.filter_by(patient_id=appointment.patient_id).all()
        history = []
        for apt in appointments:
            if apt.status == 'completed':
                treatment = apt.treatment
                history.append({
                    'id': apt.id,
                    'date': str(apt.date),
                    'doctor_name': apt.doctor.user.name, 
                    'department': apt.doctor.department.name,
                    'tests_done': treatment.tests_done,
                    'diagnosis': treatment.diagnosis,
                    'prescription': treatment.prescription,
                    'medicines': treatment.medicines
                })
        appointment_info = {
            'id': appointment.id,
            'patient_id': appointment.patient_id,
            'patient_name': appointment.patient.user.name,
            'doctor_id': appointment.doctor_id,
            'doctor_name': appointment.doctor.user.name,
            'department': appointment.doctor.department.name,
            'date': str(appointment.date),
            'slot': appointment.slot,
            'status': appointment.status,
            'history': history
        }
        
        return appointment_info

    @staticmethod
    def create_appointment(data):

        doctor_id = data.get('doctor_id')
        apt_date = data.get('date')
        slot = data.get('slot')
        weekday = apt_date.strftime('%A')  

        doctor = Doctor.query.filter_by(user_id=doctor_id).first()
        if not doctor or not doctor.user.active:
            return {'error': 'Doctor not available.'}, 404

        # Check if doctor is available for this slot
        avail = DoctorAvailability.query.filter_by(doctor_id=doctor_id).first()
        if avail:
            normalized_availability, changed = AppointmentService._normalize_availability_for_today(avail.availability)
            if changed:
                avail.availability = normalized_availability
                db.session.commit()
        is_available = avail.availability[weekday][slot] if avail and weekday in avail.availability and slot in avail.availability[weekday] else False
        if not is_available:
            return {'error': 'This slot is not available.'}, 409

        existing_booked_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=apt_date,
            slot=slot,
            status='booked',
        ).first()
        if existing_booked_appointment:
            return {'error': 'This slot is already booked for selected date.'}, 409

        try:
            new_appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=doctor_id,
                date=apt_date,
                slot=slot
            )

            db.session.add(new_appointment)
            db.session.flush()

            treatment = Treatment(appointment_id=new_appointment.id)
            db.session.add(treatment)

            updated_availability = {
                day: (dict(day_slots) if isinstance(day_slots, dict) else {})
                for day, day_slots in avail.availability.items()
            }
            updated_availability[weekday][slot] = False
            avail.availability = updated_availability

            db.session.commit()

            return {'message': 'Appointment booked successfully.'}, 201            

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def get_all_appointments():
        if current_user.role == 'admin':
            appointments = Appointment.query.all()
        elif current_user.role == 'doctor':
            appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        elif current_user.role == 'patient':
            appointments = Appointment.query.filter_by(patient_id=current_user.id).all()

        if not appointments:
            return {'error': 'No appointments found.'}, 404
        try:
            appointment_list = []
            for appointment in appointments:
                appointment_info = AppointmentService.appointment_json(appointment)
                appointment_list.append(appointment_info)

            return {'data': appointment_list, 'message': 'Appointments retrieved successfully.'}, 200
        except Exception as e:
            return {'error': f'Failed to retrieve appointments: {str(e)}'}, 500

    @staticmethod
    def get_appointment_by_id(appointment_id):  
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {'error': 'Appointment not found.'}, 404
        
        try:
            appointment_data = AppointmentService.appointment_json(appointment)
            return {'data': appointment_data, 'message': 'Appointment retrieved successfully.'}, 200
        except Exception as e:
            return {'error': f'Failed to retrieve appointment: {str(e)}'}, 500

    @staticmethod
    def update_appointment(appointment_id, data):
        appointment = Appointment.query.get(appointment_id)

        if not appointment:
            return {'error': 'Appointment not found.'}, 404

        if appointment.status == 'cancelled' and data.get('status') == 'cancelled':
            return {'error': 'Appointment is already cancelled.'}, 400

        apt_date = appointment.date
        slot = appointment.slot
        weekday = apt_date.strftime('%A')

        avail = DoctorAvailability.query.filter_by(doctor_id=appointment.doctor_id).first()

        if avail:
            normalized_availability, changed = AppointmentService._normalize_availability_for_today(avail.availability)
            if changed:
                avail.availability = normalized_availability
                db.session.commit()

        if data.get('status') == 'booked':
            is_available = avail.availability[weekday][slot] if avail and weekday in avail.availability and slot in avail.availability[weekday] else False
            if not is_available:
                return {'error': 'This slot is not available.'}, 409

            existing_booked_appointment = Appointment.query.filter(
                Appointment.id != appointment.id,
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.date == appointment.date,
                Appointment.slot == appointment.slot,
                Appointment.status == 'booked',
            ).first()
            if existing_booked_appointment:
                return {'error': 'This slot is already booked for selected date.'}, 409

        try:
            for key, value in data.items():
                if value is None:
                    continue
                if key == 'status':
                    setattr(appointment, key, value)

            if avail:
                updated_availability = {
                    day: (dict(day_slots) if isinstance(day_slots, dict) else {})
                    for day, day_slots in avail.availability.items()
                }

                if data.get('status') == 'booked':
                    updated_availability[weekday][slot] = False
                else:
                    updated_availability[weekday][slot] = False if weekday == 'Sunday' else True

                avail.availability = updated_availability

            db.session.commit()
            return {'message': f'Appointment {data.get("status")} successfully.'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update appointment: {str(e)}'}, 500
    