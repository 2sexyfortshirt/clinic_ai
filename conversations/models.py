from django.db import models

from common.models import BaseModel
from leads.models import Lead


class Conversation(BaseModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    is_active = models.BooleanField(default=True)

    # Состояние AI-бронирования
    pending_slots = models.JSONField(default=list, blank=True)
    pending_selected_time = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    pending_action = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )
    pending_appointment_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    def __str__(self):
        return f"Conversation with {self.id}"


class Message(BaseModel):
    ROLE_CHOICES = [
        ("patient", "Patient"),
        ("assistant", "Assistant"),
        ("admin", "Admin"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"