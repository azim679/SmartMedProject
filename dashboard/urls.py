from django.urls import path
from .views import chatbot_response

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path("chatbot/", chatbot_response, name="chatbot_response"),
]