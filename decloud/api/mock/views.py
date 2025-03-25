import uuid
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class MockUploadView(APIView):
    def post(self, _request: Request) -> Response:
        task_id = uuid.uuid4()

        return Response(
            {"task_id": str(task_id), "status": "queued", "message": "File upload accepted"},
            status=status.HTTP_202_ACCEPTED,
        )


class MockStatusView(APIView):
    def get(self, _request: Request, task_id: str) -> Response:
        current_second = datetime.now().second
        status = "processing" if current_second % 2 == 0 else "ready"

        return Response(
            {
                "task_id": task_id,
                "status": status,
                "progress": 100 if status == "ready" else current_second % 100,
                "estimated_completion": (datetime.now() + timedelta(seconds=30)).isoformat(),
            }
        )


class MockGetImageView(APIView):
    def get(self, _request: Request, task_id: str) -> Response:
        return Response(
            {
                "task_id": task_id,
                "status": "completed",
                "download_url": f"https://mock-storage.example.com/images/{task_id}.jpg",
                "expires_at": (datetime.now() + timedelta(days=1)).isoformat(),
            }
        )


class MockPresignedUrlView(APIView):
    def get(self, _request: Request) -> Response:
        task_id = uuid.uuid4()
        return Response(
            {
                "task_id": str(task_id),
                "upload_url": f"https://mock-storage.example.com/upload/{task_id}",
                "fields": {
                    "key": f"uploads/{task_id}",
                    "AWSAccessKeyId": "MOCK_ACCESS_KEY",
                    "policy": "MOCK_POLICY_STRING",
                    "signature": "MOCK_SIGNATURE",
                },
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            }
        )
