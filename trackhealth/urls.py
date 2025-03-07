from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.trackhealth_view, name='trackhealth')

]