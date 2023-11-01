from .models import EmailService


def store_email_tokens(email, security_code, session_token):
    # Delete old security_code(s) for email if already exists
    EmailService.objects.filter(email=email).delete()

    # Default security_code generated of 6 digits
    EmailService.objects.create(
        email=email,
        security_code=security_code,
        session_token=session_token,
    )


# def get_stored_token(email, security_code):
#     stored_verification = EmailService.objects.filter(
#         security_code=security_code, email=email
#     ).first()

#     return stored_verification
