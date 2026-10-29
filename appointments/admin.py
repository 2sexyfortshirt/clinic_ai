from django.contrib import admin
from .models import Appointment,Doctor, DoctorWorkingHours
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "lead",
        "scheduled_at",
        "status",
    )
    list_filter = ("status",)
# Register your models here.

admin.site.register(Doctor)
admin.site.register(DoctorWorkingHours)
