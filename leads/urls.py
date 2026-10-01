from django.urls import path
from leads.views import LeadListAPIView, LeadDetailAPIView


urlpatterns = [
    path(
        "",
        LeadListAPIView.as_view(),
        name="lead-list",
    ),
    path(
        "<uuid:pk>/",
        LeadDetailAPIView.as_view(),
        name="lead-detail",
    ),
]