import Prediction.views as views
from django.urls import path

urlpatterns = [
    path("add/", views.api_add, name="api_add"),
    path("add_values/", views.Add_Values.as_view(), name="api_add_values"),
]
