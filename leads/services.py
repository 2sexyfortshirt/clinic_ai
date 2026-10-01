from .models import Lead

class LeadService:
    @staticmethod
    def get_or_create(clinic,**kwargs):
        return Lead.objects.create(clinic=clinic, **kwargs)
