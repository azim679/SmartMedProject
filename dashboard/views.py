from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from trackhealth.models import TrackHealth
import json
from django.http import JsonResponse
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import torch

#path of trained model, question and answers
df = pd.read_csv("processed_faq.csv") 
question_embeddings = torch.load("question_embeddings.pt")

#model used 
model = SentenceTransformer("all-MiniLM-L6-v2")

#Dashboard for user role
@login_required
def dashboard_view(request):
    if request.user.profile.role == 'user':
        today = date.today()
        ten_days_ago = today - timedelta(days=10)

        #gets todays tracked data and from the last 10 days
        health_data = TrackHealth.objects.filter(user=request.user, date=today).first()
        health_history = TrackHealth.objects.filter(user=request.user, date__gte=ten_days_ago).order_by('date')

        #sorted data for the barchart
        health_dates = [entry.date.strftime('%b %d') for entry in health_history]
        blood_pressure_systolic_data = [entry.blood_pressure_systolic for entry in health_history]
        blood_pressure_diastolic_data = [entry.blood_pressure_diastolic for entry in health_history]
        heart_rate_data = [entry.heart_rate for entry in health_history]
        blood_glucose_data = [entry.blood_glucose for entry in health_history]
        bmi_data = [entry.bmi for entry in health_history]
        weight_data = [entry.weight for entry in health_history]


        # Fetch appointments for today
        todays_appointments = Appointment.objects.filter(user=request.user, date=today).select_related('doctor__profile')

        #default values
        if not health_data:
            health_data = {
                "blood_pressure_systolic": 0,
                "blood_pressure_diastolic": 0,
                "heart_rate": 0,
                "weight": 0,
                "height": 0,
                "bmi": 0,
                "activity_level": "N/A",
                "blood_glucose": 0
            }

        context = {
            "health_data": health_data,
            "todays_appointments": todays_appointments,
            "health_dates": json.dumps(health_dates),
            "blood_pressure_systolic_data": json.dumps(blood_pressure_systolic_data),
            "blood_pressure_diastolic_data": json.dumps(blood_pressure_diastolic_data),
            "heart_rate_data": json.dumps(heart_rate_data),
            "blood_glucose_data": json.dumps(blood_glucose_data),
            "bmi_data": json.dumps(bmi_data),
            "weight_data": json.dumps(weight_data),
        }

        return render(request, "dashboard.html", context)

    #dashboard for doctor role
    elif request.user.profile.role == 'doctor':
        today = date.today()
    
        # Fetch appointments for doctor today
        todays_appointments = Appointment.objects.filter(doctor=request.user, date=today)

        context = {
            "todays_appointments": todays_appointments,
        }

        return render(request, "doctor_dashboard.html", context)
    else:
        return redirect('login')
    

def chatbot_response(request):
    #gets the users inputted query
    user_query = request.GET.get("query", "")

    if not user_query:
        return JsonResponse({"response": "Please enter a valid question."})

    #convert user query to embedding
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    #compare query with stored question embedding
    scores = util.pytorch_cos_sim(query_embedding, question_embeddings)

    #find the best matching response and return it as json
    best_match_idx = torch.argmax(scores).item()
    response_text = df["Answer"][best_match_idx]
    return JsonResponse({"response": response_text})
