from rest_framework_simplejwt.tokens import RefreshToken

from email_service.serializers import EmailServiceWithOTPSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def verify_otp_and_reset_password(user_request_data, user_db_details):
    serializer = EmailServiceWithOTPSerializer(data=user_request_data)
    serializer.is_valid(raise_exception=True)

    user_db_details.is_email_verified = True

    user_db_details.set_password(user_request_data["password"])
    user_db_details.save()

    return {
        "message": "Password Reset Successfully"
    }


