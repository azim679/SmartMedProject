from celery import shared_task
from django.core.mail import send_mail
from .models import Appointment

#send email 5 minutes before appointment
@shared_task
def send_appointment_reminder(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        user_email = appointment.user.email

        subject = "Upcoming Appointment Reminder"
        message = f"""
        Dear {appointment.user.first_name},

        This is a reminder for your upcoming appointment with Dr. {appointment.doctor.username} 
        at {appointment.time.strftime('%H:%M')} on {appointment.date.strftime('%Y-%m-%d')}.

        Best regards,
        SmartMed 
        """

        send_mail(
            subject,
            message,
            'smartmed681@gmail.com',  
            [user_email],
            fail_silently=False,
        )

        return f"Reminder email sent to {user_email}"

    except Appointment.DoesNotExist:
        return "Appointment not found"
