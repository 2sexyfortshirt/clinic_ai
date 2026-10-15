import traceback

from core_events.registry import register, publish
from conversations.models import Conversation, Message
from ai.services import AIService


@register("message_received")
def ai_reply(event):
    try:
        # AI отвечает только пациенту
        if event.get("role") != "patient":
            return

        print("AI START")

        conversation = Conversation.objects.get(
            id=event["conversation_id"]
        )

        reply = AIService.generate_reply(conversation)

        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=reply,
        )

        print("AI message created")

        publish(
            "message_received",
            {
                "message_id": str(assistant_message.id),
                "conversation_id": str(conversation.id),
                "role": assistant_message.role,
            }
        )

        print("AI END")

    except Exception:
        traceback.print_exc()