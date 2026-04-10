from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Supplier, Category, PurchaseOrder, PurchaseOrderItem, Aircraft, Flight, CrewAssignment

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


#search form for finding flights
class FlightSearchForm(forms.Form):
    origin = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'From (e.g. Dublin)'})
    )
    destination = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'To (e.g. London)'})
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


# form for booking seats on a flight
class BookingForm(forms.Form):
    num_seats = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


# form for assigning crew to flights
class CrewAssignmentForm(forms.ModelForm):
    class Meta:
        model = CrewAssignment
        fields = ['crew_member', 'flight', 'task', 'status']

    def __init__(self, *args, **kwargs):
        super(CrewAssignmentForm, self).__init__(*args, **kwargs)
        # only show ground crew users in the dropdown
        self.fields['crew_member'].queryset = get_user_model().objects.filter(role='ground_crew')
        # only show scheduled or boarding flights
        self.fields['flight'].queryset = Flight.objects.filter(status__in=['scheduled', 'boarding'])
