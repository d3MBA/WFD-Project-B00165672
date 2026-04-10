from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/passenger/', views.passenger_dashboard, name='passenger_dashboard'),
    path('dashboard/procurement/', views.procurement_dashboard, name='procurement_dashboard'),
    path('dashboard/flight-manager/', views.flight_manager_dashboard, name='flight_manager_dashboard'),
    path('dashboard/crew/', views.crew_dashboard, name='crew_dashboard'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Purchase Orders
    path('purchase-orders/', views.po_list, name='po_list'),
    path('purchase-orders/create/', views.po_create, name='po_create'),
    path('purchase-orders/<int:pk>/', views.po_detail, name='po_detail'),
    path('purchase-orders/<int:pk>/edit/', views.po_edit, name='po_edit'),
    path('purchase-orders/<int:pk>/delete/', views.po_delete, name='po_delete'),
    path('purchase-orders/<int:pk>/status/<str:new_status>/', views.po_change_status, name='po_change_status'),
    path('purchase-orders/items/<int:item_pk>/remove/', views.po_remove_item, name='po_remove_item'),

    # Aircraft
    path('aircraft/', views.aircraft_list, name='aircraft_list'),
    path('aircraft/create/', views.aircraft_create, name='aircraft_create'),
    path('aircraft/<int:pk>/edit/', views.aircraft_edit, name='aircraft_edit'),
    path('aircraft/<int:pk>/delete/', views.aircraft_delete, name='aircraft_delete'),

    # Flights
    path('flights/', views.flight_list, name='flight_list'),
    path('flights/create/', views.flight_create, name='flight_create'),
    path('flights/<int:pk>/', views.flight_detail, name='flight_detail'),
    path('flights/<int:pk>/edit/', views.flight_edit, name='flight_edit'),
    path('flights/<int:pk>/delete/', views.flight_delete, name='flight_delete'),
    path('flights/<int:pk>/status/<str:new_status>/', views.flight_change_status, name='flight_change_status'),

    # Bookings
    path('flights/search/', views.flight_search, name='flight_search'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/<int:pk>/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    # Crew Assignments (flight manager)
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),

    # My Assignments (ground crew)
    path('my-assignments/', views.my_assignments, name='my_assignments'),
    path('my-assignments/<int:pk>/status/<str:new_status>/', views.my_assignment_update_status, name='my_assignment_update_status'),
]
