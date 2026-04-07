from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Supplier, Category, PurchaseOrder, PurchaseOrderItem, Aircraft, Flight

User = get_user_model()


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_email', 'phone', 'address']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'supplier', 'status', 'notes']


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['category', 'description', 'quantity', 'unit_price']


class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = ['registration', 'aircraft_type', 'total_seats', 'status']


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['flight_number', 'aircraft', 'origin', 'destination', 'departure_time', 'arrival_time', 'available_seats', 'status']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(FlightForm, self).__init__(*args, **kwargs)
        # Format the datetime fields so they show up in the date picker when editing
        if self.instance.pk:
            if self.instance.departure_time:
                self.initial['departure_time'] = self.instance.departure_time.strftime('%Y-%m-%dT%H:%M')
            if self.instance.arrival_time:
                self.initial['arrival_time'] = self.instance.arrival_time.strftime('%Y-%m-%dT%H:%M')
