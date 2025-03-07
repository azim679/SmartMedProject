from django import forms
from .models import Prescription
from django.contrib.auth.models import User

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['user', 'name', 'reason']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prescription Name'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Reason'}),
        }

    def __init__(self, *args, **kwargs):#Allows for dictionary and tuples to be passed in 
        doctor = kwargs.pop('doctor', None)  # Pass doctor instance
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields['user'].queryset = User.objects.filter(profile__role='user')  # Show only users
