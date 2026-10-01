from django.urls import path
from .views import ReceiveMessageView, ConversationListAPIView, ConversationDetailAPIView, SendMessageAPIView,\
    SendAdminMessageAPIView,ConversationReadAPIView,ConversationMessagesAPIView,test_api


urlpatterns = [
    path("receive/",ReceiveMessageView.as_view(),
         ),
    path("", ConversationListAPIView.as_view()),
    path("<uuid:conversation_id>/", ConversationDetailAPIView.as_view(),
         ),
    path("messages/", SendMessageAPIView.as_view()),
    path("send/", SendAdminMessageAPIView.as_view()),
    path("<uuid:conversation_id>/read/", ConversationReadAPIView.as_view()),
    path("<uuid:conversation_id>/messages/", ConversationMessagesAPIView.as_view()),
    path("test/", test_api),

]