from django.urls import path
import Prediction.views as views

urlpatterns = [
    path("api/image/upload/", views.UploadView.as_view()),
    path("api/image/status/<str:task_id>/", views.StatusView.as_view()),
    path("api/image/get-processed/<str:task_id>/", views.GetImageView.as_view()),
    path("api/get-presigned-url/", views.PresignedUrlView.as_view()),
]
