from django.contrib.auth.models import User
from rest_framework import serializers
from accounts.services import AccountService

from clinics.models import Clinic

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    clinic_name = serializers.CharField(max_length=255)
    def create(self, validated_data):
        return AccountService.register(**validated_data)



class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    clinic = serializers.CharField()

class PatientRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=50)

    def create(self, validated_data):
        clinic = self.context["clinic"]

        return AccountService.register_patient(
            clinic=clinic,
            **validated_data,
        )
