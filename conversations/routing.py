from django.urls import path
from .consumers import ConversationConsumer



websocket_urlpatterns = [
    path("ws/conversation/<uuid:conversation_id>/",ConversationConsumer.as_asgi(),),
]