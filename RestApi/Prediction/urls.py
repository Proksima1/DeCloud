from django.urls import path
import Prediction.views as views

urlpatterns = [
    path('add/', views.api_add, name = 'api_add'),
    path('add_values/', views.Add_Values.as_view(), name = 'api_add_values'),
    path('api/upload/', views.UploadView.as_view()),
    path('api/status/<str:task_id>/', views.StatusView.as_view()),
    path('api/presigned-url/', views.PresignedUrlView.as_view()),
]

