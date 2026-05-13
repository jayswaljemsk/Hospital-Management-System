import os

from celery.schedules import crontab
from dotenv import load_dotenv


load_dotenv()


broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'
timezone = os.getenv('CELERY_TIMEZONE', 'UTC')
broker_connection_retry_on_startup = True

daily_reminder_hour = int(os.getenv('DAILY_REMINDER_HOUR', '8'))
daily_reminder_minute = int(os.getenv('DAILY_REMINDER_MINUTE', '0'))
monthly_report_hour = int(os.getenv('MONTHLY_REPORT_HOUR', '9'))
monthly_report_minute = int(os.getenv('MONTHLY_REPORT_MINUTE', '0'))

beat_schedule = {
    'daily-reminder-task': {
        'task': 'daily_reminders',
        'schedule': crontab(hour=daily_reminder_hour, minute=daily_reminder_minute),
    },
    'monthly-doctor-report-task': {
        'task': 'monthly_activity_report',
        'schedule': crontab(day_of_month=1, hour=monthly_report_hour, minute=monthly_report_minute),
    },
}