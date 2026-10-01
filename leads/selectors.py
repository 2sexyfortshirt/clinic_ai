from .models import Lead
from django.shortcuts import get_object_or_404


class LeadSelector:
    @staticmethod
    def list_for_clinic(clinic):
        return Lead.objects.filter(clinic=clinic).order_by("-created_at")

    @staticmethod
    def by_id(clinic, lead_id):
        return get_object_or_404(
            Lead,
            clinic=clinic,
            id=lead_id,
        )