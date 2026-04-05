from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model with roles
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('passenger', 'Passenger'),
        ('procurement_manager', 'Procurement Manager'),
        ('flight_manager', 'Flight Manager'),
        ('ground_crew', 'Ground Crew'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='passenger')

    def __str__(self):
        return self.username


# Aircraft in the airline fleet
class Aircraft(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
    ]
    registration = models.CharField(max_length=20, unique=True)
    aircraft_type = models.CharField(max_length=100)
    total_seats = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.registration} - {self.aircraft_type}"


# Flight information
class Flight(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('arrived', 'Arrived'),
        ('cancelled', 'Cancelled'),
    ]
    flight_number = models.CharField(max_length=20)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    available_seats = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"{self.flight_number} - {self.origin} to {self.destination}"


# Supplier for purchase orders
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Category for purchase order items
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


# Purchase Order
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('received', 'Received'),
    ]
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.po_number


# Individual items in a purchase order
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} for {self.purchase_order.po_number}"


# Passenger booking for a flight
class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    num_seats = models.IntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')

    def __str__(self):
        return f"{self.passenger.username} - {self.flight.flight_number}"


# Crew assignment to a flight
class CrewAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    crew_member = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crew_member.username} - {self.flight.flight_number} - {self.task}"
