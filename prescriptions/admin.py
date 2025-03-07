from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'user', 'name', 'created_at')  
    list_filter = ('doctor', 'created_at') 
    search_fields = ('name', 'user__username', 'doctor__username')  
