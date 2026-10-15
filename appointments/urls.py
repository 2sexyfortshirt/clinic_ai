from django.urls import path
from appointments.views import AppointmentListCreateAPIView

urlpatterns = [
path("", AppointmentListCreateAPIView.as_view(), name="appointment-list-create"),
]
