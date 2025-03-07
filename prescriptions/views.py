from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PrescriptionForm
from django.contrib import messages
from .models import Prescription


def prescriptions_view(request):
    return render(request, 'prescriptions.html')

@login_required
def add_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, doctor=request.user)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user  # Set the current doctor
            prescription.save()
            messages.success(request, "Prescription added successfully!")
            return redirect('add_prescription')
    else:
        form = PrescriptionForm(doctor=request.user)
    return render(request, 'add_prescription.html', {
        'form': form,
    })


@login_required
def user_prescriptions(request):
    # Retrieve prescriptions for the logged-in user, ordered by creation date 
    prescriptions = Prescription.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'prescriptions.html', {'prescriptions': prescriptions})

