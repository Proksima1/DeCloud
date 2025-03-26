import boto3
from datetime import datetime, timedelta


def handler(event, context):
    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix='uploads/')
    if 'Contents' not in response:
        return {'statusCode': 200, 'body': 'Файлы не найдены'}
    for obj in response['Contents']:
        # Удаляем файлы старше допустим 1 дня
        if obj['LastModified'] < datetime.now() - timedelta(days=1):
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    return {'statusCode': 200, 'body': 'Очистка завершена'}