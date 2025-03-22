from django.urls import path

from .views import GetImageView, PresignedUrlView, StatusView

urlpatterns = [
    path("image/status/<uuid:task_id>/", StatusView.as_view()),
    path("image/get-processed/<uuid:task_id>/", GetImageView.as_view()),
    path("get-presigned-url/", PresignedUrlView.as_view()),
]
