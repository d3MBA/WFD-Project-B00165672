from django.test import TestCase
from django.contrib.auth import get_user_model
from main.models import Supplier, Aircraft, Flight, Booking
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class SupplierUseCaseTest(TestCase):
    def test_procurement_creates_supplier(self):
        user = User.objects.create_user(username='proc_uc', password='password', role='procurement_manager')
        self.client.login(username='proc_uc', password='password')
        response = self.client.post('/suppliers/create/', {
            'name': 'New Supplier',
            'contact_email': 'supplier@test.com',
            'phone': '123456',
            'address': '123 Test St'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Supplier.objects.filter(name='New Supplier').exists())


class AircraftUseCaseTest(TestCase):
    def test_flight_manager_creates_aircraft(self):
        user = User.objects.create_user(username='fm_uc', password='password', role='flight_manager')
        self.client.login(username='fm_uc', password='password')
        response = self.client.post('/aircraft/create/', {
            'registration': 'EI-UC1',
            'aircraft_type': 'Boeing 737',
            'total_seats': 200,
            'status': 'active'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Aircraft.objects.filter(registration='EI-UC1').exists())


class BookingUseCaseTest(TestCase):
    def test_book_and_cancel(self):
        # setup
        passenger = User.objects.create_user(username='pax_uc', password='password', role='passenger')
        aircraft = Aircraft.objects.create(registration='EI-UC2', aircraft_type='Airbus A320', total_seats=180)
        flight = Flight.objects.create(
            flight_number='SK777',
            aircraft=aircraft,
            origin='Dublin',
            destination='Amsterdam',
            departure_time=timezone.now() + timedelta(days=7),
            arrival_time=timezone.now() + timedelta(days=7, hours=3),
            available_seats=50,
            status='scheduled'
        )

        # book 2 seats
        self.client.login(username='pax_uc', password='password')
        self.client.post(f'/bookings/create/{flight.pk}/', {'num_seats': 2})
        flight.refresh_from_db()
        self.assertEqual(flight.available_seats, 48)

        # now cancel it
        booking = Booking.objects.get(passenger=passenger, flight=flight)
        self.client.post(f'/bookings/{booking.pk}/cancel/')
        flight.refresh_from_db()
        self.assertEqual(flight.available_seats, 50)
