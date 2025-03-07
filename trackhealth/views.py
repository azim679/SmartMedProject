from django.shortcuts import render, redirect
from .models import TrackHealth
from .forms import HealthDataForm
from django.contrib.auth.decorators import login_required

@login_required
def trackhealth_view(request):
    # data for date selected
    selected_date = request.GET.get('date', None)
    health_data = None

    if selected_date:
        # Filter health data by date
        health_data = TrackHealth.objects.filter(user=request.user, date=selected_date).first()

    if not health_data:
        health_data = {
            'heart_rate': 0,
            'weight': 0,
            'height': 0,
            'blood_glucose': 0,
            'blood_pressure_systolic': 0,
            'blood_pressure_diastolic': 0,
            'activity_level': 'N/A',  
            'bmi': 0,
            'date': selected_date or 'N/A',
        }
    #form data associated with logged in user track health data
    if request.method == 'POST':
        form = HealthDataForm(request.POST)
        form.instance.user = request.user
        if form.is_valid():
            new_data = form.save(commit=False)
            new_data.user = request.user 
            if new_data.weight and new_data.height:
                new_data.bmi = round(new_data.weight / (new_data.height ** 2), 2)
            new_data.save()
            form = HealthDataForm()  
            success_message = "Health data successfully added."
        else:
            success_message = None 
    else:
        form = HealthDataForm()
        success_message = None

    return render(request, 'trackhealth.html', {
        'user': request.user,
        'health_data': health_data,
        'selected_date': selected_date,
        'form': form,
        'success_message': success_message
    })
