from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from django import forms
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

#Custom registartion form
class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta: 
        model= User
        fields = ["username","first_name", "last_name", "email", "password1", "password2"]


@login_required
def dashboard(request):
    return render(request, "dashboard.html")

#creates new user if request is post
def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html",{"form":form})


