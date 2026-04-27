from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from main.models import Aircraft, Flight, Booking
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class BookingTransactionTest(TransactionTestCase):
    def test_booking_reduces_seats(self):
        # create user, aircraft, flight
        user = User.objects.create_user(username='txnpassenger', password='password', role='passenger')
        aircraft = Aircraft.objects.create(registration='EI-TXN', aircraft_type='Boeing 737', total_seats=200)
        flight = Flight.objects.create(
            flight_number='SK500',
            aircraft=aircraft,
            origin='Dublin',
            destination='London',
            departure_time=timezone.now() + timedelta(days=3),
            arrival_time=timezone.now() + timedelta(days=3, hours=2),
            available_seats=100,
            status='scheduled'
        )
        # login and book 3 seats
        self.client.login(username='txnpassenger', password='password')
        self.client.post(f'/bookings/create/{flight.pk}/', {'num_seats': 3})
        flight.refresh_from_db()
        self.assertEqual(flight.available_seats, 97)
