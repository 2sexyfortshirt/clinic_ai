
import json
import re
from datetime import date, timedelta

from django.utils import timezone

from ai.clients.openai_client import OpenAIClient
from ai.prompts.receptionist import SYSTEM_PROMPT
from ai.tools import (
    list_doctors,
    find_available_slots_for_date,
    find_available_dates,
    create,
    my_appointments,
    cancel,
    reschedule,
)


DURATION_OPTIONS = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]


def function_tool(name, description, properties=None, required=None):
    """Создаёт описание инструмента для OpenAI."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


TOOLS = [
    function_tool(
        "list_doctors",
        "Показать активных врачей клиники.",
    ),
    function_tool(
        "find_available_slots",
        "Найти свободные слоты на конкретную дату. Предлагай только возвращённые слоты.",
        {
            "date": {"type": "string", "description": "Дата YYYY-MM-DD."},
            "duration_minutes": {
                "type": "integer",
                "enum": DURATION_OPTIONS,
            },
        },
        ["date"],
    ),
    function_tool(
        "find_available_dates",
        "Найти даты со свободными слотами в указанном диапазоне.",
        {
            "start_date": {"type": "string", "description": "Начальная дата YYYY-MM-DD."},
            "days": {"type": "integer", "description": "Количество дней от 1 до 14."},
            "duration_minutes": {
                "type": "integer",
                "enum": DURATION_OPTIONS,
            },
        },
        ["start_date", "days"],
    ),
    function_tool(
        "book_appointment",
        "Создать запись только на слот из сохранённого списка предложений.",
        {
            "doctor_id": {"type": "string"},
            "date": {"type": "string"},
            "start_time": {"type": "string"},
            "duration_minutes": {
                "type": "integer",
                "enum": DURATION_OPTIONS,
            },
        },
        ["doctor_id", "date", "start_time", "duration_minutes"],
    ),
    function_tool(
        "find_my_appointments",
        "Найти будущие активные записи текущего пациента.",
    ),
    function_tool(
        "cancel_appointment",
        "Отменить существующую запись текущего пациента по её ID.",
        {"appointment_id": {"type": "string"}},
        ["appointment_id"],
    ),
    function_tool(
        "reschedule_appointment",
        "Перенести существующую запись на выбранную дату и время.",
        {
            "appointment_id": {"type": "string"},
            "new_date": {"type": "string"},
            "new_start_time": {"type": "string"},
        },
        ["appointment_id", "new_date", "new_start_time"],
    ),
]


class AIService:
    client = OpenAIClient()

    @classmethod
    def generate_reply(cls, conversation, patient_message=None):
        today = timezone.localdate()
        clinic = conversation.lead.clinic

        if patient_message is None:
            latest_message = (
                conversation.messages
                .filter(role="patient")
                .order_by("-created_at")
                .first()
            )
            patient_message = (
                latest_message.content.strip()
                if latest_message else ""
            )

        pending_slots = conversation.pending_slots or []

        # Обрабатываем короткий выбор времени, например «на 9».
        time_match = re.fullmatch(
            r"(?:на|в|к)?\s*(\d{1,2})(?::(\d{2}))?",
            patient_message.strip(),
            re.IGNORECASE,
        )

        if pending_slots and time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or "00")

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                selected_time = f"{hour:02d}:{minute:02d}"
                matches = [
                    slot for slot in pending_slots
                    if slot.get("start_time") == selected_time
                ]

                if len(matches) == 1:
                    result = create(conversation, matches[0])

                    conversation.pending_slots = []
                    conversation.pending_selected_time = ""
                    conversation.save(update_fields=[
                        "pending_slots",
                        "pending_selected_time",
                    ])

                    if result.get("success"):
                        return result.get("message") or (
                            f"Запись оформлена на {matches[0]['date']} "
                            f"в {matches[0]['start_time']}, "
                            f"врач {matches[0]['doctor_name']}."
                        )

                    return result.get("message") or (
                        "Это время больше недоступно. "
                        "Давайте проверим свободные слоты ещё раз."
                    )

                if len(matches) > 1:
                    conversation.pending_selected_time = selected_time
                    conversation.save(
                        update_fields=["pending_selected_time"]
                    )

                    doctors = ", ".join(
                        dict.fromkeys(
                            slot["doctor_name"] for slot in matches
                        )
                    )
                    return (
                        f"На {selected_time} доступны врачи: {doctors}. "
                        "К какому врачу вас записать?"
                    )

        system_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Текущая дата: {today.isoformat()}.\n"
            "Завтра — следующий календарный день.\n"
            "Не выдумывай даты, врачей, время или доступность.\n"
            "Предлагай только слоты, возвращённые инструментами.\n"
            "Не сообщай об успешной записи, если инструмент "
            "не вернул success=true.\n"
            "Если пациент отвечает «на 9», трактуй это как 09:00, "
            "если такой слот есть среди предложенных.\n"
        )

        if pending_slots:
            system_prompt += (
                "\nРанее предложенные слоты:\n"
                + json.dumps(pending_slots, ensure_ascii=False)
            )

        messages = [{"role": "system", "content": system_prompt}]

        for message in conversation.messages.all().order_by("created_at"):
            if message.role == "patient":
                role = "user"
            elif message.role in ("assistant", "admin"):
                role = "assistant"
            else:
                continue

            messages.append({
                "role": role,
                "content": message.content,
            })

        def execute_tool(name, arguments):
            if name == "list_doctors":
                return {
                    "success": True,
                    "doctors": list_doctors(clinic),
                }

            if name == "find_available_slots":
                try:
                    requested_date = date.fromisoformat(arguments["date"])
                    duration = int(arguments.get("duration_minutes", 40))
                except (ValueError, TypeError, KeyError):
                    return {
                        "success": False,
                        "message": "Некорректная дата или длительность.",
                    }

                if requested_date < today:
                    return {
                        "success": False,
                        "message": "Нельзя искать запись в прошлом.",
                    }

                if duration not in DURATION_OPTIONS:
                    return {
                        "success": False,
                        "message": "Недопустимая длительность записи.",
                    }

                slots = find_available_slots_for_date(
                    clinic,
                    requested_date,
                    duration=duration,
                )

                saved_slots = [
                    {
                        **slot,
                        "doctor_id": str(slot["doctor_id"]),
                        "date": str(slot["date"]),
                    }
                    for slot in sorted(
                        slots,
                        key=lambda item: (
                            item["start_time"],
                            item["doctor_name"],
                        ),
                    )[:5]
                ]

                conversation.pending_slots = saved_slots
                conversation.pending_selected_time = ""
                conversation.save(update_fields=[
                    "pending_slots",
                    "pending_selected_time",
                ])

                return {
                    "success": True,
                    "date": requested_date.isoformat(),
                    "slots": saved_slots,
                }

            if name == "find_available_dates":
                try:
                    start_date = date.fromisoformat(arguments["start_date"])
                    days = int(arguments["days"])
                    duration = int(arguments.get("duration_minutes", 40))
                except (ValueError, TypeError, KeyError):
                    return {
                        "success": False,
                        "message": "Некорректные параметры поиска.",
                    }

                if start_date < today or not 1 <= days <= 14:
                    return {
                        "success": False,
                        "message": "Выберите будущую дату и диапазон от 1 до 14 дней.",
                    }

                if duration not in DURATION_OPTIONS:
                    return {
                        "success": False,
                        "message": "Недопустимая длительность записи.",
                    }

                dates = find_available_dates(
                    clinic,
                    start_date,
                    days=days,
                    duration=duration,
                )

                all_slots = []
                for item in dates:
                    for slot in item["slots"]:
                        all_slots.append({
                            **slot,
                            "doctor_id": str(slot["doctor_id"]),
                            "date": str(slot["date"]),
                        })

                all_slots.sort(
                    key=lambda item: (
                        item["date"],
                        item["start_time"],
                        item["doctor_name"],
                    )
                )

                offered_slots = all_slots[:10]
                conversation.pending_slots = offered_slots
                conversation.pending_selected_time = ""
                conversation.save(update_fields=[
                    "pending_slots",
                    "pending_selected_time",
                ])

                return {
                    "success": True,
                    "available_dates": [
                        item["date"] for item in dates
                    ],
                    "slots": offered_slots,
                }

            if name == "book_appointment":
                requested = {
                    "doctor_id": str(arguments.get("doctor_id", "")),
                    "date": str(arguments.get("date", "")),
                    "start_time": str(arguments.get("start_time", "")),
                    "duration_minutes": arguments.get("duration_minutes"),
                }

                slot = next(
                    (
                        item for item in (conversation.pending_slots or [])
                        if str(item.get("doctor_id")) == requested["doctor_id"]
                        and str(item.get("date")) == requested["date"]
                        and item.get("start_time") == requested["start_time"]
                        and item.get("duration_minutes")
                        == requested["duration_minutes"]
                    ),
                    None,
                )

                if slot is None:
                    return {
                        "success": False,
                        "message": (
                            "Этот слот не был предложен. "
                            "Сначала проверь доступность."
                        ),
                    }

                result = create(conversation, slot)

                if result.get("success"):
                    conversation.pending_slots = []
                    conversation.pending_selected_time = ""
                    conversation.save(update_fields=[
                        "pending_slots",
                        "pending_selected_time",
                    ])

                return result

            if name == "find_my_appointments":
                return {
                    "success": True,
                    "appointments": my_appointments(conversation),
                }

            if name == "cancel_appointment":
                return cancel(
                    conversation,
                    arguments["appointment_id"],
                )

            if name == "reschedule_appointment":
                return reschedule(
                    conversation,
                    arguments["appointment_id"],
                    arguments["new_date"],
                    arguments["new_start_time"],
                )

            return {
                "success": False,
                "message": "Неизвестный инструмент.",
            }

        return cls.client.chat(
            messages,
            tools=TOOLS,
            tool_executor=execute_tool,
        )
