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
]
