from django import forms
from .models import Appointment
from datetime import datetime, timedelta
from django.db.models import Q


class AppointmentForm(forms.ModelForm):
    DURATION_CHOICES = [
        (30, "30 Minutes"),
        (60, "1 Hour"),
    ]

    TIME_CHOICES = [
        ("09:00", "9:00 AM"),
        ("09:30", "9:30 AM"),
        ("10:00", "10:00 AM"),
        ("10:30", "10:30 AM"),
        ("11:00", "11:00 AM"),
        ("11:30", "11:30 AM"),
        ("12:00", "12:00 PM"),
        ("12:30", "12:30 PM"),
        ("13:00", "1:00 PM"),
        ("13:30", "1:30 PM"),
        ("14:00", "2:00 PM"),
        ("14:30", "2:30 PM"),
        ("15:00", "3:00 PM"),
        ("15:30", "3:30 PM"),
        ("16:00", "4:00 PM")
    ]

    duration = forms.ChoiceField(
        choices=DURATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Appointment Time"
    )

    class Meta:
        model = Appointment
        fields = ['date', 'time', 'duration', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for appointment'}),
        }

    def clean_duration(self):
        #Convert duration to a timedelta if it's not already
        duration = self.cleaned_data.get('duration')
        if isinstance(duration, timedelta):
            return duration  
        if duration:
            return timedelta(minutes=int(duration)) 
        return duration

    def clean(self):
        #Validate and ensure no overlapping appointments
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_str = cleaned_data.get('time') 
        duration = cleaned_data.get('duration') 
        doctor = self.initial.get('doctor') 

        if not date or not time_str or not duration or not doctor:
            return cleaned_data 

        # Calculate the start and end times for the new appointment
        hours, minutes = map(int, time_str.split(":"))
        start_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=hours, minutes=minutes)
        end_time = start_time + duration

        # Query for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            doctor=doctor,
            date=date,
        ).filter(
            Q(time__lt=end_time.time()) & Q(time__gte=start_time.time())
        )

        if overlapping_appointments.exists():
            raise forms.ValidationError("This time slot is not available. Please choose a different time.")

        return cleaned_data
