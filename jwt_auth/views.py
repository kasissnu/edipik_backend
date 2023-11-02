from datetime import date, datetime
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from .serializers import UserForgotPasswordSerializer, UserPasswordResetSerializer, UserRegistrationSerializer, WaitingListSerializer
from email_service.serializers import EmailServiceSerializer, EmailSerializer
from email_service.services import send_email_and_generate_token
from django.contrib.auth import authenticate, get_user_model
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    NotFound,
    ParseError,
    bad_request
)
from . import services
from rest_framework_simplejwt.views import TokenObtainPairView
import jwt
import requests
from rest_framework.serializers import ValidationError
import json
from django.core import serializers
from rest_framework import serializers as drf_serializers
from .models import WaitingList
import re
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import EmailValidator


# Create your views here.

User = get_user_model()


class UserSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserProfileRegistrationView(generics.CreateAPIView):
    """
    To Create user based on POST request to 'user/register' endpoint
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()


class UserEmailVerificationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query_params = {}
        query_params["email"] = self.request.data["email"]
        return User.objects.filter(**query_params).first()

    def get_serializer_class(self):
        return EmailServiceSerializer if "session_token" in self.request.data.keys() else EmailSerializer

    def post(self, request):
        user_db_details = self.get_queryset()
        if not user_db_details:
            raise NotFound({"error": "Account not found"})

        user_request_data = request.data
        serializer = self.get_serializer(data=user_request_data)
        # If session_token for email verification is not in request means user doesn't have verification link
        # so send email verification link
        if serializer.is_valid():
            if not "session_token" in user_request_data.keys():
                user_name = user_db_details.first_name.capitalize(
                ) + " " + user_db_details.last_name.capitalize()
                # Function defined in email_service.services
                send_email_and_generate_token(
                    user_db_details.email,
                    user_name=user_name,
                    email_template="../templates/mails/registration.html",
                    email_subject="Email Verification Link",
                )
                raise NotAuthenticated(
                    {"message": "Email is not verified. Verification mail has been sent"})

            # Else user has session_token and now wants to verify_token and make is_email_verified field true
            else:
                # Now as we are reached here with no exception generated in is_valid()
                # session_token is Verified in EmailServiceSerializer
                # so now as email is verified, update is_email_verified in database
                user_db_details.is_email_verified = True
                user_db_details.save(update_fields=["is_email_verified"])

                return Response(
                    {"message": "Email is verified successfully"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    """
    View that provides Login functionalities via JWT Authentication.
    """

    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        query_params = {}
        user_request_data = self.request.data
        query_params["email"] = user_request_data["email"]

        return User.objects.filter(**query_params).first()

    def post(self, request, *args, **kwargs):
        user_db_details = self.get_queryset()  # details from database
        if not user_db_details:
            raise NotFound({"message": "User does not exist"})

        user_request_data = self.request.data

        if not user_db_details.is_active:
            raise NotAuthenticated({"message": "User is not active"})

        user = authenticate(
            username=user_request_data["email"],
            password=user_request_data["password"],
        )

        if user is None:
            raise AuthenticationFailed(
                {"message": "Username and Password does not match"})

        if not user_db_details.is_email_verified:
            user_name = (
                user_db_details.first_name.capitalize()
                + " "
                + user_db_details.last_name.capitalize()
            )

            send_email_and_generate_token(
                user_db_details.email,
                user_name=user_name,
                email_template="../templates/mails/registration.html",
                email_subject="Email Verification Link",
            )
            raise NotAuthenticated(
                {"message": "Email is not verified. Verification mail has been sent"}
            )

        else:

            response = services.get_tokens_for_user(user_db_details)
            user_db_details.last_login = datetime.now()
            user_db_details.save()
            response["message"] = "Login Successfully"
            response["email_verify"] = user_db_details.is_email_verified
            # serialize the user instance to JSON
            user_obj = user_db_details
            user_obj.password = ""
            user_json = json.loads(serializers.serialize('json', [user_obj, ]))
            response['user'] = user_json
            return Response(
                response,
                status=status.HTTP_200_OK,
            )


class UserForgotPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        user_request_data = self.request.data
        query_params = {}
        query_params["email"] = user_request_data["email"]
        return User.objects.filter(**query_params).first()

    def get_serializer_class(self):
        user_request_data = self.request.data
        if "security_code" not in user_request_data.keys():
            return UserForgotPasswordSerializer
        else:
            return UserPasswordResetSerializer

    def post(self, request):
        user_request_data = self.request.data
        user_db_details = self.get_queryset()
        serializer = self.get_serializer(data=user_request_data)
        serializer.is_valid(raise_exception=True)

        # Check if user is active then proceed further
        if not user_db_details.is_active:
            raise NotAuthenticated({"message": "User is not active"})

        # If security_code is not in request means User wants to start ForgotPassword and send security_code
        if "security_code" not in user_request_data.keys():
            user_name = (
                user_db_details.first_name.capitalize() + " " + user_db_details.last_name.capitalize()
            )
            session_token = send_email_and_generate_token(
                serializer.data["email"],
                user_name=user_name,
                generate_security_code=True,
                email_template="../templates/mails/password_reset.html",
                email_subject="Password Reset Link",
            )
            return Response(
                {
                    "message": "The link has been sent to your Email",
                    "session_token": session_token,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        elif "security_code" in user_request_data.keys():
            response = services.verify_otp_and_reset_password(
                user_request_data, user_db_details
            )
            return Response(response, status=status.HTTP_202_ACCEPTED)

        else:
            raise ParseError({"error": "Missing Parameters"})


class UserGoogleCallBack(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def validate_token(self, token):
        r = requests.get(
            "https://www.googleapis.com/oauth2/v3/tokeninfo",
            params={"id_token": token},
        )
        r.raise_for_status()

    def user_exits_check(self, email):
        query_params = {}
        query_params["email"] = email

        return User.objects.filter(**query_params).first()

    def post(self, request):
        google_request_data = request.data
        google_identify_key = google_request_data['key']

        try:
            self.validate_token(google_identify_key)
        except Exception:
            error = {"message": "Google token invalid."}
            raise ValidationError(error)
        else:
            data = jwt.decode(google_identify_key, options={
                              "verify_signature": False})

            user_db_details = self.user_exits_check(data["email"])
            response = ""

            if not user_db_details:
                validated_data = {}
                validated_data["email"] = data["email"]
                validated_data["first_name"] = data["given_name"]
                validated_data["last_name"] = data["family_name"]
                validated_data["is_email_verified"] = data["email_verified"]
                validated_data["is_active"] = 1
                validated_data["user_credits"] = 1000
                validated_data["current_subscription_id"] = 1
                validated_data["password"] = ""
                validated_data["is_google_oauth"] = 1
                user_db_details = User.objects.create_user(**validated_data)

            response = services.get_tokens_for_user(user_db_details)
            user_db_details.last_login = datetime.now()
            user_db_details.save()
            response["message"] = "Login Successfully"
            response["email_verify"] = user_db_details.is_email_verified
            user_obj = user_db_details
            user_obj.password = ""
            user_json = json.loads(serializers.serialize('json', [user_obj, ]))
            response['user'] = user_json

        return Response(response, status=status.HTTP_200_OK)

class UserWaitingList(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user_data = request.data
        print("model_data", user_data)
        try:
            email_validator = EmailValidator()
            email_validator(user_data['email'])
            user = WaitingList.objects.get(email=user_data['email'])
            if user:
                return Response(
                    {"message": "User already exist! "},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            serializer = WaitingListSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "You have successfully joined Waitinglist "},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Enter valid data", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
