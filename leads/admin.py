from django.contrib import admin
from .models import Lead


# Register your models here.
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "clinic",
        "status",
        "created_at",
    )
    list_filter = ("clinic","status",)

    search_fields = ("name","phone",)
