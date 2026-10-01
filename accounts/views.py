from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer,PatientRegisterSerializer


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id,
             "username": user.username,
             "message": "Registration successful",
             },
            status=status.HTTP_201_CREATED,
        )


class PatientRegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self,request,slug):
        from clinics.models import Clinic
        clinic = Clinic.objects.filter(slug=slug,is_active=True,).first()
        if not clinic:
            return Response({"detail":"Clinic not found."},
                            status=status.HTTP_404_NOT_FOUND,)


        serializer = PatientRegisterSerializer(data=request.data,context={"clinic":clinic},
                                                   )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "message": "Patient registration successful",

             },
            status=status.HTTP_201_CREATED,
        )

# Create your views here.
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        clinic = getattr(request.user,"clinic",None)
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "clinic": clinic.name if clinic else None,
            "role": "admin" if clinic else "patient",

        })
