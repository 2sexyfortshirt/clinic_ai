from rest_framework import serializers
from .models import Conversation,Message

class ConversationSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source="lead.name",read_only=True)
    lead_phone = serializers.CharField(source="lead.phone",read_only=True)


    class Meta:
        model = Conversation

        fields = [
            "id",
            "lead_name",
            "lead_phone",
            "is_active",
            "created_at",
        ]



class SendMessageSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=False,
        allow_null=True,)
    content = serializers.CharField()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id",
                  "role",
                  "content",
                  "is_read",
                  "created_at",)

class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    class Meta:
        model = Conversation
        fields = (
            "id",
            "messages",
        )