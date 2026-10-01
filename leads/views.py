from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from leads.selectors import LeadSelector
from leads.serializers import LeadSerializer
from leads.services import LeadService
from rest_framework.generics import RetrieveAPIView


class LeadListAPIView(ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return LeadSelector.list(self.request.user.clinic)


    def perform_create(self, serializer):
        lead = LeadService.create(clinic=self.request.user.clinic,
                                  **serializer.validated_data,)
        serializer.instance = lead



# Create your views here.



class LeadDetailAPIView(RetrieveAPIView):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return LeadSelector.by_id(clinic=self.request.user.clinic,lead_id=self.kwargs["pk"],)