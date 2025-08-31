from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, ReviewViewSet
from .views import initiate_payment, verify_payment

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),  # keep your ViewSets
    path("payments/initiate/<int:booking_id>/", initiate_payment, name="initiate-payment"),
    path("payments/verify/<uuid:reference>/", verify_payment, name="verify-payment"),
]

