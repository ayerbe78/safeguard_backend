from ..imports import *
from .service.email_service import *
from .mail_credentials import *


class EmailCommons(Common, CryptographyUtils):
    def get_credentials(self, request: APIViewRequest):
        user: CustomUser = request.user
        mail = user.mail_account
        password = user.mail_password
        password = self.decrypt(password)
        user_name = f"{user.first_name} {user.last_name}"
        return mail, password, user_name

    def get_mail_service(self, email, passw, name):
        if not email or not passw:
            raise WrongMailCredentialsException("Wrong Credentials")
        return EmailService(email, passw, user_name=name)

    def get_mail_service_from_req(self, request: APIViewRequest):
        user_mail, user_pass, user_name = self.get_credentials(request)
        return self.get_mail_service(user_mail, user_pass, user_name)


class CheckEmails(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        flag = self.check_none(request.data.get("flag"))
        folder = self.check_none(request.data.get("folder"), "INBOX")
        offset = self.check_none(request.data.get("offset"), 0)
        limit = self.check_none(request.data.get("limit"), 25)

        mails, count = [], 0
        params = {
            "folder": folder,
            "limit": limit,
            "offset": offset,
            "headers_only": True,
        }
        if flag:
            params.update({"flag": flag})

        try:
            mails = service.get_messages(**params)

            def map_mail(mail: EmailMessage):
                return mail.get_dict()

            count = service.get_folder_count(folder, flag)
            mails = list(map(map_mail, mails))
        except Exception as e:
            logger.error(e)

        return Response({"count": count, "results": mails})


class GetEmail(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        message = self.check_none(request.data.get("message"))
        folder = self.check_none(request.data.get("folder"), "INBOX")
        if not message or not folder:
            return Response("Must pass message param", status.HTTP_400_BAD_REQUEST)

        message = service.get_message(message, folder, mark_seen=True)
        return Response(message.get_dict())


class MoveEmail(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        messages = self.check_none(request.data.get("messages"))
        from_ = self.check_none(request.data.get("from"), "INBOX")
        to = self.check_none(request.data.get("to"), "INBOX")

        service.move_message(messages, from_, to)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteEmail(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        message = self.check_none(request.data.get("message"))
        folder = self.check_none(request.data.get("folder"), "INBOX")
        delete = self.check_none(request.data.get("delete"), 0)
        service.delete_message(message, folder, bool(not delete))
        return Response(status=status.HTTP_204_NO_CONTENT)


class ToggleSeen(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        messages = self.check_none(request.data.get("messages"))
        folder = self.check_none(request.data.get("folder"), "INBOX")
        unseen = self.check_none(request.data.get("unseen"), 0)
        service.toggle_seen_message(messages, bool(not unseen), folder)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ToggleFav(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        messages = self.check_none(request.data.get("messages"))
        folder = self.check_none(request.data.get("folder"), "INBOX")
        unfav = self.check_none(request.data.get("unfav"), 0)
        service.toggle_fav_message(messages, bool(not unfav), folder)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SendEmail(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)

        service.send_message(*self.__get_mail_parts(request))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def __get_mail_parts(self, request: APIViewRequest):
        to = self.check_none(request.data.get("to"))
        subject = self.check_none(request.data.get("subject"))
        reply_to = self.check_none(request.data.get("reply_to"))
        cc = self.check_none(request.data.get("cc"))
        bcc = self.check_none(request.data.get("bcc"))
        text = self.check_none(request.data.get("text"))
        html = self.check_none(request.data.get("html"))

        return to, subject, reply_to, cc, bcc, text, html


class ReplyEmail(APIView, EmailCommons):
    def post(self, request: APIViewRequest):
        service = self.get_mail_service_from_req(request)
        service.reply_message(*self.__get_mail_parts(request))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def __get_mail_parts(self, request: APIViewRequest):
        message = self.check_none(request.data.get("message"))
        cc = self.check_none(request.data.get("cc"))
        bcc = self.check_none(request.data.get("bcc"))
        folder = self.check_none(request.data.get("folder"), "inbox")
        html = self.check_none(request.data.get("html"))
        text = self.check_none(request.data.get("text"))

        return message, cc, bcc, folder, html, text
