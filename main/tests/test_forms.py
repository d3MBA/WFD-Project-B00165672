from django.test import SimpleTestCase
from main.forms import FlightSearchForm, BookingForm


class FlightSearchFormTest(SimpleTestCase):
    # search form - all fields optional so empty should be valid
    def test_empty_form_is_valid(self):
        form = FlightSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_with_origin(self):
        form = FlightSearchForm(data={'origin': 'Dublin', 'destination': '', 'date': ''})
        self.assertTrue(form.is_valid())


class BookingFormTest(SimpleTestCase):
    def test_valid_seats(self):
        form = BookingForm(data={'num_seats': 2})
        self.assertTrue(form.is_valid())

    def test_zero_seats_invalid(self):
        form = BookingForm(data={'num_seats': 0})
        self.assertFalse(form.is_valid())

    def test_too_many_seats(self):
        # max is 10
        form = BookingForm(data={'num_seats': 11})
        self.assertFalse(form.is_valid())

    def test_one_seat(self):
        form = BookingForm(data={'num_seats': 1})
        self.assertTrue(form.is_valid())
