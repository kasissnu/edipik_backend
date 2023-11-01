# -*- coding: utf-8 -*-

# Third Party Stuff
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .base import response
from .serializers import (
    EmailSerializer,
    EmailServiceSerializer,
    EmailServiceWithOTPSerializer,
)
from .services import send_email_and_generate_token


class EmailServiceViewSet(viewsets.GenericViewSet):
    """
        `send` method with send security_code(OTP) + session token
        `send_token` method with send only session token
        
        `verify` method with verify security_code(OTP) + session token
        `verify_token` method only verifies session token
    """
    
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=EmailSerializer,
    )
    def send(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = send_email_and_generate_token(
            str(serializer.validated_data["email"]), generate_security_code=True
        )
        return response.Ok({"session_token": session_token})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=EmailSerializer,
    )
    def send_token(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = send_email_and_generate_token(
            str(serializer.validated_data["email"])
        )
        return response.Ok({"session_token": session_token})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=EmailServiceWithOTPSerializer,
    )
    def verify(self, request):
        serializer = EmailServiceWithOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Ok({"message": "Security code is valid."})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=EmailServiceSerializer,
    )
    def verify_token(self, request):
        serializer = EmailServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Ok({"message": "Security code is valid."})
