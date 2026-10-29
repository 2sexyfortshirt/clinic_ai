
from appointments.models import Doctor


def list_doctors(clinic):
    doctors = (
        Doctor.objects
        .filter(
            clinic=clinic,
            is_active=True,
        )
        .order_by("name")
    )

    return [
        {
            "id": str(doctor.id),
            "name": doctor.name,
            "specialty": doctor.specialty,
        }
        for doctor in doctors
    ]
