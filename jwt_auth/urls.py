from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserProfileRegistrationView,
    UserEmailVerificationView,
    UserLoginView,
    UserForgotPasswordView,
    UserGoogleCallBack
)

urlpatterns = [
    path("user/register", UserProfileRegistrationView.as_view(), name="register"),
    path("user/token/refresh", TokenRefreshView.as_view()),
    path("user/login", UserLoginView.as_view(), name="login"),
    path(
        "user/forgot-password", UserForgotPasswordView.as_view(), name="forgot_password"
    ),
    path(
        "user/email/verify",
        UserEmailVerificationView.as_view(),
        name="verify_email",
    ),
    path("user/google-auth-callback", UserGoogleCallBack.as_view(), name="login"),
]
