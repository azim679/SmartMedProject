from django.contrib import admin

from .models import TrackHealth

@admin.register(TrackHealth)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'heart_rate', 
        'blood_pressure_systolic', 
        'blood_pressure_diastolic', 
        'weight', 
        'height', 
        'bmi', 
        'activity_level', 
        'blood_glucose',
        'date', 
    )

