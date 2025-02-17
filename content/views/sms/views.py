from ..imports import *
from .service.sms_service import SMSService
from .service.sms_temp_file import *
from .models.sms_serializer import *
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import CharField, Value
from django.db.models.functions import Length


class SmsCommons(Common, CompanySMSCommons):
    def sms_get_service(self) -> SMSService:
        return SMSService()

    def sms_send_sms(
        self,
        request: HttpRequest,
        service: SMSService,
        to: str,
        from_: str,
        body: str,
        media_urls=[],
        get_medias=False,
    ):
        result = False
        if len(media_urls):
            result = service.send_sms(
                from_=from_, to=to, sms=body, medias=media_urls,
            )
        else:
            result = service.send_sms(from_=from_, to=to, sms=body)
        if get_medias:
            return result, media_urls
        else:
            return result

    def sms_get_data_from_req(self, request: APIViewRequest):
        user: CustomUser = request.user
        from_ = user.company_phone_number
        files = request.FILES
        to = self.check_none(request.data.get("to"), [])
        if isinstance(to, str):
            to = to.split(",")
            to = list(map(lambda n: n.strip(), to))
        body = self.check_none(request.data.get("body"), "")

        return from_, to, body, files

    def create_file_urls(self, files: dict, hostname):
        new_files = []

        for f in files.values():
            f.name = f"temp_{f.name}"
            serializer = SmsImageTempSerializer(data={"file": f})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            new_files.append(serializer.data)

        files_urls = list(
            map(
                lambda f: f"https://{hostname}/api/sms/tempfile?file={f.get('id')}",
                new_files,
            )
        )
        return files_urls


class SMSRecieveHook(APIView, SmsCommons, TwilioCommons):
    def post(self, request: APIViewRequest):
        self.twilio_validate_post_request(request)
        with transaction.atomic():
            conversation = self.__handle_conversation(request)
            sms = self.__handle_sms(request, conversation)
            self.__handle_media(request, sms)
            return Response()

    def __handle_conversation(self, request: APIViewRequest):
        conversation_data = self.__get_conversation_params(request)
        number = self.sms_ready_phone_number(conversation_data[0])
        conversation, _ = SMSConversation.objects.get_or_create(
            user=conversation_data[3],
            peer=conversation_data[1],
            peer_number=number,
        )
        conversation.unread_count += 1
        # conversation.updated = datetime.datetime.now()
        conversation.save()
        return conversation

    def __get_conversation_params(self, request: APIViewRequest):
        from_ = self.check_none(request.data.get("From"))
        from_user = self.sms_get_user_by_phone(from_)

        to = self.check_none(request.data.get("To"))
        to_user = CustomUser.objects.filter(company_phone_number=to)
        to_user = to_user[0] if to_user.exists() else None

        if not (from_ and to):
            raise ValidationException('"From" or "To" attributes missing')
        if not to_user:
            raise NotFoundException("Not user with that phone number")

        return from_, from_user, to, to_user

    def __handle_sms(self, request: APIViewRequest, conversation: SMSConversation):
        data = request.data
        new_sms = SMS(
            sid=data.get("MessageSid"),
            from_number=data.get("From"),
            to_number=data.get("To"),
            from_user=conversation.peer,
            to_user=conversation.user,
            received=True,
            received_date=timezone.now(),
            sended=False,
            sended_date=None,
            readed=False,
            body=data.get("Body"),
            conversation=conversation,
        )
        new_sms.save()
        conversation.last_message = new_sms
        conversation.save()
        return new_sms

    def __handle_media(self, request: APIViewRequest, sms: SMS):
        media_count = int(self.check_none(request.data.get("NumMedia"), 0))
        for i in range(media_count):
            new_media = SMSMedia(
                url=request.data.get(f"MediaUrl{i}"),
                content_type=request.data.get(f"MediaContentType{i}"),
                sms=sms,
            )
            new_media.save()


class SendSmsView(APIView, SmsCommons):
    permission_classes = [HasPhoneNumberPermission]

    def post(self, request: APIViewRequest):
        service = self.sms_get_service()
        from_, to, body, media = self.sms_get_data_from_req(request)
        messages = []
        new_files = []
        media_urls = []

        if len(media):
            for f in media.values():
                f.name = f"temp_{f.name}"
                serializer = SmsImageTempSerializer(data={"file": f})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                new_files.append(serializer.data)
                logger.info('added')

            media_urls = list(
                map(
                    lambda f: f"https://{request.get_host()}/api/sms/tempfile?file={f.get('id')}",
                    new_files,
                )
            )
        with transaction.atomic():
            for t in to:
                conversation = self.__handle_conversation(request.user, t)
                result = self.sms_send_sms(
                    request, service, t, from_, body, media_urls
                )
                sms = self.__handle_sms(result, conversation, from_, t, body)
                self.__handle_media(sms, result, media_urls)
                messages.append(sms)

        serializer = SMSSerializer(messages, many=True)
        return Response(serializer.data)

    def __handle_conversation(self, user, to: str):
        correct_to = self.sms_ready_phone_number(to)
        to_user = self.sms_get_user_by_phone(correct_to)
        conversations = SMSConversation.objects.filter(
            user=user,
            peer=to_user,
            peer_number=correct_to,
        )
        if len(conversations) == 1:
            conversation = conversations.get()
        else:
            conversations.delete()
            conversation = SMSConversation(
                user=user,
                peer=to_user,
                peer_number=correct_to,
            )
            conversation.save()
        return conversation

    def __handle_sms(
        self, sms_instance, conversation: SMSConversation, from_, to, body
    ):
        new_sms = SMS(
            sid=sms_instance.sid if sms_instance else None,
            from_number=from_,
            to_number=to,
            from_user=conversation.user,
            to_user=conversation.peer,
            received=False,
            received_date=None,
            sended=True if sms_instance else False,
            sended_date=timezone.now(),
            readed=True,
            body=body,
            conversation=conversation,
        )
        new_sms.save()
        conversation.last_message = new_sms
        conversation.save()
        return new_sms

    def __handle_media(self, sms, twilio_response, mediaUrls):
        for m in mediaUrls:
            new_media = SMSMedia(
                url=m,
                content_type="None",
                sms=sms,
            )
            new_media.save()


class ReSendSmsView(APIView, SmsCommons):
    permission_classes = [HasPhoneNumberPermission]

    def post(self, request: APIViewRequest):
        user: CustomUser = request.user
        service = self.sms_get_service()
        message_id = request.data.get("id")
        if not message_id:
            raise ValidationException("Not Message Id Provided")
        user_conversations = user.conversations.all()
        user_messages = SMS.objects.filter(conversation__in=user_conversations).filter(
            pk=message_id
        )
        if not user_messages.exists():
            raise NotFoundException("Not such message")
        message = user_messages.get()
        if message.received == True:
            raise ValidationException("Message received can not be resended")
        if message.sended == True:
            return Response(message, status=status.HTTP_202_ACCEPTED)
        if message.conversation.peer_number != message.to_number:
            message.to_number = message.conversation.peer_number
        mediaurls = list(map(lambda m: m.get("url"),
                         message.media.all().values("url")))
        result = service.send_sms(
            from_=message.from_number,
            to=message.to_number,
            sms=message.body,
            medias=mediaurls,
        )
        message.sended = True if result else False
        message.sended_date = timezone.now()
        message.save()
        serializer = SMSSerializer(message)
        return Response(serializer.data)


class SendServiceSMS(APIView, SmsCommons):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request: APIViewRequest):
        with transaction.atomic():
            service = self.sms_get_service()
            _, to, sms, media = self.sms_get_data_from_req(request)
            final_result = []

            for t in to:
                result = False
                if len(media):
                    media_urls = self.create_file_urls(
                        media, request.get_host())
                    result = service.service_sms(sms, t, media_urls)
                else:
                    result = service.service_sms(sms, t)
                final_result.append(result)

            if True in final_result:
                result = Response(
                    (final_result.count(True), len(final_result)),
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                raise ValidationException()
            return result


class UserContactsView(APIView, AgencyManagement):
    permission_classes = [HasPhoneNumberPermission]

    def get(self, requets: APIViewRequest):
        user: CustomUser = requets.user
        clients = self.get_related_clients(
            user.id, year=date.today().year, include_self=True).exclude(telephone=None).exclude(telephone="").exclude(telephone="N/A").exclude(telephone="n/a").exclude(telephone="na").exclude(telephone="NA").exclude(telephone="Na").annotate(
                name=Concat(('names'), Value(' '), ('lastname'),
                            output_field=models.CharField())
        ).values('name', 'telephone', 'email').annotate(
            telephone_length=Length('telephone')
        ).exclude(telephone_length__lt=10)
        if not user.is_agent:
            if user.is_admin:
                related_users = CustomUser.objects.all()
            else:
                agents = self.get_related_agents(user.pk, only=["email"])
                assistants = self.get_related_assistants(user.pk)
                related_users = CustomUser.objects.filter(
                    email__in=self.queryset_to_list(agents, param="email")
                )
                related_users |= CustomUser.objects.filter(
                    email__in=self.queryset_to_list(assistants, param="email")
                )
            contact_users = (
                related_users.prefetch_related("groups")
                .exclude(personal_phone_number=None)
                .exclude(personal_phone_number="")
                .annotate(
                    name=Concat("first_name", V(" "), "last_name"),
                    phone=F("personal_phone_number"),
                    company=V(False),
                    contact_id=Concat("id", V("-personal"),
                                      output_field=CharField()),
                )
            )
            contact_users = (
                (
                    related_users.prefetch_related("groups")
                    .exclude(company_phone_number=None)
                    .exclude(company_phone_number="")
                    .annotate(
                        name=Concat("first_name", V(" "), "last_name"),
                        phone=F("company_phone_number"),
                        company=V(True),
                        contact_id=Concat("id", V("-company"),
                                          output_field=CharField()),
                    )
                )
                .union(contact_users, all=True)
                .order_by("name")
            )
            serializer = ContactUserSerializer(contact_users, many=True)
            users = serializer.data
            groups = Group.objects.annotate(
                contact_id=Concat(V("group-"), "pk",
                                  output_field=models.CharField()),
                is_group=V(True),
            ).values("contact_id", "name", "is_group", "id")
        else:
            users = []
            for client in clients:
                users.append(
                    {
                        "name": client.get('name'),
                        "email": client.get("email"),
                        "phone": client.get("telephone"),
                        "company": False,
                        "groups": [],
                        "contact_id": ""
                    }
                )
            groups = ()

        clients_group = {'name': 'Clients', 'id': 999,
                         'contact_id': 'clients', 'is_group': True}

        # Assuming your existing queryset is named 'queryset', you can add the new object like this:
        groups = list(groups)
        groups.append(clients_group)

        return Response({"users": users, "groups": groups, "clients": clients})


class ListConversationsView(APIView, DirectSql, AgencyManagement):
    permission_classes = [HasPhoneNumberPermission]

    def get(self, request: APIViewRequest):
        user: CustomUser = request.user
        if not user.is_agent:
            conversations = (
                user.conversations.all()
                .prefetch_related("last_message", "peer")
                .annotate(
                    peer_name=Concat("peer__first_name",
                                     V(" "), "peer__last_name"),
                    peer_email=F("peer__email"),
                    last_message_text=F("last_message__body"),
                    last_message_date=F("last_message__created"),
                    last_message_received=F("last_message__received"),
                    last_message_sended=F("last_message__sended"),
                )
                .order_by("-last_message__created")
            )
        else:
            today = date.today()
            agents = self.get_related_agents(user.id, True, ['id'])
            if len(agents) != 1:
                raise ValidationException()
            agent_id = agents[0].id
            query = f"""
                SELECT 
                    s.id,
                    case when (cl.names IS NOT NULL and cl.lastname IS NOT NULL) then CONCAT(cl.`names`," ", cl.lastname) ELSE s.formatted_telephone END AS peer_name,
                    CASE when cl.email IS NOT NULL then cl.email ELSE '' end AS peer_email,
                    s.formatted_telephone,
                    s.unread_count,
                    s.body,
                    s.created,
                    s.received,
                    s.sended
                FROM
                    (
                        SELECT 
                            c.id,
                            c.unread_count,
                            CASE
                                WHEN LEFT(REPLACE(c.peer_number, ' ', ''), 2) = '+1' THEN REPLACE(c.peer_number, ' ', '')
                                ELSE CONCAT('+1', REPLACE(c.peer_number, ' ', ''))
                        END AS formatted_telephone,
                        s.body,
                            s.created,
                            s.received,
                            s.sended
                        FROM
                            sms_conversation c
                            JOIN sms_object s ON c.last_message_id = s.id
                        WHERE
                            c.user_id={user.id} AND LENGTH(REPLACE(c.peer_number, ' ', '')) > 9 
                    ) s
                    LEFT JOIN 
                        (
                            SELECT 
                                cl.`names`, cl.lastname, cl.email,
                                CASE
                                    WHEN LEFT(REPLACE(REPLACE(cl.telephone, ' ', ''), '-', ''), 2) = '+1' 
                                        THEN REPLACE(REPLACE(cl.telephone, ' ', ''), '-', '')
                                    ELSE CONCAT('+1', REPLACE(REPLACE(cl.telephone, ' ', ''), '-', ''))
                            END AS formatted_telephone
                            FROM client cl
                            where
                                cl.id_agent = {agent_id}
                                AND YEAR(cl.aplication_date)={today.year}
                                AND cl.borrado<>1
                                AND (cl.tipoclient =1 OR cl.tipoclient=3)
                                AND REPLACE(cl.telephone, ' ', '')>9 
                    ) cl ON s.formatted_telephone = cl.formatted_telephone 
                ORDER BY created desc

            """
            map = [
                "id",
                "peer_name",
                "peer_email",
                "peer_number",
                "unread_count",
                "last_message_text",
                "last_message_date",
                "last_message_received",
                "last_message_sended",
            ]
            conversations = self.sql_select_all(
                query, map)
        serializer = SMSConversationListSerializer(conversations, many=True)
        return Response(serializer.data)


class GetConversationSMSView(APIView, Common):
    permission_classes = [HasPhoneNumberPermission]

    def get(self, request: APIViewRequest):
        user: CustomUser = request.user
        conversation_id = int(self.check_none(
            request.query_params.get("id"), 0))
        if not conversation_id:
            raise ValidationException("Not conversation id provided")
        conversation = user.conversations.filter(pk=conversation_id)
        if not conversation.exists():
            raise NotFoundException("Not sus conversation")
        conversation: SMSConversation = conversation.get()
        conversation.unread_count = 0
        conversation.save()
        messages = conversation.sms.all().order_by("-created")
        serializer = SMSSerializer(messages, many=True)
        return Response(serializer.data)


class GetSmsMMediaView(APIView, SmsCommons):
    permission_classes = [HasPhoneNumberPermission]

    def get(self, request: APIViewRequest):
        service = self.sms_get_service()

        sms_sid = request.query_params.get("sms_sid")
        media_sid = request.query_params.get("media_sid")

        if not (sms_sid and media_sid):
            return Response(
                "Both sms_sid and media_sid must be valid",
                status=status.HTTP_400_BAD_REQUEST,
            )

        sms = service.get_sms(sms_sid)
        media = sms.media.get(media_sid).fetch()
        result = service.get_media(media)

        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(result, content_type=media.content_type)

    def get(self, request: APIViewRequest):
        user: CustomUser = request.user
        service = self.sms_get_service()

        media_id = self.check_none(request.query_params.get("id"))
        if not media_id:
            raise ValidationException("Not Media id provided")

        media = user.conversations.annotate(media=F("sms__media__pk")).filter(
            media=media_id
        )
        if not media.exists():
            raise NotFoundException("Not such media")
        media: SMSMedia = SMSMedia.objects.get(pk=media_id)

        result = service.get_media(media.url)

        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(result, content_type=media.content_type)


class DeleteConversation(APIView, Common):
    permission_classes = [HasPhoneNumberPermission]

    def post(self, request: APIViewRequest):
        user = request.user
        conversation_id = self.check_none(request.data.get("id"))
        if not conversation_id:
            raise ValidationException("Not id privided")
        conversation = user.conversations.filter(pk=conversation_id)
        if not conversation.exists():
            raise NotFoundException("Not sus conversation")
        conversation: SMSConversation = conversation.get()
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReceiveStatusUpdate(APIView, SmsCommons):
    def post(self, request: APIViewRequest):
        sms_status = self.check_none(request.data.get("SmsStatus"))
        sms_sid = self.check_none(request.data.get("SmsSid"))
        service = self.sms_get_service()
        if sms_status == 'delivered':
            media_list = service.get_media_list(sms_sid)
            sms = SMS.objects.filter(sid=sms_sid)
            if len(sms) == 1:
                sms = sms.get()
                sms_media_list = SMSMedia.objects.filter(sms_id=sms)
                for media_obj, sms_media in zip(media_list, sms_media_list):
                    uri = media_obj.uri.split(".")[0]
                    SMSMedia.objects.filter(sms_id=sms, id=sms_media.id).update(
                        url="https://api.twilio.com/" + uri, content_type=media_obj.content_type)

        return Response(status=status.HTTP_204_NO_CONTENT)
