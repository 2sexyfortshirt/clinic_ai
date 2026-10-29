

# Create your tests here.



from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from clinics.models import Clinic
from leads.models import Lead
from conversations.models import Conversation

from .models import Appointment, Doctor, DoctorWorkingHours
from .services import (
    get_available_slots,
    book_appointment,
    get_patient_appointments,
    cancel_appointment,
    reschedule_appointment,
)


class AppointmentServicesTests(TestCase):
    def setUp(self):
        """Создаём тестовую клинику, пациента и врача."""

        self.user = User.objects.create_user(
            username="test_patient",
            password="test-password-123",
        )

        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            slug="test-clinic",
        )

        self.lead = Lead.objects.create(
            clinic=self.clinic,
            user=self.user,
            phone="+905551112233",
            name="Test Patient",
        )

        self.conversation = Conversation.objects.create(
            lead=self.lead,
        )

        self.doctor = Doctor.objects.create(
            clinic=self.clinic,
            name="Dr. Test",
            specialty="Dentist",
        )

        # Выбираем будущий понедельник, чтобы дата не зависела
        # от дня, когда запускаются тесты.
        today = timezone.localdate()
        days_until_monday = (0 - today.weekday()) % 7

        if days_until_monday == 0:
            days_until_monday = 7

        self.test_date = today + timedelta(days=days_until_monday)

        DoctorWorkingHours.objects.create(
            doctor=self.doctor,
            weekday=self.test_date.weekday(),
            start_time=time(9, 0),
            end_time=time(12, 0),
        )

    def test_get_available_slots_returns_slots(self):
        """В рабочее время должны появляться свободные интервалы."""

        slots = get_available_slots(
            clinic=self.clinic,
            date=self.test_date,
            duration_minutes=40,
        )

        self.assertTrue(slots)

        self.assertEqual(
            slots[0]["start_time"],
            "09:00",
        )

        self.assertEqual(
            slots[0]["doctor_id"],
            self.doctor.id,
        )

    def test_booking_creates_appointment(self):
        """Бронирование свободного интервала создаёт запись."""

        result = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        self.assertTrue(result["success"])
        self.assertEqual(Appointment.objects.count(), 1)

        appointment = Appointment.objects.get()

        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.lead, self.lead)
        self.assertEqual(appointment.status, "pending")

    def test_booking_rejects_occupied_slot(self):
        """Нельзя повторно забронировать уже занятый интервал."""

        first_result = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        self.assertTrue(first_result["success"])

        second_result = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        self.assertFalse(second_result["success"])
        self.assertEqual(Appointment.objects.count(), 1)

    def test_cancel_appointment(self):
        """Активную будущую запись можно отменить."""

        booking = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        result = cancel_appointment(
            conversation=self.conversation,
            appointment_id=booking["appointment_id"],
        )

        self.assertTrue(result["success"])

        appointment = Appointment.objects.get()

        self.assertEqual(appointment.status, "cancelled")

    def test_get_patient_appointments_returns_active_booking(self):
        """Сервис возвращает будущие активные записи пациента."""

        booking = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        appointments = get_patient_appointments(self.conversation)

        self.assertEqual(len(appointments), 1)
        self.assertEqual(
            appointments[0]["appointment_id"],
            booking["appointment_id"],
        )

    def test_reschedule_appointment(self):
        """Запись можно перенести на другой свободный интервал."""

        booking = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        result = reschedule_appointment(
            conversation=self.conversation,
            appointment_id=booking["appointment_id"],
            new_date=self.test_date.isoformat(),
            new_start_time="10:00",
        )

        self.assertTrue(result["success"])

        appointment = Appointment.objects.get()

        self.assertEqual(
            timezone.localtime(appointment.scheduled_at).strftime("%H:%M"),
            "10:00",
        )

        # Переносит существующую запись, не создавая дубликат.
        self.assertEqual(Appointment.objects.count(), 1)

    def test_reschedule_rejects_occupied_slot(self):
        """Нельзя перенести запись на время другого пациента."""

        booking_one = book_appointment(
            conversation=self.conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="09:00",
        )

        # Создаём второго пациента той же клиники.
        second_lead = Lead.objects.create(
            clinic=self.clinic,
            phone="+905559998877",
            name="Second Patient",
        )

        second_conversation = Conversation.objects.create(
            lead=second_lead,
        )

        booking_two = book_appointment(
            conversation=second_conversation,
            doctor_id=self.doctor.id,
            appointment_date=self.test_date.isoformat(),
            start_time="10:00",
        )

        self.assertTrue(booking_one["success"])
        self.assertTrue(booking_two["success"])

        result = reschedule_appointment(
            conversation=self.conversation,
            appointment_id=booking_one["appointment_id"],
            new_date=self.test_date.isoformat(),
            new_start_time="10:00",
        )

        self.assertFalse(result["success"])

        appointment = Appointment.objects.get(
            id=booking_one["appointment_id"],
        )

        self.assertEqual(
            timezone.localtime(appointment.scheduled_at).strftime("%H:%M"),
            "09:00",
        )

        self.assertEqual(Appointment.objects.count(), 2)
