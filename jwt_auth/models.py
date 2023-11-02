from django.db import models
from .managers import CustomUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from email_service.services import send_email_and_generate_token
# Create your models here.

class WaitingList(models.Model):
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)

class Subscription(models.Model):
    name = models.CharField(max_length=50, unique=True)
    credit = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserProfile(AbstractUser):
    username = None

    regex = r"^[a-zA-Z]+$"

    first_name = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=regex,
                message="Firstname must contain Alphabets only.",
            )
        ]
    )

    last_name = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=regex,
                message="Lastname must contain Alphabets only.",
            )
        ]
    )

    email = models.EmailField(
        _("Email Address"),
        unique=True,
        db_index=True,
        error_messages={
            "unique": "User is already exist with given email address"
        }
    )

    date_of_birth = models.DateField(null=True)

    phone_number = PhoneNumberField(
        unique=True,
        null=True,
        db_index=True,
        error_messages={
            "unique": "User is already exist with given phone number"
        }
    )
    is_email_verified = models.BooleanField(default=False)

    # New fields
    user_credits = models.IntegerField(default=1000)
    current_subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, related_name='users')
    subscription_start_date = models.DateField(null=True, default=None)
    subscription_end_date = models.DateField(null=True, default=None)

    is_google_oauth = models.BooleanField(default=False)


    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["date_of_birth"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


@receiver(post_save, dispatch_uid="adhisAY^&*D(h", sender=UserProfile)
def send_email(sender, instance, created, **kwargs):
    user_name = instance.first_name.capitalize() + ' ' + instance.last_name.capitalize()

    if created:
        send_email_and_generate_token(instance.email, user_name=user_name,
                                      email_template='../templates/mails/registration.html',
                                      email_subject="Email Verification Link")