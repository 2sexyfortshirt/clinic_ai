
from datetime import timedelta

from appointments.services import get_available_slots


def find_available_slots_for_date(
    clinic,
    target_date,
    duration=40,
):
    return get_available_slots(
        clinic,
        target_date,
        duration_minutes=duration,
    )


def find_available_dates(
    clinic,
    start_date,
    days=7,
    duration=40,
):
    result = []

    for i in range(days):
        check_date = start_date + timedelta(days=i)

        slots = get_available_slots(
            clinic,
            check_date,
            duration_minutes=duration,
        )

        if slots:
            result.append({
                "date": check_date.isoformat(),
                "slots": slots,
            })

    return result
