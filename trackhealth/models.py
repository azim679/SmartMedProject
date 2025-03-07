from django.contrib.auth.models import User
from django.db import models

class TrackHealth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_metrics")
    heart_rate = models.IntegerField()
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    weight = models.FloatField()  
    height = models.FloatField() 
    bmi = models.FloatField(null=True, blank=True)  
    activity_level = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High'),
        ]
    )
    blood_glucose = models.FloatField()
    date = models.DateField()

    #BMI calculation
    def save(self, *args, **kwargs):
        if self.weight and self.height:
            self.bmi = round(self.weight / (self.height ** 2), 2) 
        super().save(*args, **kwargs)