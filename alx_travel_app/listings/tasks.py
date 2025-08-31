from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings



@shared_task
def send_payment_confirmation_email(to_email, booking_id):
    subject = "Payment Confirmation - Booking Successful"
    message = f"Dear Customer,\n\nYour payment for booking #{booking_id} was successful.\nWe look forward to your trip!"
    from_email = "no-reply@alxtravelapp.com"

    send_mail(subject, message, from_email, [to_email])


@shared_task
def send_booking_confirmation(email, listing_name):
    subject = "Booking Confirmation"
    message = f"Your booking for {listing_name} was successful!"
    from_email = "no-reply@alxtravelapp.com"
    
    send_mail(subject, message, from_email, [email])
    return f"Confirmation sent to {email}"


