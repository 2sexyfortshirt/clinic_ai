from django.contrib import admin
from .models import Clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "is_active",
    )
    search_fields = ("name","phone","email",)



# Register your models here.
