from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("login.urls")),
    path('dashboard/', include('dashboard.urls')),
    path('trackhealth/', include('trackhealth.urls')),
    path('prescriptions/', include('prescriptions.urls')),
    path('appointments/', include('appointments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)