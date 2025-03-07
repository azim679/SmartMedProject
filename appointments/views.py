from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import AppointmentForm
from .models import Appointment
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import numpy as np
import os
from django.conf import settings
from django.utils.timezone import make_aware, get_current_timezone
from .tasks import send_appointment_reminder

#load the model from file
try:
    model_path = os.path.join(settings.BASE_DIR, 'model.p')
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)  
        model = model_data['model'] 
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

#lists doctors and appointments
@login_required
def doctor_list(request):
    doctors = User.objects.filter(profile__role='doctor').select_related('profile')  # Get all doctors

    now = make_aware(datetime.now(), timezone=get_current_timezone())#make it timezone aware due to celery
    today = date.today()
    
    # Get all appointments for the user thats logged in
    user_appointments = Appointment.objects.filter(user=request.user)

    past_appointments = []
    upcoming_appointments = []

    for appointment in user_appointments:
        # Convert duration to minutes if timedelta object and if not we don't need to convert 
        duration_minutes = appointment.duration.total_seconds() / 60 if isinstance(appointment.duration, timedelta) else appointment.duration

        # Calculate end time by adding start time and date by duration
        end_time = (datetime.combine(appointment.date, appointment.time) + timedelta(minutes=duration_minutes)).time()

        if appointment.date < today or (appointment.date == today and end_time < now.time()):
            past_appointments.append(appointment)
        else:
            upcoming_appointments.append(appointment)

    #sorts past appointments by date first then time in reverse so latest first
    past_appointments.sort(key=lambda x: (x.date, x.time), reverse=True)
    
    #sorts upcoming appointments by earliest first
    upcoming_appointments.sort(key=lambda x: (x.date, x.time))

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        doctor_id = request.POST.get('doctor_id')

        if not doctor_id or not doctor_id.isdigit():
            messages.error(request, "Invalid doctor selection.")
            return redirect('appointments')

        # Get the selected doctor
        doctor = get_object_or_404(User, id=int(doctor_id), profile__role='doctor')
        form.initial['doctor'] = doctor

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.user = request.user
            appointment.save()

            #adds reminder for appointment 5 minutes before
            appointment_time = make_aware(datetime.combine(appointment.date, appointment.time))
            reminder_time = appointment_time - timedelta(minutes=5)

            reminder_delay = (reminder_time - now).total_seconds()

            print(f"Appointment at {appointment_time}, Reminder scheduled for {reminder_time}")

            #schedule celery task if in the future
            if reminder_delay > 0:
                send_appointment_reminder.apply_async(args=[appointment.id], countdown=reminder_delay)
                print("Reminder scheduled!")
            else:
                print("Error: Reminder time is in the past. Task not scheduled.")
            messages.success(request, "Appointment successfully booked! You will receive an email 5 minutes before appointment")
            return redirect('appointments') 
        else:
            messages.error(request, "There was an error booking the appointment. Please try again.")
            return render(request, 'appointments.html', {
                'doctors': doctors,
                'form': form,
                'doctor_id': doctor_id,
                'past_appointments': past_appointments,
                'upcoming_appointments': upcoming_appointments,
            })
    else:
        form = AppointmentForm()

    return render(request, 'appointments.html', {
        'doctors': doctors,
        'form': form,
        'past_appointments': past_appointments,
        'upcoming_appointments': upcoming_appointments,
        'now': now,  
        'today': today,  
        'TIME_CHOICES': TIME_CHOICES,
        'DURATION_CHOICES': DURATION_CHOICES,
    })

#cancel appointment 
@login_required
def cancel_appointment(request, appointment_id):
    try:
        #checks if appointment belongs to logged in user
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)
        appointment.delete() 
        messages.success(request, "Appointment has been cancelled.")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found")
    

    return redirect('appointments')

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

DURATION_CHOICES = [
    (30, "30 Minutes"),
    (60, "1 Hour"),
]

@login_required
def reschedule_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_date = request.POST.get('date')
        new_time = request.POST.get('time')

        try:
            # Fetch the appointment
            appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

            # Validate the new datetime
            new_datetime = datetime.combine(datetime.strptime(new_date, '%Y-%m-%d').date(),
                                            datetime.strptime(new_time, '%H:%M').time())
            if new_datetime < datetime.now():
                messages.error(request, "You cannot reschedule to a date before today.")
                return redirect('appointments')

            # Check for conflicts
            overlapping_appointments = Appointment.objects.filter(
            doctor=appointment.doctor,
            date=new_datetime.date(),
            time__lt=(new_datetime + appointment.duration).time(),
            time__gte=new_datetime.time()
            ).exclude(id=appointment.id)
    
            if overlapping_appointments.exists():
                messages.error(request, "This time slot has already been booked elsewhere choose a different time.")
                return redirect('appointments')


            appointment.date = new_datetime.date()
            appointment.time = new_datetime.time()
            appointment.save()

            messages.success(request, "Appointment successfully rescheduled.")
            return redirect('appointments')

        except Appointment.DoesNotExist:
            messages.error(request, "Appointment error.")
            return redirect('appointments')
        
@login_required
def doctor_appointments_view(request):
    if request.user.profile.role != 'doctor':
        return redirect('dashboard')

    now = datetime.now()
    today = date.today()

    # Get all appointments for this doctor
    doctor_appointments = Appointment.objects.filter(doctor=request.user)

    past_appointments = []
    upcoming_appointments = []

    for appointment in doctor_appointments:
        # Convert duration to minutes if timedelta object and if not we don't need to convert 
        duration_minutes = appointment.duration.total_seconds() / 60 if isinstance(appointment.duration, timedelta) else appointment.duration

        # Calculate end time by adding start time and date by duration
        end_time = (datetime.combine(appointment.date, appointment.time) + timedelta(minutes=duration_minutes)).time()

        if appointment.date < today or (appointment.date == today and end_time < now.time()):
            past_appointments.append(appointment)
        else:
            upcoming_appointments.append(appointment)

    #sorts past appointments by date first then time in reverse so latest first
    past_appointments.sort(key=lambda x: (x.date, x.time), reverse=True)

    #sorts upcoming appointments by earliest first
    upcoming_appointments.sort(key=lambda x: (x.date, x.time))

    context = {
        "upcoming_appointments": upcoming_appointments,
        "past_appointments": past_appointments,
        "today": today,  
        "now": now,
    }

    return render(request, "doctor_appointments.html", context)        

@login_required
def video_call(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    #retrieves if the profile of person is doctor 
    is_doctor = request.user.profile.role == "doctor"
    return render(request, "video_call.html", {
        "room_name": str(appointment.id),
        "is_doctor": is_doctor
    })

@login_required
def leave_video_call(request):
    if request.user.profile.role == "doctor":
        return redirect("doctor_appointments")  # Redirect to doctor dashboard
    else:
        return redirect("appointments")  # Redirect to user dashboard
    
# prevents unauthorised access    
@csrf_exempt
def sign_language_predict(request):
    #error handling if model cant be found
    if not model:
        print("Model failed to load! Check model.p file path")
        return JsonResponse({'error': 'Model not loaded'}, status=500)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            landmarks = data['landmarks']#extract landmarks of the hand from json data
            
            # Validate input is 42 as thats how many are in the hands
            if len(landmarks) != 42:
                return JsonResponse({'error': f'Expected 42 landmarks, got {len(landmarks)}'}, status=400)

            #converts landmarks into numpy array for effieciency and model receives correct format of 1 sample and 42 features
            landmarks_array = np.array(landmarks).reshape(1, -1)
            print("Received landmarks:", landmarks_array.shape) 
            
            try:
                #displays first prediction made by ML model
                prediction = model.predict(landmarks_array)[0]
                print("Prediction:", prediction) 
                return JsonResponse({'prediction': prediction})
            except Exception as e:
                print("Prediction error:", str(e))
                return JsonResponse({'error': 'Prediction failed'}, status=500)
                
        except Exception as e:
            print("Processing error:", str(e))
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)