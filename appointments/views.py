from django.utils import timezone

from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from appointments.models import Appointment
from appointments.serializers import AppointmantSerializer

class AppointmentListCreateAPIView(ListCreateAPIView):
    serializer_class = AppointmantSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        clinic = getattr(user, "clinic", None)

        if clinic:
            return Appointment.objects.filter(
                clinic=clinic
            ).select_related("lead")

        return Appointment.objects.filter(
            lead__user=user
        ).select_related("lead")

    def perform_create(self, serializer):
        user = self.request.user
        clinic = getattr(user, "clinic", None)

        if clinic:
            raise serializers.ValidationError(
                "Clinic administrators cannot create appointments through this endpoint yet."
            )

        try:
            lead = user.lead
        except Exception:
            raise serializers.ValidationError(
                "Your account is not linked to a patient profile."
            )

        scheduled_at = serializer.validated_data["scheduled_at"]

        if scheduled_at <= timezone.now():
            raise serializers.ValidationError(
                {"scheduled_at": "Appointment must be scheduled in the future."}
            )

        serializer.save(
            lead=lead,
            clinic=lead.clinic,
        )

from django.shortcuts import render

# Create your views here.
