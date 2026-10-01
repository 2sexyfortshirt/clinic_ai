from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from clinics.models import Clinic
from conversations.services import ConversationService


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("1")
        self.conversation_id = str(
            self.scope["url_route"]["kwargs"]["conversation_id"]
        )
        self.room_group_name = (
            f"conversation_{self.conversation_id}"
        )
        print("2")
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        print(
            "CONNECTED TO GROUP:",
            self.room_group_name
        )

        print("3")

        await self.accept()
        print("4")


    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)

    async def receive_json(self, content):
        print("receive_json")

        text = content["message"]

        clinic = await sync_to_async(Clinic.objects.first)()

        print("CLINIC:", clinic)
        print("before service")

        message = await sync_to_async(
            ConversationService.send_admin_message
        )(
            clinic=clinic,
            conversation_id=self.conversation_id,
            text=text,
        )

        print("SERVICE RETURNED:", message.id)
        print("after service")

    async def chat_message(self, event):
        print("CHAT MESSAGE RECEIVED:", event)

        await self.send_json(
            event["message"]
        )
        print("MESSAGE SENT TO CLIENT")



