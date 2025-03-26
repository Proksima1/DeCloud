import requests


def handler(event, context):
    task_id = event.get('task_id')
    if not task_id:
        return {'statusCode': 400, 'body': 'task_id не указан'}
    response = requests.get(
        f"{'BACKEND_API_URL'}/api/status/{task_id}/",
        headers={"Authorization": "Bearer API_TOKEN"}
    )
    return {
        'statusCode': response.status_code,
        'body': response.json()
    }