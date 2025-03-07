from django.contrib import admin
from .models import Profile

#displays user and role in the admin panel
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',) 