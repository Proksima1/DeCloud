import boto3
import json
import os
from datetime import datetime, timedelta

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def handler(event, context):
    print("Raw event:", event)

    if isinstance(event, dict) and "body" in event:
        try:
            event = json.loads(event["body"])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON format in body", "event": event})
            }
    print("Parsed event:", event)

    bucket_name = event.get("bucket_name")
    task_id = event.get("task_id")
    expires_in = event.get("expires_in", 3600)

    # Проверка
    if not bucket_name or not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required parameters: 'bucket_name' and 'task_id' are required"})
        }

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
    file_key = f"testka/uploads/{task_id}"

    try:
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": file_key,
                "ContentType": "application/octet-stream",
            },
            ExpiresIn=expires_in,
            HttpMethod="PUT"
        )

        expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)
        expiration_time_iso = expiration_time.isoformat() + "Z" 

        return {
            "statusCode": 200,
            "body": json.dumps({
                "presigned_url": presigned_url,
                "task_id": task_id,
                "expiration_time": expiration_time_iso
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Ошибка при генерации Pre-Signed URL: {str(e)}"})
        }