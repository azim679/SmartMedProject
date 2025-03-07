from django.db import models
from django.contrib.auth.models import User

class Prescription(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescribed_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    name = models.CharField(max_length=255)  
    reason = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Prescription: {self.name} for {self.user.username}"
