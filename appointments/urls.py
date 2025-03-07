from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='appointments'),
     path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
     path('reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
     path('appointments/', views.doctor_appointments_view, name='doctor_appointments'),
     path('video/<int:appointment_id>/', views.video_call, name='video_call'),
     path("leave-video-call/", views.leave_video_call, name="leave_video_call"),
     path('sign_language/predict/', views.sign_language_predict, name='sign_language_predict'),
]
