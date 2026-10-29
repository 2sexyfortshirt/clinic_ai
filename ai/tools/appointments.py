
from appointments.services import (
    book_appointment,
    get_patient_appointments,
    cancel_appointment,
    reschedule_appointment,
)


def create(conversation, slot):
    return book_appointment(
        conversation=conversation,
        doctor_id=slot["doctor_id"],
        appointment_date=slot["date"],
        start_time=slot["start_time"],
        duration_minutes=slot["duration_minutes"],
    )


def my_appointments(conversation):
    return get_patient_appointments(conversation)


def cancel(conversation, appointment_id):
    return cancel_appointment(
        conversation=conversation,
        appointment_id=appointment_id,
    )


def reschedule(
    conversation,
    appointment_id,
    new_date,
    new_time,
):
    return reschedule_appointment(
        conversation=conversation,
        appointment_id=appointment_id,
        new_date=new_date,
        new_start_time=new_time,
    )
