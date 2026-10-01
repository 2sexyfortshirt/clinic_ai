from django.urls import path
from .views import RegisterAPIView,MeAPIView,PatientRegisterAPIView
from rest_framework_simplejwt.views import (TokenRefreshView,TokenObtainPairView,)

urlpatterns = [
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="register"
    ),
    path("login/", TokenObtainPairView.as_view(),
         name="login",
         ),
    path("refresh/", TokenRefreshView.as_view(), name="refresh",
         ),
    path("me/",MeAPIView.as_view(),name="me",),

    path(
        "patient-register/<slug:slug>/",PatientRegisterAPIView.as_view(),name="patient-register",
    ),

]