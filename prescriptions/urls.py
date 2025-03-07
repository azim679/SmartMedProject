from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.user_prescriptions, name='prescriptions'),
    path('add/', views.add_prescription, name='add_prescription')
    
]
