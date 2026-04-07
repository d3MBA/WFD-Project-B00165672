from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum, F
from django.utils import timezone
from .forms import (
    RegistrationForm, SupplierForm, CategoryForm,
    PurchaseOrderForm, PurchaseOrderItemForm,
    AircraftForm, FlightForm,
    FlightSearchForm, BookingForm
)
from .models import Supplier, Category, PurchaseOrder, PurchaseOrderItem, Aircraft, Flight, Booking
from .decorators import role_required


def home(request):
    if request.user.is_authenticated:
        role = request.user.role
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'passenger':
            return redirect('passenger_dashboard')
        elif role == 'procurement_manager':
            return redirect('procurement_dashboard')
        elif role == 'flight_manager':
            return redirect('flight_manager_dashboard')
        elif role == 'ground_crew':
            return redirect('crew_dashboard')
    return render(request, 'main/home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = 'Invalid username or password'
    return render(request, 'main/login.html', {'error': error})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')


# ---- Dashboards ----

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'main/dashboard/admin_dashboard.html')


@login_required
@role_required(['passenger'])
def passenger_dashboard(request):
    confirmed_count = Booking.objects.filter(passenger=request.user, status='confirmed').count()
    cancelled_count = Booking.objects.filter(passenger=request.user, status='cancelled').count()
    context = {
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
    }
    return render(request, 'main/dashboard/passenger_dashboard.html', context)


@login_required
@role_required(['procurement_manager'])
def procurement_dashboard(request):
    draft_count = PurchaseOrder.objects.filter(status='draft').count()
    submitted_count = PurchaseOrder.objects.filter(status='submitted').count()
    approved_count = PurchaseOrder.objects.filter(status='approved').count()
    received_count = PurchaseOrder.objects.filter(status='received').count()
    context = {
        'draft_count': draft_count,
        'submitted_count': submitted_count,
        'approved_count': approved_count,
        'received_count': received_count,
    }
    return render(request, 'main/dashboard/procurement_dashboard.html', context)


@login_required
@role_required(['flight_manager'])
def flight_manager_dashboard(request):
    context = {
        'scheduled_count': Flight.objects.filter(status='scheduled').count(),
        'boarding_count': Flight.objects.filter(status='boarding').count(),
        'departed_count': Flight.objects.filter(status='departed').count(),
        'arrived_count': Flight.objects.filter(status='arrived').count(),
        'cancelled_count': Flight.objects.filter(status='cancelled').count(),
        'active_aircraft': Aircraft.objects.filter(status='active').count(),
        'maintenance_aircraft': Aircraft.objects.filter(status='maintenance').count(),
        'retired_aircraft': Aircraft.objects.filter(status='retired').count(),
    }
    return render(request, 'main/dashboard/flight_manager_dashboard.html', context)


@login_required
@role_required(['ground_crew'])
def crew_dashboard(request):
    return render(request, 'main/dashboard/crew_dashboard.html')


# ---- Helper function ----

def recalculate_po_total(po):
    total = po.items.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0
    po.total_amount = total
    po.save()


# ---- Supplier CRUD ----

@login_required
@role_required(['admin', 'procurement_manager'])
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'main/suppliers/supplier_list.html', {'suppliers': suppliers})


@login_required
@role_required(['admin', 'procurement_manager'])
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'main/suppliers/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


@login_required
@role_required(['admin', 'procurement_manager'])
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'main/suppliers/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})


@login_required
@role_required(['admin', 'procurement_manager'])
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'main/suppliers/supplier_delete.html', {'supplier': supplier})


# ---- Category CRUD ----

@login_required
@role_required(['admin', 'procurement_manager'])
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'main/categories/category_list.html', {'categories': categories})


@login_required
@role_required(['admin', 'procurement_manager'])
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'main/categories/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
@role_required(['admin', 'procurement_manager'])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'main/categories/category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
@role_required(['admin', 'procurement_manager'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'main/categories/category_delete.html', {'category': category})


# ---- Purchase Order CRUD ----

@login_required
@role_required(['admin', 'procurement_manager'])
def po_list(request):
    purchase_orders = PurchaseOrder.objects.all().order_by('-created_date')
    return render(request, 'main/purchase_orders/po_list.html', {'purchase_orders': purchase_orders})


@login_required
@role_required(['admin', 'procurement_manager'])
def po_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save(commit=False)
            po.created_by = request.user
            po.save()
            return redirect('po_detail', pk=po.pk)
    else:
        form = PurchaseOrderForm()
    return render(request, 'main/purchase_orders/po_form.html', {'form': form, 'title': 'Create Purchase Order'})


@login_required
@role_required(['admin', 'procurement_manager'])
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    items = po.items.all()

    # Handle adding a new item
    if request.method == 'POST':
        item_form = PurchaseOrderItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.purchase_order = po
            item.save()
            recalculate_po_total(po)
            return redirect('po_detail', pk=po.pk)
    else:
        item_form = PurchaseOrderItemForm()

    context = {
        'po': po,
        'items': items,
        'item_form': item_form,
    }
    return render(request, 'main/purchase_orders/po_detail.html', context)


@login_required
@role_required(['admin', 'procurement_manager'])
def po_edit(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=po)
        if form.is_valid():
            form.save()
            return redirect('po_detail', pk=po.pk)
    else:
        form = PurchaseOrderForm(instance=po)
    return render(request, 'main/purchase_orders/po_form.html', {'form': form, 'title': 'Edit Purchase Order'})


@login_required
@role_required(['admin', 'procurement_manager'])
def po_delete(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        po.delete()
        return redirect('po_list')
    return render(request, 'main/purchase_orders/po_delete.html', {'po': po})


@login_required
@role_required(['admin', 'procurement_manager'])
def po_remove_item(request, item_pk):
    item = get_object_or_404(PurchaseOrderItem, pk=item_pk)
    po = item.purchase_order
    if request.method == 'POST':
        item.delete()
        recalculate_po_total(po)
    return redirect('po_detail', pk=po.pk)


@login_required
@role_required(['admin', 'procurement_manager'])
def po_change_status(request, pk, new_status):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    # Only allow valid status transitions
    valid_transitions = {
        'draft': 'submitted',
        'submitted': 'approved',
        'approved': 'received',
    }

    if request.method == 'POST':
        if valid_transitions.get(po.status) == new_status:
            po.status = new_status
            po.save()

    return redirect('po_detail', pk=po.pk)


# ---- Aircraft CRUD ----

# Show all aircraft in a table
@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_list(request):
    aircraft = Aircraft.objects.all()
    return render(request, 'main/aircraft/aircraft_list.html', {'aircraft': aircraft})


# Create a new aircraft
@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_create(request):
    if request.method == 'POST':
        form = AircraftForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('aircraft_list')
    else:
        form = AircraftForm()
    return render(request, 'main/aircraft/aircraft_form.html', {'form': form, 'title': 'Add Aircraft'})


# Edit an existing aircraft
@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_edit(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    if request.method == 'POST':
        form = AircraftForm(request.POST, instance=aircraft)
        if form.is_valid():
            form.save()
            return redirect('aircraft_list')
    else:
        form = AircraftForm(instance=aircraft)
    return render(request, 'main/aircraft/aircraft_form.html', {'form': form, 'title': 'Edit Aircraft'})


# Delete an aircraft
@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_delete(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    if request.method == 'POST':
        aircraft.delete()
        return redirect('aircraft_list')
    return render(request, 'main/aircraft/aircraft_delete.html', {'aircraft': aircraft})


# ---- Flight CRUD ----

# Show all flights in a table
@login_required
@role_required(['admin', 'flight_manager'])
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'main/flights/flight_list.html', {'flights': flights})


# Create a new flight
@login_required
@role_required(['admin', 'flight_manager'])
def flight_create(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flight_list')
    else:
        form = FlightForm()
    return render(request, 'main/flights/flight_form.html', {'form': form, 'title': 'Add Flight'})


# Show details for one flight
@login_required
@role_required(['admin', 'flight_manager'])
def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, 'main/flights/flight_detail.html', {'flight': flight})


# Edit a flight
@login_required
@role_required(['admin', 'flight_manager'])
def flight_edit(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('flight_detail', pk=flight.pk)
    else:
        form = FlightForm(instance=flight)
    return render(request, 'main/flights/flight_form.html', {'form': form, 'title': 'Edit Flight'})


# Delete a flight
@login_required
@role_required(['admin', 'flight_manager'])
def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        flight.delete()
        return redirect('flight_list')
    return render(request, 'main/flights/flight_delete.html', {'flight': flight})


# Change flight status
@login_required
@role_required(['admin', 'flight_manager'])
def flight_change_status(request, pk, new_status):
    flight = get_object_or_404(Flight, pk=pk)

    if request.method == 'POST':
        # only allow valid transitions
        if flight.status == 'scheduled' and new_status == 'boarding':
            flight.status = 'boarding'
            flight.save()
        elif flight.status == 'scheduled' and new_status == 'cancelled':
            flight.status = 'cancelled'
            flight.save()
        elif flight.status == 'boarding' and new_status == 'departed':
            flight.status = 'departed'
            flight.save()
        elif flight.status == 'departed' and new_status == 'arrived':
            flight.status = 'arrived'
            flight.save()

    return redirect('flight_detail', pk=flight.pk)


#booking views

# search for available flights (anyone can use this no login needed)
def flight_search(request):
    form = FlightSearchForm(request.GET or None)
    # only show scheduled flights with seats available in the future
    flights = Flight.objects.filter(
        status='scheduled',
        available_seats__gt=0,
        departure_time__gt=timezone.now()
    )

    if form.is_valid():
        origin = form.cleaned_data.get('origin')
        destination = form.cleaned_data.get('destination')
        date = form.cleaned_data.get('date')
        if origin:
            flights = flights.filter(origin__icontains=origin)
        if destination:
            flights = flights.filter(destination__icontains=destination)
        if date:
            flights = flights.filter(departure_time__date=date)

    return render(request, 'main/bookings/flight_search.html', {
        'form': form,
        'flights': flights,
    })


#book seats on a flight
@login_required
@role_required(['passenger', 'admin'])
def booking_create(request, pk):
    flight = get_object_or_404(Flight, pk=pk)

    # check if flight can be booked
    if flight.status != 'scheduled' or flight.available_seats <= 0 or flight.departure_time <= timezone.now():
        return redirect('flight_search')

    error = None

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            num_seats = form.cleaned_data['num_seats']
            # check there are enough seats
            if num_seats > flight.available_seats:
                error = 'Not enough available seats'
            else:
                # create the booking
                booking = Booking()
                booking.passenger = request.user
                booking.flight = flight
                booking.num_seats = num_seats
                booking.save()
                # reduce available seats on the flight
                flight.available_seats = flight.available_seats - num_seats
                flight.save()
                return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'main/bookings/booking_create.html', {
        'form': form,
        'flight': flight,
        'error': error,
    })


#show list of bookings
@login_required
@role_required(['passenger', 'admin'])
def booking_list(request):
    # admin sees all bookings, passenger sees only their own
    if request.user.role == 'admin':
        bookings = Booking.objects.all().order_by('-booking_date')
    else:
        bookings = Booking.objects.filter(passenger=request.user).order_by('-booking_date')

    return render(request, 'main/bookings/booking_list.html', {
        'bookings': bookings,
    })


# show booking details
@login_required
@role_required(['passenger', 'admin'])
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    # passengers can only see their own bookings
    if request.user.role == 'passenger' and booking.passenger != request.user:
        return redirect('booking_list')

    return render(request, 'main/bookings/booking_detail.html', {
        'booking': booking,
    })


# cancel a booking
@login_required
@role_required(['passenger', 'admin'])
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    # passengers can only cancel their own bookings
    if request.user.role == 'passenger' and booking.passenger != request.user:
        return redirect('booking_list')

    if request.method == 'POST':
        # cancel the booking and add seats back
        booking.status = 'cancelled'
        booking.save()
        booking.flight.available_seats = booking.flight.available_seats + booking.num_seats
        booking.flight.save()
        return redirect('booking_list')

    return render(request, 'main/bookings/booking_cancel.html', {
        'booking': booking,
    })
