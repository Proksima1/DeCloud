import boto3
import json
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def handler(event, context):
    print("Raw event:", event)  # Логируем входные данные
    # Если event — словарь, но тело запроса (`body`) передано строкой, парсим `body`
    if isinstance(event, dict) and "body" in event:
        try:
            event = json.loads(event["body"])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON format in body", "event": event})
            }
    print("Parsed event:", event)  # Логируем распарсенные данные
    bucket_name = event.get("bucket_name")
    task_id = event.get("task_id")
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url="https://storage.yandexcloud.net",
            config=boto3.session.Config(signature_version='s3v4')
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Ошибка при создании S3 клиента: {str(e)}"})
        }
    file_key = f"testka/uploads/{task_id}" # # Формируем путь к файлу в S3
    try:
        presigned_url = s3.generate_presigned_url(
            "put_object", # Генерация Pre-Signed URL
            Params={
                "Bucket": bucket_name,
                "Key": file_key,
                "ContentType": "application/octet-stream",
            },
            ExpiresIn=3600,
            HttpMethod="PUT"
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "presigned_url": presigned_url,
                "task_id": task_id
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Ошибка при генерации Pre-Signed URL: {str(e)}"})
        }
