from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Booking, Payment
from .tasks import send_payment_confirmation_email
from .tasks import send_booking_confirmation

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

def perform_create(self, serializer):
    # attach current user as the booking user
    serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('booking', 'booking__user', 'booking__listing').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def create(self, request, *args, **kwargs):
    # ensure review is created only if booking exists and belongs to user (optional rule)
    return super().create(request, *args, **kwargs)



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


    def perform_create(self, serializer):
        booking = serializer.save()
        # Trigger async email task
        send_booking_confirmation.delay(
            booking.user.email,  # assuming booking has a user FK
            booking.id
        )








@api_view(["POST"])
def initiate_payment(request, booking_id):
    """
    Step 1: Initiate a payment request with Chapa
    """
    try:
        booking = Booking.objects.get(id=booking_id)

        # Create Payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.price,
            status="pending"
        )

        # Prepare Chapa payload
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

        payload = {
            "amount": str(payment.amount),
            "currency": "ETB",
            "email": booking.customer_email,
            "first_name": booking.customer_name.split()[0],
            "last_name": booking.customer_name.split()[-1],
            "tx_ref": str(payment.reference),
            "callback_url": f"http://127.0.0.1:8000/api/payments/verify/{payment.reference}/",
        }

        response = requests.post(chapa_url, headers=headers, json=payload)
        chapa_response = response.json()

        if response.status_code == 200 and chapa_response.get("status") == "success":
            payment.transaction_id = chapa_response["data"]["tx_ref"]
            payment.save()

            return Response({
                "checkout_url": chapa_response["data"]["checkout_url"],
                "payment_id": payment.id,
                "status": payment.status
            }, status=status.HTTP_200_OK)

        return Response({
            "error": chapa_response.get("message", "Payment initiation failed")
        }, status=status.HTTP_400_BAD_REQUEST)

    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def verify_payment(request, reference):
    """
    Step 2: Verify payment with Chapa after user completes checkout
    """
    try:
        payment = Payment.objects.get(reference=reference)

        chapa_url = f"https://api.chapa.co/v1/transaction/verify/{payment.reference}"
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        response = requests.get(chapa_url, headers=headers)
        chapa_response = response.json()

        if response.status_code == 200 and chapa_response.get("status") == "success":
            payment.status = "success"
            payment.transaction_id = chapa_response["data"]["tx_ref"]
            payment.save()

            # Send confirmation email asynchronously
            send_payment_confirmation_email.delay(payment.booking.customer_email, payment.booking.id)

            return Response({
                "message": "Payment successful",
                "status": payment.status,
                "booking_id": payment.booking.id
            }, status=status.HTTP_200_OK)

        # Mark as failed if Chapa does not confirm
        payment.status = "failed"
        payment.save()

        return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
