from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = ('id', 'doctor', 'date', 'time', 'duration', 'reason', 'created_at')

    list_filter = ('doctor', 'date', 'time')

    search_fields = ('doctor__username', 'reason')

    ordering = ('-created_at',)