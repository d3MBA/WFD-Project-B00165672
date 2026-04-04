from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/passenger/', views.passenger_dashboard, name='passenger_dashboard'),
    path('dashboard/procurement/', views.procurement_dashboard, name='procurement_dashboard'),
    path('dashboard/flight-manager/', views.flight_manager_dashboard, name='flight_manager_dashboard'),
    path('dashboard/crew/', views.crew_dashboard, name='crew_dashboard'),
]
