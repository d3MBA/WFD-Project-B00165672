from django.contrib import admin
from .models import (
    User, Aircraft, Flight, Supplier, Category,
    PurchaseOrder, PurchaseOrderItem, Booking, CrewAssignment
)

# Register all models in the admin site
admin.site.register(User)
admin.site.register(Aircraft)
admin.site.register(Flight)
admin.site.register(Supplier)
admin.site.register(Category)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(Booking)
admin.site.register(CrewAssignment)
