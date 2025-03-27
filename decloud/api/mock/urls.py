from api.mock.views import MockGetImageView, MockPresignedUrlView, MockStatusView, MockUploadView
from django.urls import path

urlpatterns = [
    path("image/upload/", MockUploadView.as_view()),
    path("image/status/<uuid:task_id>/", MockStatusView.as_view()),
    path("image/get-processed/<uuid:task_id>/", MockGetImageView.as_view()),
    path("get-presigned-url/", MockPresignedUrlView.as_view()),
]
