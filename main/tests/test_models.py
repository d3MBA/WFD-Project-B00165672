from django.test import TestCase
from django.contrib.auth import get_user_model
from main.models import Aircraft, Flight, Supplier, Category, PurchaseOrder, Booking, CrewAssignment
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user_with_role(self):
        user = User.objects.create_user(username='testuser', password='password', role='passenger')
        self.assertEqual(user.role, 'passenger')

    def test_default_role(self):
        # default role should be passenger
        user = User.objects.create_user(username='testuser2', password='password')
        self.assertEqual(user.role, 'passenger')

    def test_user_str(self):
        user = User.objects.create_user(username='john', password='password')
        self.assertEqual(str(user), 'john')


class AircraftModelTest(TestCase):
    def test_aircraft_str(self):
        aircraft = Aircraft.objects.create(registration='EI-TEST', aircraft_type='Boeing 737', total_seats=200)
        self.assertIn('EI-TEST', str(aircraft))

    def test_aircraft_default_status(self):
        aircraft = Aircraft.objects.create(registration='EI-NEW', aircraft_type='Airbus A320', total_seats=180)
        self.assertEqual(aircraft.status, 'active')


class FlightModelTest(TestCase):
    def test_flight_str(self):
        aircraft = Aircraft.objects.create(registration='EI-FLT', aircraft_type='Airbus A320', total_seats=180)
        flight = Flight.objects.create(
            flight_number='SK999',
            aircraft=aircraft,
            origin='Dublin',
            destination='London',
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2),
            available_seats=180,
            status='scheduled'
        )
        self.assertIn('SK999', str(flight))


class SupplierModelTest(TestCase):
    def test_supplier_str(self):
        supplier = Supplier.objects.create(name='Test Supplier', contact_email='test@test.com')
        self.assertEqual(str(supplier), 'Test Supplier')


class CategoryModelTest(TestCase):
    def test_category_str(self):
        cat = Category.objects.create(name='Engine Parts')
        self.assertEqual(str(cat), 'Engine Parts')


class PurchaseOrderModelTest(TestCase):
    def test_po_str(self):
        supplier = Supplier.objects.create(name='Test Supplier', contact_email='t@t.com')
        user = User.objects.create_user(username='procuser', password='password', role='procurement_manager')
        po = PurchaseOrder.objects.create(po_number='PO-TEST', supplier=supplier, created_by=user)
        self.assertIn('PO-TEST', str(po))


class BookingModelTest(TestCase):
    def test_booking_str(self):
        user = User.objects.create_user(username='passenger1', password='password', role='passenger')
        aircraft = Aircraft.objects.create(registration='EI-BKG', aircraft_type='Boeing 737', total_seats=200)
        flight = Flight.objects.create(
            flight_number='SK100',
            aircraft=aircraft,
            origin='Dublin',
            destination='Paris',
            departure_time=timezone.now() + timedelta(days=5),
            arrival_time=timezone.now() + timedelta(days=5, hours=2),
            available_seats=200,
            status='scheduled'
        )
        booking = Booking.objects.create(passenger=user, flight=flight, num_seats=2)
        self.assertIn('passenger1', str(booking))


class CrewAssignmentModelTest(TestCase):
    def test_assignment_str(self):
        user = User.objects.create_user(username='crew1', password='password', role='ground_crew')
        aircraft = Aircraft.objects.create(registration='EI-CRW', aircraft_type='ATR 72', total_seats=70)
        flight = Flight.objects.create(
            flight_number='SK200',
            aircraft=aircraft,
            origin='Dublin',
            destination='London',
            departure_time=timezone.now() + timedelta(days=2),
            arrival_time=timezone.now() + timedelta(days=2, hours=1),
            available_seats=70,
            status='scheduled'
        )
        assignment = CrewAssignment.objects.create(crew_member=user, flight=flight, task='Baggage Loading')
        self.assertIn('crew1', str(assignment))
