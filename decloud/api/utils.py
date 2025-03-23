import boto3
from botocore.client import BaseClient
from django.conf import settings


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        aws_access_key_id=settings.YC_ACCESS_KEY_ID,
        aws_secret_access_key=settings.YC_SECRET_ACCESS_KEY,
        endpoint_url=settings.YC_ENDPOINT_URL,
        config=boto3.session.Config(signature_version="s3v4"),
    )


# def generate_presigned_url_for_upload(): ...
