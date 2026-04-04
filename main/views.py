from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import RegistrationForm
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


@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'main/dashboard/admin_dashboard.html')


@login_required
@role_required(['passenger'])
def passenger_dashboard(request):
    return render(request, 'main/dashboard/passenger_dashboard.html')


@login_required
@role_required(['procurement_manager'])
def procurement_dashboard(request):
    return render(request, 'main/dashboard/procurement_dashboard.html')


@login_required
@role_required(['flight_manager'])
def flight_manager_dashboard(request):
    return render(request, 'main/dashboard/flight_manager_dashboard.html')


@login_required
@role_required(['ground_crew'])
def crew_dashboard(request):
    return render(request, 'main/dashboard/crew_dashboard.html')
