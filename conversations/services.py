from .models import Conversation,Message
from leads.services import LeadService
from core_events.registry import publish
from .selectors import ConversationSelector


class ConversationService:
    @staticmethod
    def receive_message(clinic, phone, text, name=None):
        lead = LeadService.get_or_create(clinic=clinic, phone=phone, name=name,)
        conversation, _ = Conversation.objects.get_or_create(lead=lead, is_active=True,)
        message = Message.objects.create(conversation=conversation, role="patient",content=text,)
        publish("message_received",
                {"message_id": message.id,
                 "conversation_id": conversation.id,
                 "text": text, }





                )
        return message

    @staticmethod

    def send_message(conversation,text):
        message = Message.objects.create(conversation=conversation,role="patient",
                                         content=text,)

        publish(
            "message_received",
            {
                "message_id": str(message.id),
                "conversation_id": str(conversation.id),
                "role": message.role,
            }
        )
        return message

    @staticmethod
    def send_admin_message(clinic,conversation_id,text):
        conversation = ConversationSelector.by_id(clinic=clinic,
                                                  conversation_id=conversation_id)

        message = Message.objects.create(
            conversation=conversation,
            role="admin",
            content=text,
        )

        publish(
            "message_received",
            {
                "message_id": str(message.id),
                "conversation_id": str(conversation_id),
                "text": text,
            }
        )
        return message


    @staticmethod
    def mark_as_read(clinic,conversation_id):
        conversation = ConversationSelector.by_id(clinic=clinic,conversation_id=conversation_id)

        conversation.messages.filter(is_read=False).update(is_read=True)

