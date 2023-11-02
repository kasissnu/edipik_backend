from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import WaitingList

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(object):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.current_subscription_id = 1
        user.user_credits = 1000
        user.subscription_start_date = timezone.now()
        user.save()
        return user

    def validate(self, attrs):
        password = attrs.get("password")
        user = User(**attrs)
        django_validate_password(password=password, user=user)
        return super().validate(attrs)


class UserForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        params = {}
        email = attrs.get("email", None)
        if not email:
            raise serializers.ValidationError("Email field does not exist")
        params["email"] = email

        try:
            user_details = User.objects.get(**params)
        except ObjectDoesNotExist as user_details:
            raise serializers.ValidationError(
                f"No user found for given email"
            )
        return attrs


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def _get_user(self):
        request_data = self.context["request"].data
        filter_kwargs = {}
        filter_kwargs['email'] = request_data.get('email')
        return get_object_or_404(User, **filter_kwargs)

    def validate_password(self, password):
        user = self._get_user()
        django_validate_password(password, user=user)
        return password

class WaitingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingList
        fields = '__all__'
