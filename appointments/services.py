
from datetime import datetime, time,date, timedelta

from django.utils import timezone
from django.db import transaction

from .models import Appointment, Doctor, DoctorWorkingHours


def get_available_slots(clinic, date, duration_minutes=40, step_minutes=15):
    """
    Возвращает свободные интервалы всех активных врачей
    клиники на указанную дату.
    date — объект datetime.date.
    """

    if duration_minutes < 15 or duration_minutes > 60:
        raise ValueError("Duration must be between 15 and 60 minutes.")

    if step_minutes <= 0:
        raise ValueError("Step must be positive.")

    weekday = date.weekday()
    now = timezone.localtime()

    doctors = (
        Doctor.objects.filter(clinic=clinic, is_active=True)
        .prefetch_related("working_hours")
        .order_by("name")
    )

    result = []

    for doctor in doctors:
        working_hours = doctor.working_hours.filter(
            weekday=weekday,
            is_day_off=False,
        ).first()

        if not working_hours:
            continue

        start_dt = timezone.make_aware(
            datetime.combine(date, working_hours.start_time)
        )
        end_dt = timezone.make_aware(
            datetime.combine(date, working_hours.end_time)
        )

        if end_dt <= start_dt:
            continue

        appointments = Appointment.objects.filter(
            clinic=clinic,
            doctor=doctor,
            scheduled_at__lt=end_dt,
            status__in=["pending", "confirmed"],
        ).filter(
            scheduled_at__gte=start_dt - timedelta(hours=24),
        ).order_by("scheduled_at")

        busy_intervals = []

        for appointment in appointments:
            appointment_end = appointment.scheduled_at + timedelta(
                minutes=appointment.duration_minutes
            )
            if appointment.scheduled_at < end_dt and appointment_end > start_dt:
                busy_intervals.append(
                    (appointment.scheduled_at, appointment_end)
                )

        slot_start = start_dt

        while slot_start + timedelta(minutes=duration_minutes) <= end_dt:
            slot_end = slot_start + timedelta(minutes=duration_minutes)

            if date == now.date() and slot_start <= now:
                slot_start += timedelta(minutes=step_minutes)
                continue

            overlaps = any(
                slot_start < busy_end and slot_end > busy_start
                for busy_start, busy_end in busy_intervals
            )

            if not overlaps:
                result.append({
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.name,
                    "specialty": doctor.specialty,
                    "date": date.isoformat(),
                    "start_time": slot_start.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M"),
                    "duration_minutes": duration_minutes,
                })

            slot_start += timedelta(minutes=step_minutes)

    return result

@transaction.atomic
def book_appointment(
    conversation,
    doctor_id,
    appointment_date,
    start_time,
    duration_minutes=40,
):
    if conversation.pending_action in ("reschedule", "cancel"):
        return {
            "success": False,
            "message": (
                "Сейчас обрабатывается изменение существующей записи. "
                "Не создавай новую запись через book_appointment."
            ),
        }
    lead = conversation.lead
    clinic = lead.clinic

    if not 15 <= duration_minutes <= 60:
        return {
            "success": False,
            "message": "Длительность должна быть от 15 до 60 минут.",
        }

    try:
        selected_date = date.fromisoformat(appointment_date)
        selected_time = time.fromisoformat(start_time)
    except (ValueError, TypeError):
        return {
            "success": False,
            "message": "Некорректные дата или время.",
        }

    doctor = (
        Doctor.objects.select_for_update()
        .filter(
            id=doctor_id,
            clinic=clinic,
            is_active=True,
        )
        .first()
    )

    if doctor is None:
        return {
            "success": False,
            "message": "Врач не найден или недоступен.",
        }

    available_slots = get_available_slots(
        clinic,
        selected_date,
        duration_minutes=duration_minutes,
    )

    selected_slot = next(
        (
            slot
            for slot in available_slots
            if str(slot["doctor_id"]) == str(doctor.id)
            and slot["start_time"] == selected_time.strftime("%H:%M")
        ),
        None,
    )

    if selected_slot is None:
        return {
            "success": False,
            "message": (
                "Это время уже недоступно. "
                "Нужно предложить пациенту актуальные свободные окна."
            ),
        }

    scheduled_at = timezone.make_aware(
        datetime.combine(selected_date, selected_time)
    )

    appointment = Appointment.objects.create(
        clinic=clinic,
        lead=lead,
        doctor=doctor,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        status="pending",
    )

    return {
        "success": True,
        "appointment_id": str(appointment.id),
        "doctor_name": doctor.name,
        "specialty": doctor.specialty,
        "date": selected_date.isoformat(),
        "start_time": selected_slot["start_time"],
        "end_time": selected_slot["end_time"],
        "status": appointment.status,
    }


def get_patient_appointments(conversation):
    """Возвращает будущие активные записи пациента из текущей беседы."""
    now = timezone.now()

    appointments = (
        Appointment.objects.filter(
            clinic=conversation.lead.clinic,
            lead=conversation.lead,
            status__in=["pending", "confirmed"],
            scheduled_at__gte=now,
        )
        .select_related("doctor")
        .order_by("scheduled_at")
    )

    result = []

    for appointment in appointments:
        local_dt = timezone.localtime(appointment.scheduled_at)

        result.append({
            "appointment_id": str(appointment.id),
            "doctor_id": (
                str(appointment.doctor_id)
                if appointment.doctor_id else None
            ),
            "doctor_name": (
                appointment.doctor.name
                if appointment.doctor else "Врач не указан"
            ),
            "date": local_dt.date().isoformat(),
            "start_time": local_dt.strftime("%H:%M"),
            "duration_minutes": appointment.duration_minutes,
            "status": appointment.status,
        })

    return result


@transaction.atomic
def cancel_appointment(conversation, appointment_id):
    """Отменяет только запись текущего пациента."""
    appointment = (
        Appointment.objects.select_for_update()
        .filter(
            id=appointment_id,
            clinic=conversation.lead.clinic,
            lead=conversation.lead,
        )
        .first()
    )

    if appointment is None:
        return {
            "success": False,
            "message": "Запись не найдена.",
        }

    if appointment.status not in ["pending", "confirmed"]:
        return {
            "success": False,
            "message": "Эту запись нельзя отменить: она уже не активна.",
        }

    if appointment.scheduled_at <= timezone.now():
        return {
            "success": False,
            "message": "Прошедшую запись нельзя отменить через чат.",
        }

    appointment.status = "cancelled"
    appointment.save()

    local_dt = timezone.localtime(appointment.scheduled_at)

    return {
        "success": True,
        "appointment_id": str(appointment.id),
        "message": (
            f"Запись на {local_dt:%d.%m.%Y} "
            f"в {local_dt:%H:%M} отменена."
        ),
    }


@transaction.atomic
def reschedule_appointment(
    conversation,
    appointment_id,
    new_date,
    new_start_time,
):
    """Переносит существующую запись без создания дубликата."""
    appointment = (
        Appointment.objects.select_for_update()
        .filter(
            id=appointment_id,
            clinic=conversation.lead.clinic,
            lead=conversation.lead,
        )
        .first()
    )

    if appointment is None:
        return {
            "success": False,
            "message": "Запись не найдена.",
        }

    if appointment.status not in ["pending", "confirmed"]:
        return {
            "success": False,
            "message": "Перенести можно только активную запись.",
        }

    if appointment.scheduled_at <= timezone.now():
        return {
            "success": False,
            "message": "Прошедшую запись нельзя перенести через чат.",
        }

    try:
        selected_date = date.fromisoformat(new_date)
        selected_time = time.fromisoformat(new_start_time)
    except (ValueError, TypeError):
        return {
            "success": False,
            "message": "Некорректные дата или время.",
        }

    doctor = (
        Doctor.objects.select_for_update()
        .filter(
            id=appointment.doctor_id,
            clinic=appointment.clinic,
            is_active=True,
        )
        .first()
    )

    if doctor is None:
        return {
            "success": False,
            "message": "Врач больше не доступен для записи.",
        }

    start_dt = timezone.make_aware(
        datetime.combine(selected_date, selected_time)
    )
    end_dt = start_dt + timedelta(
        minutes=appointment.duration_minutes
    )

    if start_dt <= timezone.now():
        return {
            "success": False,
            "message": "Нельзя перенести запись на прошедшее время.",
        }

    working_hours = doctor.working_hours.filter(
        weekday=selected_date.weekday(),
        is_day_off=False,
    ).first()

    if working_hours is None:
        return {
            "success": False,
            "message": "В этот день врач не работает.",
        }

    work_start = timezone.make_aware(
        datetime.combine(selected_date, working_hours.start_time)
    )
    work_end = timezone.make_aware(
        datetime.combine(selected_date, working_hours.end_time)
    )

    if start_dt < work_start or end_dt > work_end:
        return {
            "success": False,
            "message": "Выбранное время вне рабочих часов врача.",
        }

    # Разрешаем только интервалы с шагом 15 минут
    # относительно начала рабочего дня.
    minutes_from_start = int(
        (start_dt - work_start).total_seconds() // 60
    )

    if minutes_from_start % 15 != 0:
        return {
            "success": False,
            "message": (
                "Выберите время с шагом 15 минут "
                "от начала рабочего дня."
            ),
        }

    # Находим записи, которые могут пересекаться с новым интервалом.
    # Окончательное пересечение проверяем с учётом длительности каждой.
    conflicts = Appointment.objects.filter(
        clinic=appointment.clinic,
        doctor=doctor,
        status__in=["pending", "confirmed"],
        scheduled_at__lt=end_dt,
    ).exclude(
        pk=appointment.pk,
    )

    for other in conflicts:
        other_end = other.scheduled_at + timedelta(
            minutes=other.duration_minutes
        )

        if other_end > start_dt:
            return {
                "success": False,
                "message": (
                    "Это время уже занято. "
                    "Выберите другой свободный интервал."
                ),
            }

    old_dt = timezone.localtime(appointment.scheduled_at)

    appointment.scheduled_at = start_dt
    appointment.save()

    return {
        "success": True,
        "appointment_id": str(appointment.id),
        "doctor_name": doctor.name,
        "old_date": old_dt.date().isoformat(),
        "old_start_time": old_dt.strftime("%H:%M"),
        "new_date": selected_date.isoformat(),
        "new_start_time": selected_time.strftime("%H:%M"),
        "duration_minutes": appointment.duration_minutes,
        "status": appointment.status,
        "message": (
            f"Запись перенесена на {selected_date:%d.%m.%Y} "
            f"в {selected_time:%H:%M}."
        ),
    }
