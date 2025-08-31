from django.core.management.base import BaseCommand
from faker import Faker
from listings.models import Listing, Booking, Review
from django.contrib.auth.models import User
import random

faker = Faker()

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        # Create some users
        for _ in range(5):
            User.objects.create_user(
                username=faker.user_name(),
                email=faker.email(),
                password="password123"
            )

        users = list(User.objects.all())

        # Create Listings
        for _ in range(10):
            listing = Listing.objects.create(
                title=faker.sentence(nb_words=4),
                description=faker.text(),
                price_per_night=random.randint(50, 500),
                location=faker.city(),
            )

            # Create Bookings for each listing
            for _ in range(random.randint(1, 3)):
                Booking.objects.create(
                    listing=listing,
                    user=random.choice(users),
                    start_date=faker.date_this_year(),
                    end_date=faker.date_this_year(),
                )

            # Create Reviews for each listing
        bookings = list(Booking.objects.all())

        for _ in range(random.randint(1, 2)):
            if bookings:  # ensure there is at least one booking
                booking = random.choice(bookings)
                Review.objects.create(
                    booking=booking,                     # matches your model
                    rating=random.randint(1, 5),
                    comment=faker.sentence(),            # optional, blank allowed
                )
                # Remove the booking from the list to respect OneToOne constraint
                bookings.remove(booking)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
