# ALX Travel App

This project is a Django-based travel booking application designed to demonstrate backend engineering concepts such as data modeling, API serialization, and database seeding. It serves as a foundation for building scalable and secure travel-related platforms.

---

## 🌍 Big Picture

The application models the essential entities and relationships needed in a travel booking system:

- **Listings**: Travel accommodations or services available for booking.  
- **Bookings**: Reservations made by users for a specific listing.  
- **Reviews**: Feedback provided by users after completing a booking.  

These components are tied together through **Django models**, **serializers for APIs**, and **seeders for sample data population**.

---

## ⚙️ Key Components

1. **Models**
   - Define the database structure for `Listing`, `Booking`, and `Review`.
   - Relationships: 
     - A `Booking` is linked to a `Listing` and a `User`.
     - A `Review` is tied to a `Booking` (one-to-one).

2. **Serializers**
   - Convert model instances to JSON for API responses.
   - Ensure data validation when creating or updating resources.

3. **Seeders**
   - Populate the database with realistic test data using `Faker`.
   - Automatically generate listings, bookings, and reviews to simulate real-world usage.

---

## 🚀 Usage

1. **Run development server**
   ```bash
   python manage.py runserver
