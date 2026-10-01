from django.contrib import admin
from .models import Appointment
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "lead",
        "scheduled_at",
        "status",
    )
    list_filter = ("status",)
# Register your models here.
