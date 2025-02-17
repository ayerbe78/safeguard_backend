from ..imports import *
from .__common import AgentAssistantCommon

from django.db.models import Case, When, Value, CharField, F, OuterRef, Subquery, Exists
import datetime

from ..mailing.service.email_service import EmailService
from safeguard import settings


class AgentListSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField()

    class Meta:
        fields = ("id", "full_name", "license_number",
                  "telephone", 'npn', 'date_start')
        model = Agent


class AgentViewSet(viewsets.ModelViewSet, AgencyManagement, AgentAssistantCommon):
    serializer_class = AgentSerializer
    permission_classes = [HasAgentPermission]

    def get_queryset(self):
        queryset = Agent.objects.exclude(borrado=1)
        return queryset

    def list(self, request, *args, **kwargs):
        # user: CustomUser = request.user

        # subquery = AgentGlobalLicenses.objects.filter(
        #     npn=OuterRef("npn")
        # ).values("npn")

        # queryset = self.get_related_agents(user.pk, True)
        # queryset = queryset.annotate(
        #     full_name=Concat("agent_name", Value(" "), "agent_lastname"),
        #     has_global_license=Exists(subquery)
        # )
        user: CustomUser = request.user
        queryset = self.get_related_agents(user.pk, True)

        queryset = queryset.annotate(
            full_name=Concat("agent_name", V(" "), "agent_lastname")
        )
        queryset = self.__apply_filters(queryset, request)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AgentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AgentListSerializer(queryset, many=True)
        return Response(serializer.data)

    def __apply_filters(self, queryset, request: APIViewRequest):
        search = self.check_none(request.query_params.get("search"))
        medicare = self.check_none(request.query_params.get("medicare"))
        state = self.check_none(request.query_params.get("state"))
        agency = self.check_none(request.query_params.get("agency"))
        released = self.check_none(request.query_params.get("released"))
        life_insurance = self.check_none(
            request.query_params.get("life_insurance"))

        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(license_number__icontains=search)
                | Q(telephone__icontains=search)
                | Q(npn__icontains=search)
            )

        if medicare == 1 or medicare == '1':
            queryset = queryset.filter(medicare=True)
        elif medicare == 2 or medicare == '2':
            queryset = queryset.filter(medicare=False)

        if life_insurance == 1 or life_insurance == '1':
            queryset = queryset.filter(life_insurance=True)
        elif life_insurance == 2 or life_insurance == '2':
            queryset = queryset.filter(life_insurance=False)

        if released == 1 or released == '1':
            queryset = queryset.filter(released=True)
        elif life_insurance == 2 or life_insurance == '2':
            queryset = queryset.filter(life_insurance=False)

        if agency:
            queryset = queryset.filter(id_agency=agency)

        if state:
            queryset = queryset.filter(id_county__id_city__id_state=state)
        queryset = self.apply_order_queryset(queryset, request, "full_name")
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response: Response = super().create(request)
                data = {
                    "password": request.data.get("password"),
                    "email": request.data.get("email"),
                    "username": request.data.get("email"),
                    "first_name": request.data.get("agent_name"),
                    "last_name": request.data.get("agent_lastname"),
                    "personal_phone_number": request.data.get("telephone"),
                }
                if self.exists_users_with_phone(data["personal_phone_number"], None):
                    raise ValidationException(
                        "There is a user with same phone already")
                new_user_id = self.add_to_users(data)
                self.add_to_group(
                    new_user_id, "Agent with Assistant" if request.data.get('id_assistant') != '0' and request.data.get('id_assistant') != 0 else "Agent Without Assistant")
                self.send_email(response)
                return response

        except Exception as e:
            error_string = str(e)
            raise ValidationException(
                error_string
            )

    def send_email(self, response):
        if response.data.get('medicare') or response.data.get('life_insurance'):
            if response.data.get('medicare'):
                to = 'vanessa@sgilh.com'
                title = 'Agent Selling Medicare'
                body = f"The Agent '{response.data.get('agent_name')} {response.data.get('agent_lastname')}', with NPN: {response.data.get('npn')} and License: {response.data.get('license_number')}, will be selling Medicare, please contact the agent at the phone number: '{response.data.get('telephone')}' or one of the followings emails: '{response.data.get('email')}', '{response.data.get('email2')}'."
            if response.data.get('life_insurance'):
                to = 'mredondo@sgilh.com'
                title = 'Agent Selling Life Insurance'
                body = f"The Agent '{response.data.get('agent_name')} {response.data.get('agent_lastname')}', with NPN: {response.data.get('npn')} and License: {response.data.get('license_number')}, will be selling Life Insurances, please contact the agent at the phone number: '{response.data.get('telephone')}' or one of the followings emails: '{response.data.get('email')}', '{response.data.get('email2')}'."

            service = EmailService(user_name="Safeguard & Associates",
                                   email=settings.EMAIL_HOST_USER, passw=settings.EMAIL_SAFEGUARD_PASSWORD)
            service.send_message(to, title, False,
                                 None, None, None, body)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            prev_agent: Agent = self.get_object()
            response = super().update(request, *args, **kwargs)
            agent: Agent = self.get_object()
            agent_user = CustomUser.objects.get(email=prev_agent.email)
            agent_user.email = agent.email
            agent_user.username = agent.email
            if self.exists_users_with_phone(agent.telephone, agent_user):
                raise ValidationException(
                    "There is a user with same phone already")
            agent_user.personal_phone_number = agent.telephone
            agent_user.save()
            return response

    def add_to_users(self, data):
        serializer = RegisterSerializer
        new_user = serializer(data=data)
        new_user.is_valid(raise_exception=True)
        created = new_user.save()
        CustomUser.objects.filter(id=created.pk).update(
            first_name=data["first_name"], last_name=data["last_name"], is_agent=True
        )
        return created.pk

    def add_to_group(self, user_id, group_name):
        group = Group.objects.get(name=group_name)
        user = CustomUser.objects.get(id=user_id)
        user.groups.add(group)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.borrado = 1
        instance.save()
        return Response(instance.pk)


class ExportExcelAgentList(XLSXFileMixin, ReadOnlyModelViewSet, AgencyManagement):
    permission_classes = [HasExportExcelAgentListPermission]
    serializer_class = AgentExportExcelSerializer
    renderer_classes = (XLSXRenderer,)
    xlsx_use_labels = True
    filename = "agents.xlsx"

    def list(self, request):
        user: CustomUser = request.user
        queryset = self.get_related_agents(
            user.pk, True).order_by("agent_name")
        arr = []
        for el in queryset:
            assistant = Assistant.objects.filter(id=el.id_assistant)
            if len(assistant) == 1:
                assistant = assistant.get()
                assistant_str = (
                    assistant.assistant_name + " " + assistant.assistant_lastname
                )
            else:
                assistant_str = ""
            arr.append(
                {
                    "agent_name": el.agent_name + " " + el.agent_lastname,
                    "license": el.license_number,
                    "npn": el.npn,
                    "email": el.email,
                    "email2": el.email2,
                    "phone": el.telephone,
                    "phone2": el.telephone2,
                    "user_cms": el.usercms,
                    "password_cms": el.passcms,
                    "password_sherpa": el.passsherpa,
                    "question1": el.pregunta,
                    "question2": el.pregunta1,
                    "question3": el.pregunta2,
                    "assistant": assistant_str,
                }
            )
        serializer = self.get_serializer(arr, many=True)
        return Response(serializer.data)


class DataForAgent(APIView, AgencyManagement):
    permission_classes = [HasAgentPermission]
    serializer_class = AssitStateSerializer

    def get(self, request):
        user = request.user

        agents = (
            self.get_related_agents(user.pk, True)
            .values("id", "agent_name", "agent_lastname", "id_agency", "id_assistant")
            .order_by("agent_name", "agent_lastname")
        )
        agency = (
            self.get_related_agencies(user.pk, True)
            .values("id", "agency_name")
            .order_by("agency_name")
        )
        assistant = (
            self.get_related_assistants(user.pk, True)
            .values("id", "assistant_name", "assistant_lastname")
            .order_by("assistant_name", "assistant_lastname")
        )
        insurances = Insured.objects.all().order_by("names").values("id", "names")
        state = State.objects.all().order_by("names").values("id", "names")
        language = Language.objects.all().order_by("names").values("id", "names")
        groups = CommissionsGroup.objects.all().values("id", "names")
        language_serializer = LanguageOnlyNameSerializer(language, many=True)
        agent_serializer = AgentOnlyNameSerializer(agents, many=True)
        insurance_serializer = InsuredOnlyNameSerializer(insurances, many=True)
        agency_serializer = AgencyOnlyNameSerializer(agency, many=True)
        state_serializer = StateOnlyNameSerializer(state, many=True)
        assistant_serializer = AssistantOnlyNameSerializer(
            assistant, many=True)

        return Response(
            {
                "agents": agent_serializer.data,
                "languages": language_serializer.data,
                "insurances": insurance_serializer.data,
                "agency": agency_serializer.data,
                "state": state_serializer.data,
                "language": language_serializer.data,
                "assistant": assistant_serializer.data,
                "groups": groups,
            },
            status=status.HTTP_200_OK,
        )


class AgentDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAgentDocumentPermission]
    serializer_class = AgentDocumentSerializer
    queryset = AgentDocument.objects.all()


class GETAgentExcelInformation(APIView, LimitOffsetPagination, AgencyManagement):
    permission_classes = [HasAgentPermission]

    def get(self, request: APIViewRequest):
        npn = request.GET.get('npn', None)
        agent_app = AgentGlobalAppointments.objects.filter(npn=npn)
        agent_app_serializer = AgentGlobalAppointmentsSerializer(
            agent_app, many=True)
        agent_ce = AgentGlobalCE.objects.filter(npn=npn)
        agent_ce_serializer = AgentGlobalCESerializer(agent_ce, many=True)
        agent_lic = AgentGlobalLicenses.objects.filter(npn=npn)
        agent_lic_serializer = AgentGlobalLicensesSerializer(
            agent_lic, many=True)
        return Response({
            "appointments": agent_app_serializer.data,
            "ces": agent_ce_serializer.data,
            "licenses": agent_lic_serializer.data,
        })


class CheckAgentLicenseExp(APIView, LimitOffsetPagination, AgencyManagement):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: APIViewRequest):
        user = request.user
        agent = Agent.objects.filter(email=user.email).get()

        agent_ce = AgentGlobalCE.objects.filter(npn=agent.npn).first()
        if agent_ce:
            agent_ce_date = self.date_from_text(
                agent_ce.ce_due_date.replace('12:00:00 AM', "").replace(" ", ""), "%m/%d/%Y")
            today = date.today()
            three_months_before_due_date = agent_ce_date - \
                datetime.timedelta(days=90)

            if today >= three_months_before_due_date:
                raise ValidationException(
                    'Agent License Expires: '+str(agent_ce_date))

        return Response(status=status.HTTP_200_OK)


class AgentTaxDocsViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAgentTaxDocsPermission]
    serializer_class = AgentTaxDocumentSerializer
    queryset = AgentTaxDocument.objects.all()


class AgentTaxDocs(APIView):
    permission_classes = [HasAgentTaxDocsPermission]
    serializer_class = AgentTaxDocumentSerializer

    def get(self, request):
        if request.GET.get("id") == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        id_agent = request.GET.get("id")
        docs = AgentTaxDocument.objects.filter(id_agent=id_agent)
        serializer = self.serializer_class(docs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
