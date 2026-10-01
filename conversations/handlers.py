from core_events.registry import register
from conversations.models import Conversation, Message
from conversations.serializers import MessageSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@register("message_received")
def send_message_to_websocket(event):
    print("Handler Worked")

    channel_layer = get_channel_layer()

    message = Message.objects.get(
        id=event["message_id"]
    )

    message_data = MessageSerializer(message).data

    async_to_sync(channel_layer.group_send)(
        f"conversation_{event['conversation_id']}",
        {
            "type": "chat.message",
            "message": message_data,
        },
    )