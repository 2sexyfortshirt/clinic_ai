from django.contrib import admin
from .models import Conversation,Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "lead",
                    "is_active",
                    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation","role",)
    list_filter = ("role",)

# Register your models here.
