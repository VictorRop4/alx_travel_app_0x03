from django.test import TestCase

# Create your tests here.
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_payment_confirmation_email(to_email, booking_id):
    subject = "Payment Confirmation - Booking Successful"
    message = f"Dear Customer,\n\nYour payment for booking #{booking_id} was successful.\nWe look forward to your trip!"
    from_email = "no-reply@alxtravelapp.com"

    send_mail(subject, message, from_email, [to_email])
