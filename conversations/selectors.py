from django.shortcuts import get_object_or_404

from .models import Conversation

class ConversationSelector:
    @staticmethod

    def by_id(clinic,conversation_id):
        return get_object_or_404(Conversation,id=conversation_id,lead__clinic=clinic,)

    @staticmethod
    def all(clinic):
        return (
            Conversation.objects.filter(lead__clinic=clinic).select_related("lead").order_by("-id").prefetch_related("messages")
        )
    @staticmethod
    def by_user(user):
        return (
            Conversation.objects.filter(lead__user=user).select_related('lead').order_by("-id").prefetch_related("messages")
        )


    @staticmethod
    def messages(conversation):
        return (
            conversation.messages.order_by("created_at")
        )

    @staticmethod
    def by_user_id(user, conversation_id):
        return get_object_or_404(
            Conversation,
            id=conversation_id,
            lead__user=user,
        )