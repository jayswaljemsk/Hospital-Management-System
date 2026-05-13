import os

from celery.result import AsyncResult
from flask import current_app, send_file

from tasks import export_as_csv


class ExportService:

    @staticmethod
    def trigger_patient_export(user_id):
        task = export_as_csv.delay(user_id)
        return {
            'message': 'CSV export task started.',
            'task_id': task.id,
            'status': 'queued',
        }, 202

    @staticmethod
    def get_export_status(user_id, task_id):
        celery_app = current_app.extensions.get('celery')
        if not celery_app:
            return {'error': 'Celery is not configured.'}, 500

        result = AsyncResult(task_id, app=celery_app)
        state = result.state

        response = {
            'task_id': task_id,
            'status': state,
            'download_ready': False,
            'download_url': None,
        }

        if state == 'SUCCESS':
            file_name = result.result
            if isinstance(file_name, str) and file_name.startswith(f'user_{user_id}_treatments_'):
                response['download_ready'] = True
                response['download_url'] = f'/api/patients/{user_id}/export-csv/{task_id}/download'
            else:
                response['status'] = 'FAILED'

        if state == 'FAILURE':
            response['error'] = str(result.result)

        return {'data': response}, 200

    @staticmethod
    def download_export_file(user_id, task_id):
        celery_app = current_app.extensions.get('celery')
        if not celery_app:
            return {'error': 'Celery is not configured.'}, 500

        result = AsyncResult(task_id, app=celery_app)
        if result.state != 'SUCCESS':
            return {'error': 'Export is not ready yet.'}, 400

        file_name = result.result
        if not isinstance(file_name, str) or not file_name.startswith(f'user_{user_id}_treatments_'):
            return {'error': 'You are not authorized to download this export.'}, 403

        file_path = os.path.join('instance', 'exports', file_name)
        if not os.path.exists(file_path):
            return {'error': 'Export file not found.'}, 404

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype='text/csv')
