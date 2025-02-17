from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):

    email_plaintext_message = """
You're receiving this e-mail because you requested a password reset for your user account at {site_name}
You can use the next token to reset your password:
Token: {token}

Thanks for using our site!
    """.format(
        site_name="Safeguard", token=reset_password_token.key
    )
    send_mail(
        # title:
        "Password Reset for {title}".format(title="Safeguard"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@safeguard.com",
        # to:
        [reset_password_token.user.email],
    )


class CustomUser(AbstractUser):
    is_admin = models.BooleanField(null=True, blank=True)
    is_agent = models.BooleanField(null=True, blank=True)
    is_assistant = models.BooleanField(null=True, blank=True)
    is_subassistant = models.BooleanField(null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True, blank=False)
    mail_account = models.EmailField(unique=False, blank=True, null=True)
    mail_password = models.CharField(
        unique=False, blank=True, null=True, max_length=500
    )
    personal_phone_number = models.CharField(
        unique=True, null=True, max_length=500, default=None
    )
    company_phone_number = models.CharField(
        unique=True, null=True, max_length=500, default=None
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]
