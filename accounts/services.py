from django.contrib.auth.models import User
from leads.models import Lead
from clinics.models import Clinic
from conversations.models import Conversation

class AccountService:
    @staticmethod
    def register(username,password,clinic_name,email=""):
        user = User.objects.create_user(username=username,password=password,email=email,)
        Clinic.objects.create(owner=user,name=clinic_name,)
        return user



    @staticmethod


    def register_patient(username,password,clinic,name,phone,email="",):
        user = User.objects.create_user(username=username,password=password,email=email,)
        lead = Lead.objects.create(clinic=clinic,user=user,name=name,phone=phone,)
        Conversation.objects.create(lead=lead,is_active=True,)
        return user