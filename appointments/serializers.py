from rest_framework import serializers


from appointments.models import Appointment

class AppointmantSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="lead.name",read_only=True,)
    patient_phone = serializers.CharField(source="lead.phone",read_only=True,)


    class Meta:
        model = Appointment

        fields = [


            "id",
            "clinic",
            "lead",
            "patient_name",
            "patient_phone",
            "scheduled_at",
            "status",
            "notes",
            "created_at",

        ]

        read_only_fields = ["id", "clinic", "lead", "status", "created_at", "patient_name", "patient_phone",]