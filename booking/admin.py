from django.contrib import admin
from .models import User, Turf, Slot, Booking

admin.site.register(User)
admin.site.register(Turf)
admin.site.register(Booking)

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Runs model validation
        super().save_model(request, obj, form, change)