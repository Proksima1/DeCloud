import boto3
import requests


def handler(event, context):
    bucket_name = event['bucket']['name']
    object_key = event['object']['key']
    task_id = object_key.split('/')[-1]

    processed_key = f"processed/{task_id}"

    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
    s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': object_key},
        Key=processed_key,
    )
    # Обновляем статус в Django через API
    update_status_url = f"{os.getenv('BACKEND_API_URL')}/api/update-status/{task_id}/"
    response = requests.post(
        update_status_url,
        headers={"Authorization": "Bearer API_TOKEN"},
        json={"status": "ready"}
    )

    return {
        'statusCode': 200,
        'body': 'Файл обработан и статус обновлен'
    }