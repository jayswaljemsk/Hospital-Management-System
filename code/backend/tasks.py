import csv
import os
from collections import defaultdict
from datetime import date, datetime, timedelta

from celery import shared_task
from jinja2 import Template

from mail import send_email
from models import Appointment, Doctor, Patient, Treatment


@shared_task(ignore_result=False, name="export_as_csv")
def export_as_csv(user_id):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return None

    appointments = (
        Appointment.query.filter_by(patient_id=user_id)
        .order_by(Appointment.date.asc())
        .all()
    )

    export_dir = os.path.join('instance', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    csv_file_name = f"user_{user_id}_treatments_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_dir, csv_file_name)

    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            'User ID',
            'Username',
            'Consulting Doctor',
            'Appointment Date',
            'Slot',
            'Status',
            'Diagnosis',
            'Prescription',
            'Medicines',
        ])

        for appointment in appointments:
            treatment = appointment.treatment
            writer.writerow([
                patient.user_id,
                patient.user.name,
                appointment.doctor.user.name,
                appointment.date,
                appointment.slot,
                appointment.status,
                treatment.diagnosis if treatment else '',
                treatment.prescription if treatment else '',
                treatment.medicines if treatment else '',
            ])

    return csv_file_name


@shared_task(ignore_result=False, name="monthly_activity_report")
def monthly_activity_report():
    first_day_current_month = date.today().replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    month_label = first_day_previous_month.strftime('%B %Y')

    doctors = Doctor.query.all()
    for doctor in doctors:
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.user_id,
            Appointment.date >= first_day_previous_month,
            Appointment.date <= last_day_previous_month,
        ).all()

        details = []
        for appointment in appointments:
            treatment = appointment.treatment
            details.append(
                {
                    'patient_name': appointment.patient.user.name,
                    'date': appointment.date,
                    'slot': appointment.slot,
                    'status': appointment.status,
                    'diagnosis': treatment.diagnosis if treatment else '-',
                    'prescription': treatment.prescription if treatment else '-',
                }
            )

        mail_template = """
        <h3>Dear {{ doctor_name }}</h3>
        <p>Please find your monthly activity report for {{ month_label }}.</p>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr>
                <th>Patient</th>
                <th>Date</th>
                <th>Slot</th>
                <th>Status</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
            </tr>
            {% if details %}
              {% for detail in details %}
              <tr>
                  <td>{{ detail.patient_name }}</td>
                  <td>{{ detail.date }}</td>
                  <td>{{ detail.slot }}</td>
                  <td>{{ detail.status }}</td>
                  <td>{{ detail.diagnosis }}</td>
                  <td>{{ detail.prescription }}</td>
              </tr>
              {% endfor %}
            {% else %}
              <tr>
                  <td colspan="6">No appointments in this month.</td>
              </tr>
            {% endif %}
        </table>
        <p>Regards,<br>Hospital Management System</p>
        """

        message = Template(mail_template).render(
            doctor_name=doctor.user.name,
            month_label=month_label,
            details=details,
        )

        send_email(
            doctor.user.email,
            subject=f"Monthly Activity Report - {month_label}",
            message=message,
        )

    return "Monthly reports sent"


@shared_task(ignore_result=False, name="daily_reminders")
def daily_reminders():
    try:
        today = date.today()
        appointments = Appointment.query.filter_by(date=today, status='booked').all()

        if not appointments:
            return "No appointments today"

        appointments_by_patient = defaultdict(list)
        for appointment in appointments:
            appointments_by_patient[appointment.patient].append(appointment)

        for patient, items in appointments_by_patient.items():
            rows = ''.join(
                [
                    (
                        '<tr>'
                        f'<td>{appointment.doctor.user.name}</td>'
                        f'<td>{appointment.slot}</td>'
                        f'<td>{appointment.doctor.department.name}</td>'
                        '</tr>'
                    )
                    for appointment in items
                ]
            )

            mail_template = """
            <h3>Dear {{ patient_name }}</h3>
            <p>This is your reminder for today\'s booked appointment.</p>
            <table border="1" cellpadding="6" cellspacing="0">
                <tr>
                    <th>Doctor</th>
                    <th>Slot</th>
                    <th>Department</th>
                </tr>
                {{ rows | safe }}
            </table>
            <p>Please visit the hospital at your scheduled slot.</p>
            """

            message = Template(mail_template).render(patient_name=patient.user.name, rows=rows)

            send_email(
                patient.user.email,
                subject='Daily Appointment Reminder',
                message=message,
            )

        return "Daily reminders sent"
    except Exception as e:
        return f"Error sending daily reminders: {str(e)}"