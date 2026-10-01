from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from clinics.models import Clinic
from .services import ConversationService
from .selectors import ConversationSelector
from .serializers import ConversationSerializer,SendMessageSerializer,ConversationDetailSerializer,MessageSerializer
from .models import Conversation

class ReceiveMessageView(APIView):
    def post(self,request):
        clinic = Clinic.objects.first()
        message = ConversationService.receive_message(clinic=clinic,
                                                      phone=request.data["phone"],
                                                      text=request.data["text"],
                                                      name=request.data.get("name"),
                                                      )
        return Response({
            "message_id": str(message.id),
            "status": "ok",
        })

# Create your views here.


class ConversationListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        clinic = getattr(request.user,"clinic",None)
        if clinic is None:

            conversations = ConversationSelector.by_user(request.user)
        else:
            conversations = ConversationSelector.all(clinic)

        serializer = ConversationSerializer(conversations,many=True)
        return Response(serializer.data)



class ConversationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,conversation_id):
        clinic = getattr(request.user, "clinic", None)
        if clinic is None:
            conversation = ConversationSelector.by_user_id(user=request.user,conversation_id=conversation_id)


        else:
            conversation = ConversationSelector.by_id(clinic=clinic,conversation_id=conversation_id)
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)




from rest_framework import status


from .services import ConversationService

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data.get("conversation_id")
        content = serializer.validated_data["content"]

        clinic = getattr(request.user, "clinic", None)

        # PATIENT
        if clinic is None:
            lead = getattr(request.user, "lead", None)

            if lead is None:
                return Response(
                    {"detail": "Patient lead not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if conversation_id:
                conversation = ConversationSelector.by_user_id(
                    user=request.user,
                    conversation_id=conversation_id,
                )
            else:
                conversation, _ = Conversation.objects.get_or_create(
                    lead=lead,
                    is_active=True,
                )

        # ADMIN
        else:
            if not conversation_id:
                return Response(
                    {"detail": "conversation_id is required for admin."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            conversation = ConversationSelector.by_id(
                clinic=clinic,
                conversation_id=conversation_id,
            )

        message = ConversationService.send_message(
            conversation=conversation,
            text=content,
        )

        return Response(
            {
                "message_id": message.id,
                "conversation_id": conversation.id,
            },
            status=status.HTTP_201_CREATED,
        )
class SendAdminMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clinic = getattr(request.user, "clinic", None)
        if clinic is None:
            return Response(
                {"detail": "Only clinic administrators can send admin messages."},
                status=status.HTTP_403_FORBIDDEN,
            )
        message = ConversationService.send_admin_message(clinic=clinic,
                                                         conversation_id=serializer.validated_data["conversation_id"],
                                                         text=serializer.validated_data["content"],
        )
        return Response(MessageSerializer(message).data,
                        status=status.HTTP_201_CREATED,
                        )
class ConversationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, conversation_id):
        clinic = getattr(request.user, "clinic", None)

        if clinic is None:
            conversation = ConversationSelector.by_user_id(
                user=request.user,
                conversation_id=conversation_id,
            )
        else:
            conversation = ConversationSelector.by_id(
                clinic=clinic,
                conversation_id=conversation_id,
            )

        conversation.messages.filter(is_read=False).update(is_read=True)

        return Response(status=status.HTTP_200_OK)
class ConversationMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,conversation_id):
        clinic = getattr(request.user,"clinic",None)
        if clinic is None:
            conversation = ConversationSelector.by_user_id(user=request.user,
                                                           conversation_id=conversation_id,
                                                           )
        else:

            conversation = ConversationSelector.by_id(clinic=clinic,conversation_id=conversation_id)

        messages = ConversationSelector.messages(conversation)
        serializer = MessageSerializer(messages,many=True)
        return Response(serializer.data)



@api_view(["GET"])
@permission_classes([AllowAny])
def test_api(request):
    return Response({
        "status": "ok",
        "message": "Hello from Django"
    })



