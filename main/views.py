from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from .forms import (
    RegistrationForm, SupplierForm, CategoryForm,
    PurchaseOrderForm, PurchaseOrderItemForm,
    AircraftForm, FlightForm,
    FlightSearchForm, BookingForm,
    CrewAssignmentForm
)
from .models import Supplier, Category, PurchaseOrder, PurchaseOrderItem, Aircraft, Flight, Booking, CrewAssignment
from .decorators import role_required

User = get_user_model()


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
            messages.success(request, 'Account created successfully!')
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


# dashboards

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_passengers': User.objects.filter(role='passenger').count(),
        'total_flights': Flight.objects.count(),
        'scheduled_flights': Flight.objects.filter(status='scheduled').count(),
        'total_bookings': Booking.objects.count(),
        'confirmed_bookings': Booking.objects.filter(status='confirmed').count(),
        'total_pos': PurchaseOrder.objects.count(),
        'total_aircraft': Aircraft.objects.count(),
        'active_aircraft': Aircraft.objects.filter(status='active').count(),
        'total_assignments': CrewAssignment.objects.count(),
    }
    return render(request, 'main/dashboard/admin_dashboard.html', context)


@login_required
@role_required(['passenger'])
def passenger_dashboard(request):
    confirmed_count = Booking.objects.filter(passenger=request.user, status='confirmed').count()
    cancelled_count = Booking.objects.filter(passenger=request.user, status='cancelled').count()
    # get next upcoming flight
    next_booking = Booking.objects.filter(
        passenger=request.user,
        status='confirmed',
        flight__departure_time__gt=timezone.now()
    ).order_by('flight__departure_time').first()
    context = {
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
        'next_booking': next_booking,
    }
    return render(request, 'main/dashboard/passenger_dashboard.html', context)


@login_required
@role_required(['procurement_manager'])
def procurement_dashboard(request):
    context = {
        'draft_count': PurchaseOrder.objects.filter(status='draft').count(),
        'submitted_count': PurchaseOrder.objects.filter(status='submitted').count(),
        'approved_count': PurchaseOrder.objects.filter(status='approved').count(),
        'received_count': PurchaseOrder.objects.filter(status='received').count(),
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
        'total_assignments': CrewAssignment.objects.count(),
    }
    return render(request, 'main/dashboard/flight_manager_dashboard.html', context)


@login_required
@role_required(['ground_crew'])
def crew_dashboard(request):
    my_assignments = CrewAssignment.objects.filter(crew_member=request.user)
    context = {
        'assigned_count': my_assignments.filter(status='assigned').count(),
        'in_progress_count': my_assignments.filter(status='in_progress').count(),
        'completed_count': my_assignments.filter(status='completed').count(),
        'upcoming': my_assignments.filter(
            status__in=['assigned', 'in_progress'],
            flight__departure_time__gt=timezone.now()
        ).order_by('flight__departure_time')[:5],
    }
    return render(request, 'main/dashboard/crew_dashboard.html', context)


# helper
def recalculate_po_total(po):
    total = 0
    for item in po.items.all():
        total += item.quantity * item.unit_price
    po.total_amount = total
    po.save()


# suppliers

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
            messages.success(request, 'Supplier created.')
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
            messages.success(request, 'Supplier updated.')
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
        messages.success(request, 'Supplier deleted.')
        return redirect('supplier_list')
    return render(request, 'main/suppliers/supplier_delete.html', {'supplier': supplier})


# categories

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
            messages.success(request, 'Category created.')
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
            messages.success(request, 'Category updated.')
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
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'main/categories/category_delete.html', {'category': category})


# purchase orders

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
            messages.success(request, 'Purchase order created.')
            return redirect('po_detail', pk=po.pk)
    else:
        form = PurchaseOrderForm()
    return render(request, 'main/purchase_orders/po_form.html', {'form': form, 'title': 'Create Purchase Order'})

@login_required
@role_required(['admin', 'procurement_manager'])
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    items = po.items.all()

    if request.method == 'POST':
        item_form = PurchaseOrderItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.purchase_order = po
            item.save()
            recalculate_po_total(po)
            messages.success(request, 'Item added.')
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
            messages.success(request, 'Purchase order updated.')
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
        messages.success(request, 'Purchase order deleted.')
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
        messages.success(request, 'Item removed.')
    return redirect('po_detail', pk=po.pk)

@login_required
@role_required(['admin', 'procurement_manager'])
def po_change_status(request, pk, new_status):
    po = get_object_or_404(PurchaseOrder, pk=pk)
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


# aircraft

@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_list(request):
    aircraft = Aircraft.objects.all()
    return render(request, 'main/aircraft/aircraft_list.html', {'aircraft': aircraft})

@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_create(request):
    if request.method == 'POST':
        form = AircraftForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aircraft added.')
            return redirect('aircraft_list')
    else:
        form = AircraftForm()
    return render(request, 'main/aircraft/aircraft_form.html', {'form': form, 'title': 'Add Aircraft'})

@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_edit(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    if request.method == 'POST':
        form = AircraftForm(request.POST, request.FILES, instance=aircraft)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aircraft updated.')
            return redirect('aircraft_list')
    else:
        form = AircraftForm(instance=aircraft)
    return render(request, 'main/aircraft/aircraft_form.html', {'form': form, 'title': 'Edit Aircraft'})

@login_required
@role_required(['admin', 'flight_manager'])
def aircraft_delete(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    if request.method == 'POST':
        aircraft.delete()
        messages.success(request, 'Aircraft deleted.')
        return redirect('aircraft_list')
    return render(request, 'main/aircraft/aircraft_delete.html', {'aircraft': aircraft})


# flights

@login_required
@role_required(['admin', 'flight_manager'])
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'main/flights/flight_list.html', {'flights': flights})

@login_required
@role_required(['admin', 'flight_manager'])
def flight_create(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight created.')
            return redirect('flight_list')
    else:
        form = FlightForm()
    return render(request, 'main/flights/flight_form.html', {'form': form, 'title': 'Add Flight'})

@login_required
@role_required(['admin', 'flight_manager'])
def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, 'main/flights/flight_detail.html', {'flight': flight})

@login_required
@role_required(['admin', 'flight_manager'])
def flight_edit(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight updated.')
            return redirect('flight_detail', pk=flight.pk)
    else:
        form = FlightForm(instance=flight)
    return render(request, 'main/flights/flight_form.html', {'form': form, 'title': 'Edit Flight'})

@login_required
@role_required(['admin', 'flight_manager'])
def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        flight.delete()
        messages.success(request, 'Flight deleted.')
        return redirect('flight_list')
    return render(request, 'main/flights/flight_delete.html', {'flight': flight})

@login_required
@role_required(['admin', 'flight_manager'])
def flight_change_status(request, pk, new_status):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
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


# flight search - public, no login needed
def flight_search(request):
    form = FlightSearchForm(request.GET or None)
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


# bookings

@login_required
@role_required(['passenger', 'admin'])
def booking_create(request, pk):
    flight = get_object_or_404(Flight, pk=pk)

    # cant book if flight isnt scheduled or no seats or already departed
    if flight.status != 'scheduled' or flight.available_seats <= 0 or flight.departure_time <= timezone.now():
        messages.error(request, 'This flight is not available for booking.')
        return redirect('flight_search')

    error = None
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            num_seats = form.cleaned_data['num_seats']
            if num_seats > flight.available_seats:
                messages.error(request, 'Not enough available seats.')
                error = 'Not enough available seats.'
            else:
                booking = Booking()
                booking.passenger = request.user
                booking.flight = flight
                booking.num_seats = num_seats
                booking.save()
                flight.available_seats = flight.available_seats - num_seats
                flight.save()
                messages.success(request, 'Booking confirmed!')
                return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'main/bookings/booking_create.html', {
        'form': form,
        'flight': flight,
        'error': error,
    })

@login_required
@role_required(['passenger', 'admin'])
def booking_list(request):
    if request.user.role == 'admin':
        bookings = Booking.objects.all().order_by('-booking_date')
    else:
        bookings = Booking.objects.filter(passenger=request.user).order_by('-booking_date')
    return render(request, 'main/bookings/booking_list.html', {'bookings': bookings})

@login_required
@role_required(['passenger', 'admin'])
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # passengers can only view their own bookings
    if request.user.role == 'passenger' and booking.passenger != request.user:
        return redirect('booking_list')
    return render(request, 'main/bookings/booking_detail.html', {'booking': booking})

@login_required
@role_required(['passenger', 'admin'])
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # passengers can only cancel their own
    if request.user.role == 'passenger' and booking.passenger != request.user:
        return redirect('booking_list')
    # cant cancel if already cancelled
    if booking.status == 'cancelled':
        messages.error(request, 'This booking is already cancelled.')
        return redirect('booking_list')

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        # add seats back to the flight
        booking.flight.available_seats = booking.flight.available_seats + booking.num_seats
        booking.flight.save()
        messages.success(request, 'Booking cancelled.')
        return redirect('booking_list')
    return render(request, 'main/bookings/booking_cancel.html', {'booking': booking})


# crew assignments (flight manager manages these)

@login_required
@role_required(['admin', 'flight_manager'])
def assignment_list(request):
    assignments = CrewAssignment.objects.all().order_by('-assigned_date')
    return render(request, 'main/assignments/assignment_list.html', {'assignments': assignments})

@login_required
@role_required(['admin', 'flight_manager'])
def assignment_create(request):
    if request.method == 'POST':
        form = CrewAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment created.')
            return redirect('assignment_list')
    else:
        form = CrewAssignmentForm()
    return render(request, 'main/assignments/assignment_form.html', {'form': form, 'title': 'Add Assignment'})

@login_required
@role_required(['admin', 'flight_manager'])
def assignment_edit(request, pk):
    assignment = get_object_or_404(CrewAssignment, pk=pk)
    if request.method == 'POST':
        form = CrewAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated.')
            return redirect('assignment_list')
    else:
        form = CrewAssignmentForm(instance=assignment)
    return render(request, 'main/assignments/assignment_form.html', {'form': form, 'title': 'Edit Assignment'})

@login_required
@role_required(['admin', 'flight_manager'])
def assignment_delete(request, pk):
    assignment = get_object_or_404(CrewAssignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted.')
        return redirect('assignment_list')
    return render(request, 'main/assignments/assignment_delete.html', {'assignment': assignment})


# ground crew - my assignments

@login_required
@role_required(['ground_crew'])
def my_assignments(request):
    assignments = CrewAssignment.objects.filter(crew_member=request.user).order_by('-assigned_date')
    return render(request, 'main/assignments/my_assignments.html', {'assignments': assignments})

@login_required
@role_required(['ground_crew'])
def my_assignment_update_status(request, pk, new_status):
    assignment = get_object_or_404(CrewAssignment, pk=pk)
    # make sure its their assignment
    if assignment.crew_member != request.user:
        return redirect('my_assignments')
    if request.method == 'POST':
        if assignment.status == 'assigned' and new_status == 'in_progress':
            assignment.status = 'in_progress'
            assignment.save()
        elif assignment.status == 'in_progress' and new_status == 'completed':
            assignment.status = 'completed'
            assignment.save()
    return redirect('my_assignments')
