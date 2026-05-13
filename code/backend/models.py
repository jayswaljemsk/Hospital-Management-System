from extensions import db
from flask_security import UserMixin, RoleMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)

    roles = db.relationship('Role', secondary='user_roles', backref='bearers')
    patient = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete-orphan")

    @property
    def role(self):
        return self.roles[0].name if self.roles else None

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class UserRoles(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

class Patient(db.Model):
    __tablename__ = 'patients'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)

    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade="all, delete-orphan", uselist=True)

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    doctors = db.relationship('Doctor', backref='department', lazy=True, cascade="all, delete-orphan", uselist=True)

class Doctor(db.Model):
    __tablename__ = 'doctors'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    specialty = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    availability = db.relationship('DoctorAvailability', backref='doctor', uselist=False, lazy=True, cascade="all, delete-orphan")
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade="all, delete-orphan")

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.user_id'), nullable=False)
    # e.g., {"Monday": {"morning": True, "afternoon": True, "evening":True}, "Tuesday": {"morning": False, "afternoon": True, "evening":True}, ...}
    availability = db.Column(db.JSON, nullable=False)

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slot = db.Column(db.Enum('morning', 'afternoon', 'evening'), nullable=False, default='morning', name='apt_slot')
    status = db.Column(db.Enum('booked', 'completed', 'cancelled'), name='apt_status', default='booked', nullable=False)

    treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade="all, delete-orphan")

class Treatment(db.Model):
    __tablename__ = 'treatments'

    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False, primary_key=True)

    tests_done = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    medicines = db.Column(db.Text)
