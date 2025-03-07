from django.urls import path, include
from .views import dashboard, registration


urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", dashboard, name="dashboard"),
    path("",registration, name ="registration"),
]
