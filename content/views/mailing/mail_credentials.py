from ..imports import *
from .service.email_service import EmailService
from django.contrib.auth.models import Permission


class MailCredentials(APIView, Common, CryptographyUtils):
    def get(self, request: APIViewRequest):
        user: CustomUser = request.user
        mail_account = user.mail_account
        mail_password = user.mail_password
        mail_password = self.decrypt(mail_password)
        works = False
        if mail_account and mail_password:
            mail_service = EmailService(mail_account, mail_password)
            works = mail_service.check_connection()

        return Response(
            {
                "account": mail_account,
                "working": works,
            }
        )

    def post(self, request: APIViewRequest):
        user: CustomUser = request.user
        mail_account = self.check_none(
            request.data.get("account"), user.mail_account)
        mail_password = self.check_none(
            request.data.get("password"), self.decrypt(user.mail_password)
        )

        if not (mail_account and mail_password):
            return Response(
                "account and password fields must be valid", status.HTTP_400_BAD_REQUEST
            )

        mail_service = EmailService(mail_account, mail_password)
        works = mail_service.check_connection()
        mail_password = self.encrypt(mail_password)

        user: CustomUser = request.user
        user.mail_account = mail_account
        user.mail_password = mail_password
        user.save()
        permission = Permission.objects.get(codename="has_mail")
        if works:
            if not user.has_perm(f"content.{permission.codename}"):
                user.user_permissions.add(permission)
        else:
            if user.has_perm(f"content.{permission.codename}"):
                user.user_permissions.remove(permission)
        return Response(
            {
                "account": mail_account,
                "working": works,
            }
        )
