# -*- coding: utf-8 -*-

# Standard Library
from .utils import EmailUtilities
import logging

# Third Party Stuff

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
# Email Auth Stuff

logger = logging.getLogger(__name__)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailServiceSerializer(serializers.Serializer):
    """
    Serializer that will used for verification of session token both
    """

    email = serializers.EmailField(required=True)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get("email", None)
        session_token = attrs.get("session_token", None),

        backend = EmailUtilities()
        verification, token_validatation = backend.validate_data(
            email=email,
            session_token=session_token[0],
        )

        if verification is None and token_validatation == backend.SESSION_TOKEN_INVALID:
            raise serializers.ValidationError(_("The link is not valid"))
        elif token_validatation == backend.SESSION_TOKEN_INVALID:
            raise serializers.ValidationError(_("The link is not valid"))
        elif token_validatation == backend.SESSION_TOKEN_EXPIRED:
            raise serializers.ValidationError(_("The link has been expired"))
        elif token_validatation == backend.SECURITY_CODE_EXPIRED:
            raise serializers.ValidationError(_("The link has been expired"))

        return attrs


class EmailServiceWithOTPSerializer(EmailServiceSerializer):
    """
    Serializer that will used for verification session token only
    """

    security_code = serializers.CharField(required=True)
