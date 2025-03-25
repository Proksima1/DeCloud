from django.urls import path

from .views import MockGetImageView, MockPresignedUrlView, MockStatusView, MockUploadView

urlpatterns = [
    path("image/upload/", MockUploadView.as_view()),
    path("image/status/<uuid:task_id>/", MockStatusView.as_view()),
    path("image/get-processed/<uuid:task_id>/", MockGetImageView.as_view()),
    path("get-presigned-url/", MockPresignedUrlView.as_view()),
]
