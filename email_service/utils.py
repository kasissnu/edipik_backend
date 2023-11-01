import random

# Third Party Stuff
import jwt

from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from .models import EmailService
from .db_ops import store_email_tokens

DEFAULT_TOKEN_LENGTH = 6


class EmailUtilities():
    SECURITY_CODE_VALID = 0
    SECURITY_CODE_INVALID = 1
    SECURITY_CODE_EXPIRED = 2
    SECURITY_CODE_VERIFIED = 3
    SESSION_TOKEN_INVALID = 4
    SESSION_TOKEN_EXPIRED = 5

    @classmethod
    def generate_security_code(cls):
        """
        Returns a unique random `security_code` for given `TOKEN_LENGTH` in the settings.
        """
        token_length = django_settings.EMAIL_SERVICE.get(
            "TOKEN_LENGTH", DEFAULT_TOKEN_LENGTH
        )
        return get_random_string(token_length, allowed_chars="0123456789")

    @classmethod
    def generate_session_token(cls, email):
        """
        Returns a unique session_token for
        identifying a particular device in subsequent calls.
        """
        data = {"email": email, "nonce": random.random()}
        session_token = jwt.encode(
            data, django_settings.SECRET_KEY, algorithm="HS256")
        try:
            return session_token.decode()
        except AttributeError:
            return session_token

    @classmethod
    def check_security_code_expiry(cls, stored_verification):
        """
        Returns True if the `security_code` for the `stored_verification` is expired.
        """
        time_difference = timezone.now() - stored_verification.created_at
        if time_difference.seconds > django_settings.EMAIL_SERVICE.get(
            "SECURITY_CODE_EXPIRATION_TIME"
        ):
            return True
        return False

    def create_security_code_and_session_token(
        self, email, generate_security_code=True
    ):

        security_code = (
            self.generate_security_code() if generate_security_code else None
        )

        session_token = self.generate_session_token(email)

        store_email_tokens(email, security_code, session_token)
        return security_code, session_token

    def validate_data(self, email, session_token):

        stored_verification = EmailService.objects.filter(
            email=email, session_token=session_token).first()

        # check session code exists
        if not stored_verification.session_token == session_token:
            return stored_verification, self.SESSION_TOKEN_INVALID

        # check session code is not expired
        if self.check_security_code_expiry(stored_verification):
            return stored_verification, self.SESSION_TOKEN_EXPIRED

        # check security_code is not expired
        if self.check_security_code_expiry(stored_verification):
            return stored_verification, self.SECURITY_CODE_EXPIRED

        stored_verification.is_verified = True
        stored_verification.save()

        return stored_verification, self.SECURITY_CODE_VALID
