from .test.test import *
from .sms.views import *
from .mailing.views import *
from .main.views import *
from .reports.views import *
from .settings.views import *
from .utility.views import *
from .logging.views import *
import csv
from email.policy import default
from math import ceil, floor
from select import select
from django.db import connection

from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
from content.models import *
from content.serializers import *
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date, datetime
from customauth.GroupsPermission import *
from customauth.models import CustomUser
from customauth.serializers import (
    ListUserSerializer,
    RegisterSerializer,
    UserSerializer,
)
from rest_framework.pagination import LimitOffsetPagination
import io
from django.http import FileResponse, HttpRequest
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A3
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table, TableStyle, colors
from django.db import transaction
from django.db.models import Q
from django.db.models import Max
from django.contrib.auth.models import Group
from content.business.business import AgencyManagement
from content.business.logging.db_logging_service import log_empty_payment
from django.views.static import serve
import logging
from urllib.parse import unquote
logger = logging.getLogger("django")

# @permission_required('content.view_agent',raise_exception=True)


class AssitInsuranceViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAssitInsurancePermission]
    serializer_class = AssitInsuranceSerializer
    queryset = AssitInsurance.objects.all()


class SendsmsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = SendsmsSerializer
    queryset = Sendsms.objects.all()


class TypePendingdocViewSet(viewsets.ModelViewSet):
    # permission_classes = [HasClientPermission]
    serializer_class = TypePendingdocSerializer
    queryset = TypePendingdoc.objects.all()


class CommAgentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCommAgentPermission]
    serializer_class = CommAgentSerializer

    def get_queryset(self):
        today = date.today()
        return CommAgent.objects.filter(yearcom=today.year)


class SubassistantViewSet(viewsets.ModelViewSet):
    serializer_class = SubassistantSerializer
    queryset = Subassistant.objects.all()
    permission_classes = [IsAdmin]


class MedicareViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = MedicareSerializer
    queryset = Medicare.objects.all()


class ClientMedicareViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = ClientMedicareSerializer
    queryset = ClientMedicare.objects.all()


class ProspectManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = ProspectManagerSerializer
    queryset = ProspectManager.objects.all()


class UpdocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = UpdocumentSerializer
    queryset = Updocument.objects.all()


class AgentInsuredViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAgentInsuredPermission]
    serializer_class = AgentInsuredSerializer
    queryset = AgentInsured.objects.all()


class AgentPortalViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAgentPortalPermission]
    serializer_class = AgentPortalSerializer
    queryset = AgentPortal.objects.all()


class AgentLanguageViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAgentLanguagePermission]
    serializer_class = AgentLanguageSerializer
    queryset = AgentLanguage.objects.all()


class AgentStateViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAgentStatePermission]
    serializer_class = AgentStateSerializer
    queryset = AgentState.objects.all()


class StatesByAgent(APIView):
    permission_classes = [HasAgentStatePermission]
    serializer_class = AgentStateSerializer

    def get(self, request):
        arr = []
        list = AgentState.objects.filter(id_agent=request.GET.get("id"))
        for el in list:
            arr.append(el.id_state.id)
        return Response(arr, status=status.HTTP_200_OK)


class AgentProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AgentProductSerializer
    queryset = AgentProduct.objects.all()


class AssitStateViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAssitStatePermission]
    serializer_class = AssitStateSerializer
    queryset = AssitState.objects.all()


class HistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [HasHistoryPermission]
    serializer_class = HistorySerializer
    queryset = History.objects.all()


class LogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = LogSerializer
    queryset = Log.objects.all()


class MedicareSocialViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = MedicareSocialSerializer
    queryset = MedicareSocial.objects.all()


class MenuViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()


class PaymentsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()


class PaymentsGlobalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = PaymentsGlobalSerializer
    queryset = PaymentsGlobal.objects.all()


class PaymentsGlobalTmpViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = PaymentsGlobalTmpSerializer
    queryset = PaymentsGlobalTmp.objects.all()


class PaymentsagencyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = PaymentsagencySerializer
    queryset = Paymentsagency.objects.all()


class PaymentsasistentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = PaymentsasistentSerializer
    queryset = Paymentsasistent.objects.all()


class PermisosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = PermisosSerializer
    queryset = Permisos.objects.all()


class ProstManegerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = ProstManegerSerializer
    queryset = ProstManeger.objects.all()


class RegistreAsisViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = RegistreAsisSerializer
    queryset = RegistreAsis.objects.all()


class RegistroViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = RegistroSerializer
    queryset = Registro.objects.all()


class Table5ViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = Table5Serializer
    queryset = Table5.objects.all()


class ExtraFieldsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = ExtraFieldsSerializer
    queryset = ExtraFields.objects.all()


class GetCountiesByState(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CountySerializer

    def get(self, request):
        arrayCounties = []
        querysetCities = City.objects.filter(
            id_state=request.GET.get("id_state"))
        for el in querysetCities:
            results = County.objects.filter(id_city=el.id)
            for inn in results:
                arrayCounties.append(inn)
        serializer = self.serializer_class(arrayCounties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetByStateCounty(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CountySerializer

    def get(self, request):
        county = County.objects.get(id=request.GET.get("id"))
        county_list = County.objects.filter(id_city=county.id_city.id)
        # state = State.objects.get(id=county.id_city.id_state)
        state = county.id_city.id_state
        serializer = self.serializer_class(county_list, many=True)
        return Response(
            {"id_state": state.id, "county_list": serializer.data},
            status=status.HTTP_200_OK,
        )


class LanguagesByAgent(APIView):
    permission_classes = [HasLanguageByAgentPermission]
    serializer_class = AgentLanguage

    def get(self, request):
        arr = []
        list = AgentLanguage.objects.filter(id_agent=request.GET.get("id"))
        for el in list:
            arr.append(el.id_language.id)
        return Response(arr, status=status.HTTP_200_OK)


class AgentPortalsByAgent(APIView):
    permission_classes = [HasAgentPortalPermission]
    serializer_class = AgentPortalSerializer

    def get(self, request):
        list = AgentPortal.objects.filter(agent=request.GET.get("id"))
        return Response(self.serializer_class(list, many=True).data, status=status.HTTP_200_OK)


class InsurancesByAgent(APIView):
    permission_classes = [HasInsurancesByAgentPermission]
    serializer_class = AgentInsured

    def get(self, request):
        arr = []
        list = AgentInsured.objects.filter(id_agent=request.GET.get("id"))
        for el in list:
            arr.append(el.id_insured)
        return Response(arr, status=status.HTTP_200_OK)


class AssistStateByAgent(APIView, AgencyManagement):
    permission_classes = [HasAssistStateByAgentPermission]
    serializer_class = AssitStateSerializer

    def get(self, request):
        agent = self.select_agent(request.GET.get("id"), request.user.id)
        list = AssitState.objects.filter(
            id_agente=agent.id, id_asistente=agent.id_assistant)
        serializer = self.serializer_class(list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentsByAssistant(APIView, AgencyManagement):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListAgentSerializer

    def get(self, request):
        assistant = Assistant.objects.filter(id=request.GET.get('id'))
        if len(assistant) == 1:
            assistant = assistant.get()
            assistant_user = CustomUser.objects.filter(
                email=assistant.email)
            if len(assistant_user) == 1:
                assistant_user = assistant_user.get()
        agents = self.get_related_agents(
            request.user.id).filter(id_assistant=assistant.id)
        if not assistant_user:
            raise ValidationException('Assistant not Found')
        x = date.today()
        a = date(x.year, 1, 1)
        b = date(x.year, 12, 31)
        clients = self.get_related_clients(assistant_user.id)
        for el in agents:
            filter_clients = clients.filter(
                aplication_date__range=[a, b], id_agent=el.id).values('id')
            el.client_count = len(filter_clients)
        serializer = self.serializer_class(agents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssistInsuranceByAgent(APIView, AgencyManagement):
    permission_classes = [HasAssistInsuranceByAgentPermission]
    serializer_class = AssitInsuranceSerializer

    def get(self, request):
        agent = self.select_agent(request.GET.get("id"), request.user.id)
        list = AssitInsurance.objects.filter(
            id_agente=agent.id, id_asistente=agent.id_assistant)
        serializer = self.serializer_class(list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditLanguageInAgent(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgentLanguageSerializer

    def post(self, request):
        user = request.user
        if user.is_admin or user.has_perm("content.change_agent"):
            agent = Agent.objects.get(id=request.data.get("id_agent"))
            if isAgent(user):
                agent_user = Agent.objects.filter(email=user.email).get()
                if agent.id != agent_user.id:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            if isAssistant(user):
                assistant = Assistant.objects.filter(email=user.email).get()
                if assistant.id != agent_user.id_assistant:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            list = request.data.get("list")
            AgentLanguage.objects.filter(
                id_agent=request.data.get("id_agent")).delete()
            for el in list:
                language = Language.objects.get(id=el)
                AgentLanguage.objects.create(
                    id_agent=agent, id_language=language)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class EditAgentState(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgentStateSerializer

    def post(self, request):
        user = request.user
        if user.is_admin or user.has_perm("content.change_agent"):
            agent = Agent.objects.get(id=request.data.get("id_agent"))
            if isAgent(user):
                agent_user = Agent.objects.filter(email=user.email).get()
                if agent.id != agent_user.id:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            if isAssistant(user):
                assistant = Assistant.objects.filter(email=user.email).get()
                if assistant.id != agent_user.id_assistant:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            list = request.data.get("list")
            AgentState.objects.filter(
                id_agent=request.data.get("id_agent")).delete()
            for el in list:
                state = State.objects.get(id=el)
                AgentState.objects.create(
                    id_agent=agent, id_state=state)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class EditInsuranceInAgent(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgentInsuredSerializer

    def post(self, request):
        user = request.user
        if user.is_admin or user.has_perm("content.change_agent"):
            agent = Agent.objects.filter(id=request.data.get("id_agent"))
            agent = agent.get()
            if isAgent(user):
                agent_user = Agent.objects.filter(email=user.email).get()
                if agent.id != agent_user.id:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            if isAssistant(user):
                assistant = Assistant.objects.filter(email=user.email).get()
                if assistant.id != agent.id_assistant:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            list = request.data.get("list")
            AgentInsured.objects.filter(
                id_agent=request.data.get("id_agent")).delete()
            for el in list:
                insured = Insured.objects.filter(id=el).get()
                AgentInsured.objects.create(
                    id_agent=agent.id, id_insured=insured.id)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class EditInsuranceAssistInAgent(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssitInsuranceSerializer

    def post(self, request):
        user = request.user
        if user.is_admin or user.has_perm("content.change_agent"):
            agent = Agent.objects.filter(
                id=request.data.get("id_agente")).get()
            if isAgent(user):
                agent_user = Agent.objects.filter(email=user.email).get()
                if agent.id != agent_user.id:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            if isAssistant(user):
                assistant = Assistant.objects.filter(email=user.email).get()
                if assistant.id != agent_user.id_assistant:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            list = request.data.get("list")
            AssitInsurance.objects.filter(
                id_agente=request.data.get("id_agente"),
                id_asistente=request.data.get("id_asistente"),
                posicion=request.data.get("posicion"),
            ).delete()
            for el in list:
                AssitInsurance.objects.create(
                    id_agente=request.data.get("id_agente"),
                    id_insurance=el,
                    id_asistente=request.data.get("id_asistente"),
                    posicion=request.data.get("posicion"),
                )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class EditStateAssistInAgent(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssitStateSerializer

    def post(self, request):
        user = request.user
        if user.is_admin or user.has_perm("content.change_agent"):
            agent = Agent.objects.get(id=request.data.get("id_agente"))
            if isAgent(user):
                agent_user = Agent.objects.filter(email=user.email).get()
                if agent.id != agent_user.id:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            if isAssistant(user):
                assistant = Assistant.objects.filter(email=user.email).get()
                if assistant.id != agent_user.id_assistant:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            list = request.data.get("list")
            AssitState.objects.filter(
                id_agente=request.data.get("id_agente"),
                id_asistente=request.data.get("id_asistente"),
                posicion=request.data.get("posicion"),
            ).delete()
            for el in list:
                AssitState.objects.create(
                    id_agente=request.data.get("id_agente"),
                    id_state=el,
                    id_asistente=request.data.get("id_asistente"),
                    posicion=request.data.get("posicion"),
                )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class GetAllAgents(APIView):
    permission_classes = [IsAdmin]

    serializer_class = AgentSerializer

    def get(self, request):
        user = request.user
        if user.is_admin:
            queryset = Agent.objects.all()
        if user.is_agent:
            queryset = Agent.objects.filter(email=user.email)
        if user.is_assistant:
            assistant = Assistant.objects.filter(email=user.email).get()
            queryset = Agent.objects.filter(id_assistant=assistant.id)
        # if user.is_subassistant:
        serializer = self.serializer_class(
            queryset.order_by("agent_name"), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DataForImportCsv(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssitStateSerializer

    def get(self, request):
        user = request.user
        if (
            user.is_admin
            or isAgent(user)
            and user.has_perm("content.add_importpaymentcsv")
            or isAssistant(user)
            and user.has_perm("content.add_importpaymentcsv")
        ):
            insurances = Insured.objects.all().order_by("names").values("id", "names")
            insurance_serializer = InsuredOnlyNameSerializer(
                insurances, many=True)
            return Response(
                {"insurances": insurance_serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class DataForImportBob(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssitStateSerializer

    def get(self, request):
        user = request.user
        if (
            user.is_admin
            or isAgent(user)
            and user.has_perm("content.add_importbob")
            or isAssistant(user)
            and user.has_perm("content.add_importbob")
        ):
            insurances = Insured.objects.all().order_by("names").values("id", "names")
            insurance_serializer = InsuredOnlyNameSerializer(
                insurances, many=True)
            return Response(
                {"insurances": insurance_serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class AgentDocs(APIView):
    permission_classes = [HasAgentDocsPermission]
    serializer_class = AgentDocumentSerializer

    def get(self, request):
        if request.GET.get("id") == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        id_agent = request.GET.get("id")
        docs = AgentDocument.objects.filter(id_agent=id_agent)
        serializer = self.serializer_class(docs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientNotes(APIView):
    # permission_classes = [HasClientNotesPermission]
    serializer_class = HistorySerializer

    def get(self, request):
        if request.GET.get("id_client") == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        notes = History.objects.filter(id_client=request.GET.get("id_client"))
        serializer = self.serializer_class(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteAgentPaymentCSV(APIView, PaymentCommons):
    permission_classes = [HasDeletePaymentCSVPermission]

    def post(self, request):
        user = request.user
        year = request.data.get("year")
        month = request.data.get("month")
        insured = request.data.get("insured")
        if user.is_admin or user.has_perm("content.delete_importpaymentcsv"):
            if year == None or month == None or insured == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                if month == 1 or month == "1":
                    str_month = "january"
                    month_mod = " AND (month='01' OR month='1')"
                elif month == 2 or month == "2":
                    str_month = "february"
                    month_mod = " AND (month='02' OR month='2')"
                elif month == 3 or month == "3":
                    str_month = "march"
                    month_mod = " AND (month='03' OR month='3')"
                elif month == 4 or month == "4":
                    str_month = "april"
                    month_mod = " AND (month='04' OR month='4')"
                elif month == 5 or month == "5":
                    str_month = "may"
                    month_mod = " AND (month='05' OR month='5')"
                elif month == 6 or month == "6":
                    str_month = "june"
                    month_mod = " AND (month='06' OR month='6')"
                elif month == 7 or month == "7":
                    str_month = "july"
                    month_mod = " AND (month='07' OR month='7')"
                elif month == 8 or month == "8":
                    str_month = "august"
                    month_mod = " AND (month='08' OR month='8')"
                elif month == 9 or month == "9":
                    str_month = "september"
                    month_mod = " AND (month='09' OR month='9')"
                elif month == 10 or month == "10":
                    str_month = "october"
                    month_mod = " AND month='10'"
                elif month == 11 or month == "11":
                    str_month = "november"
                    month_mod = " AND month='11'"
                elif month == 12 or month == "12":
                    str_month = "dicember"
                    month_mod = " AND month='12'"
                with transaction.atomic():
                    cursor = connection.cursor()
                    sql = (
                        "DELETE from payments_global where id_insured="
                        + str(insured)
                        + " AND pyear='"
                        + str(year)
                        + "'"
                        + month_mod
                    )
                    cursor.execute(sql)
                    cursor.close()

                    cursor = connection.cursor()
                    sql = f"""
                        DELETE FROM zero_payment_logs 
                        WHERE insured_id={insured} and payment_year={year} and (payment_month={month} or  payment_month='0{month}')

                    """
                    cursor.execute(sql)
                    cursor.close()

                    cursor = connection.cursor()
                    sql = f"""
                        DELETE FROM unassigned_payments 
                        WHERE id_insured={insured} and year={year} and (month={month} or  month='0{month}')

                    """
                    cursor.execute(sql)
                    cursor.close()

                    self.backup_repayments(insured, year, month)
                    cursor = connection.cursor()
                    sql = f"""
                        DELETE from agent_payments
                        WHERE id_insured={insured} and year={year} {month_mod} 
                    """
                    cursor.execute(sql)
                    cursor.close()
                    self.delete_future_payments(insured, year, month)

                    PaymentExcel.objects.filter(year=year, insured=insured).filter(
                        Q(month=month) | Q(month=f'0{month}')).delete()

                    return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def delete_future_payments(self, insured, year, month):
        FuturePayments.objects.filter(
            id_insured=insured, year=year, month=self.inverse_map_month(self.map_month(month))).delete()

    def backup_repayments(self, insured, year, month):
        payments = AgentPayments.objects.filter(
            id_insured=insured, year=year, month=self.inverse_map_month(self.map_month(month)), payment_index=2).exclude(commission=0)
        for payment in payments:
            data = Repayments(
                id_agent=payment.id_agent,
                id_client=payment.id_client,
                id_insured=payment.id_insured,
                id_state=payment.id_state,
                year=payment.year,
                month=payment.month,
                info_month=payment.info_month,
                payment_type=payment.payment_type,
                agent_name=payment.agent_name,
                client_name=payment.client_name,
                insured_name=payment.insured_name,
                suscriberid=payment.suscriberid,
                members_number=payment.members_number,
                payment_index=payment.payment_index,
                commission=payment.commission,
                description=payment.description,
            )
            data.save()


class MakeAgentRePayment(APIView, PaymentCommons):
    permission_classes = [HasMakeRepaymentPermission]

    def post(self, request: HttpRequest):
        user = request.user
        year = request.data.get("year")
        request_month = request.data.get("month")
        insured = request.data.get("insured")
        agent = self.check_none(request.data.get("agent"))
        payment = request.data.get("payment")
        search = request.data.get("search")
        cursor = connection.cursor()
        count = 0
        with transaction.atomic():
            if user.is_admin or user.has_perm("content.change_importpaymentcsv"):
                if (
                    year == None
                    or request_month == None
                    or insured == None
                    or payment == None
                    or payment == "0"
                    or payment == "1"
                ):
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    str_month = self.map_month(request_month)
                    month = self.inverse_map_month(str_month)
                    current_date = datetime.now()
                    current_month = current_date.month
                    current_year = current_date.year
                    month_will_pay, year_will_pay = self.__get_month_year_will_pay(
                        current_year, insured, current_month)
                    try:
                        insured_obj = Insured.objects.get(id=insured)
                    except:
                        raise ValidationException(
                            f"There is not such insured with id {insured}"
                        )

                    if request.data.get('old_system'):
                        count = self.pay_old_repayment(
                            agent, insured, year, str_month, search, month_will_pay, year_will_pay, insured_obj, request_month)
                    else:
                        count = self.__pay_new_repayment(
                            insured, request_month, year, agent, search, month_will_pay, year_will_pay, insured_obj)

                    return Response(count)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

    def __check_already_repaid(self, suscriberid, insured, info_month):
        payments = AgentPayments.objects.filter(
            suscriberid=suscriberid, id_insured=insured, info_month=info_month).exclude(commission=0).count()
        repayments = Repayments.objects.filter(
            suscriberid=suscriberid, id_insured=insured, info_month=info_month).exclude(commission=0).count()
        future_payments = FuturePayments.objects.filter(
            suscriberid=suscriberid, id_insured=insured, info_month=info_month).exclude(commission=0).count()
        return payments+repayments + future_payments != 0

    def __get_month_year_will_pay(self, year, insured, month):
        result_month = 0
        result_year = 0
        past_month = month-1
        past_month_year = year
        if month-1 == 0:
            past_month = 12
            past_month_year = year-1
        else:
            past_month = self.inverse_map_month(self.map_month(past_month))
        if AgentPayments.objects.filter(
                id_insured=insured, month=past_month, year=past_month_year).count() == 0:
            result_month = past_month
            result_year = past_month_year
        elif AgentPayments.objects.filter(
                id_insured=insured, month=self.inverse_map_month(self.map_month(month)), year=year).count() == 0:
            result_month = month
            result_year = year
        else:
            result_month = month+1 if month+1 != 13 else 1
            result_year = year if month+1 != 13 else year+1
        return self.inverse_map_month(self.map_month(result_month)), result_year

    def __pay_new_repayment(self, insured, month, year, agent, search, month_will_pay, year_will_pay, insured_obj):
        agent_filter = f" and id_agent={agent} " if agent else ""

        cursor = connection.cursor()
        sql = f"""
            SELECT 
                pg.n_member, pg.p_number,
                pg.p_state,pg.new_ren,pg.info_month,pg.id, pg.commission, pg.c_name, pg.description
            FROM 
                payments_global pg 
                left join 
                (
                    SELECT * FROM agent_payments WHERE repaid_on is NULL GROUP BY suscriberid, info_month
                ) ap 
                    ON (pg.p_number=ap.suscriberid AND pg.info_month= ap.info_month)
                left join 
                (
                    SELECT * FROM repayments GROUP BY suscriberid, info_month
                ) rp 
                    ON (pg.p_number=rp.suscriberid AND pg.info_month= rp.info_month)
                left join 
                (
                    SELECT * FROM future_payments  GROUP BY suscriberid, info_month
                ) ft 
                    ON (pg.p_number=ft.suscriberid AND pg.info_month= ft.info_month)
            WHERE 
                pg.id_insured={insured} AND pg.info_month='{month}/1/{year}' AND ap.id IS NULL  AND rp.id IS NULL AND ft.id IS null
                AND pg.p_number IN (SELECT suscriberid FROM client WHERE borrado<>1 AND YEAR(aplication_date)={year} AND (tipoclient=1 OR tipoclient=3) {agent_filter}  AND id_insured={insured}) 
                AND (pg.p_number like '%{search}%')

        """
        cursor.execute(sql)
        all = cursor.fetchall()
        cursor.close()
        inverse_mapped_month = self.inverse_map_month(self.map_month(month))
        count = 0
        for row in all:
            comm_date = self.date_from_text(row[4])
            clients = Client.objects.filter(
                suscriberid=row[1],
                id_insured=insured,
                aplication_date__year=comm_date.year,
            ).exclude(borrado=1)
            if clients.count() != 1:
                continue
            client = clients.get()
            if not comm_date:
                continue
            agent_obj = Agent.objects.filter(id=client.id_agent)
            if not agent_obj.exists():
                continue
            else:
                agent_obj = agent_obj.get()
                has_assistant = True if hasattr(
                    agent_obj, 'commission_group') and agent_obj.commission_group and agent_obj.commission_group.pk == 1 else False
                agent_year_comm = self.pay_get_agent_year_commission(
                    agent_obj.pk, insured, comm_date.year, row[2], row[
                        3], inverse_mapped_month, year, has_assistant
                )
                total_commission = abs(
                    float(agent_year_comm)) * abs(int(row[0]))
                if float(row[6]) == 0:
                    total_commission = 0
                elif float(row[6]) < 0:
                    total_commission = -total_commission

                data = Repayments(
                    id_agent=agent_obj.id,
                    id_client=client.id,
                    id_insured=insured_obj.id,
                    id_state=client.id_state,
                    # Strings
                    year=year_will_pay,
                    month=month_will_pay,
                    info_month=row[4],
                    payment_type=row[3],
                    agent_name=f"{agent_obj.agent_name} {agent_obj.agent_lastname}",
                    client_name=row[7],
                    insured_name=insured_obj.names,
                    suscriberid=client.suscriberid,
                    description=row[8],
                    # Numbers
                    members_number=row[0],
                    payment_index=2,
                    commission=total_commission
                )
                count += 1
                data.save()

                ap_data = AgentPayments(
                    id_agent=agent_obj.id,
                    id_client=client.id,
                    id_insured=insured_obj.id,
                    id_state=client.id_state,
                    # Strings
                    year=year,
                    month=inverse_mapped_month,
                    info_month=row[4],
                    repaid_on=f"{month_will_pay}/01/{year_will_pay}",
                    payment_type=row[3],
                    agent_name=f"{agent_obj.agent_name} {agent_obj.agent_lastname}",
                    client_name=row[7],
                    insured_name=insured_obj.names,
                    suscriberid=client.suscriberid,
                    description=row[8],
                    # Numbers
                    members_number=row[0],
                    payment_index=2,
                    commission=0
                )
                ap_data.save()
        return count

    def check_old_already_paid(self, month, id_client, year):
        cursor = connection.cursor()
        sql = (
            f"""
                Select {self.map_month(month)}, id from payments where id_client={id_client} and fecha={year}
            """
        )
        cursor.execute(sql)
        entries = cursor.fetchone()
        cursor.close()
        if entries[0] != 0:
            return True
        cursor = connection.cursor()
        sql = (
            f"""
                Select * from payments_control control where month ={month} and id_payment={entries[1]} and year_made={year} Limit 1
            """
        )
        cursor.execute(sql)
        all = cursor.fetchall()
        cursor.close()
        return True if len(all) > 0 and all[0] else False

    def pay_old_repayment(self, agent, insured, year, str_month, search, month_will_pay, year_will_pay, insured_obj, incoming_month):
        month = self.inverse_map_month(str_month)
        if not agent:
            raise ValidationException('Missing Agent Filter')
        agent_obj = Agent.objects.filter(id=agent).get()
        cursor = connection.cursor()
        sql = (
            "Select c.suscriberid,c.id from payments p inner join client c on p.id_client=c.id "
            + f" join agent a on p.id_agent = a.id where p.id_agent="
            + str(agent)
            + " and c.id_insured="
            + str(insured)
            + " and p.fecha='"
            + str(year)
            + "' and p."
            + str_month
            + "=0 "
            + "and year(c.aplication_date) = "
            + str(year)
            + f"""
                and c.borrado<>1 and (concat(a.agent_name,' ',a.agent_lastname) like '%{search}%'
                or concat(c.names,' ',c.lastname) like '%{search}%' OR c.suscriberid LIKE '%{search}%')
            and c.suscriberid not in (SELECT
                    c.suscriberid
                FROM
                    payments p
                LEFT JOIN client c ON
                    p.id_client = c.id
                WHERE
                    p.fecha = '{str(year)}' AND p.{str_month} <> 0  and c.suscriberid is not Null 
                    
                Group by c.suscriberid)
                
                """
        )
        cursor.execute(sql)
        unpaid_policies = cursor.fetchall()
        cursor.close()

        count = 0
        for el in unpaid_policies:
            suscriberid = el[0]
            if self.__check_duplicated_subscriber(suscriberid, insured_obj.id, year):
                continue
            id_client = el[1]

            cursor = connection.cursor()
            sql = (
                "SELECT sum(case when(pg.commission > 0) then pg.n_member else 0 end),  sum(case when(pg.commission < 0) then pg.n_member else 0 end),pg.p_number,pg.p_state,pg.new_ren,pg.info_month, month, pyear FROM `payments_global` pg where pg.info_month=" +
                f"'{incoming_month}/1/{year}'"
                + "and pg.id_insured="
                + str(insured_obj.id)
                + " and pg.p_number='"
                + str(suscriberid)
                + "' GROUP by pg.p_number,pg.info_month"
            )
            cursor.execute(sql)
            all = cursor.fetchall()
            cursor.close()
            for row in all:
                if self.__check_already_repaid(suscriberid, insured_obj.id, row[5]):
                    continue
                if self.check_old_already_paid(row[6], id_client, row[7]):
                    continue
                comm_year = self.date_from_text(row[5])
                if not comm_year:
                    continue

                agent_year_comm = self.pay_get_agent_year_commission(
                    agent,
                    insured_obj.id,
                    comm_year.year,
                    row[3],
                    row[4],
                    month,
                    year,
                )
                positive_commission = (
                    self.pay_get_agent_payment_using_commission(
                        1, agent_year_comm, row[0]
                    )
                )
                negative_commission = (
                    self.pay_get_agent_payment_using_commission(
                        -1, agent_year_comm, row[1]
                    )
                )
                total_commission = positive_commission + negative_commission
                if total_commission == 0:
                    continue
                total_members = row[0] + row[1]

                client = Client.objects.filter(id=id_client).get()

                if not agent_obj or not client or not insured:
                    continue

                data = Repayments(
                    id_agent=agent_obj.id,
                    id_client=client.id,
                    id_insured=insured_obj.id,
                    id_state=client.id_state,
                    # Strings
                    year=year_will_pay,
                    month=month_will_pay,
                    info_month=row[5],
                    payment_type=row[4],
                    agent_name=f"{agent_obj.agent_name} {agent_obj.agent_lastname}",
                    client_name=f"{client.names} {client.lastname}",
                    insured_name=insured_obj.names,
                    suscriberid=client.suscriberid,
                    # Numbers
                    members_number=total_members,
                    payment_index=2,
                    commission=total_commission
                )
                count += 1
                data.save()

                ap_data = AgentPayments(
                    id_agent=agent_obj.id,
                    id_client=client.id,
                    id_insured=insured_obj.id,
                    id_state=client.id_state,
                    # Strings
                    year=year,
                    month=month,
                    info_month=row[5],
                    repaid_on=f"{month_will_pay}/01/{year_will_pay}",
                    payment_type=row[4],
                    agent_name=f"{agent_obj.agent_name} {agent_obj.agent_lastname}",
                    client_name=f"{client.names} {client.lastname}",
                    insured_name=insured_obj.names,
                    suscriberid=client.suscriberid,
                    # Numbers
                    members_number=total_members,
                    payment_index=2,
                    commission=0
                )
                ap_data.save()
        return count

    def __check_duplicated_subscriber(self, subscriberid, insured_id, year):
        clients = Client.objects.filter(
            suscriberid=subscriberid,
            id_insured=insured_id,
            aplication_date__year=year,
        ).exclude(borrado=1)
        if clients.count() != 1:
            return True
        return False


class ImportBobCSV(APIView):
    permission_classes = [HasImportBOBPermission]

    def post(self, request, *args, **kwargs):
        # get params

        insured = request.data.get("insured")
        agent_firstname = request.data.get("agentFirstName")
        agent_lastname = request.data.get("agentLastName")
        client_name = request.data.get("clientName")
        client_lastname = request.data.get("clientLastName")
        policy_number = request.data.get("policyNumber")
        num_members = request.data.get("numberOfMembers")
        request_client_dob = request.data.get("clientDOB")
        state = request.data.get("policyHolderState")
        request_policy_rec_date = request.data.get("policyReceivedDate")
        elegible = request.data.get("eligibleForCommission")
        request_effective_date = request.data.get("effectiveDate")
        request_paid_date = request.data.get("paidThroughDate")
        request_term_date = request.data.get("terminationDate")
        client_phone = request.data.get("clientPhoneNumber")
        policy_status = request.data.get("policyStatus")
        agent_npn = request.data.get("npn")

        # file stuff
        file = request.data.get("file")
        decoded_file = file.read().decode()
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)

        bobs = []
        delete = BobGlobal.objects.filter(id_insured=insured).delete()
        first = True
        for row in reader:
            if first:
                first = False
                continue
            if (
                request_effective_date != None
                and row[int(request_effective_date)] != None
            ):
                try:
                    format = "%m/%d/%Y"
                    effective_date = datetime.strptime(
                        row[int(request_effective_date)], format
                    ).date()
                except ValueError:
                    try:
                        format = "%m/%d/%y"
                        effective_date = datetime.strptime(
                            row[int(request_effective_date)], format
                        ).date()
                    except ValueError:
                        effective_date = None
            else:
                effective_date = None
            if request_client_dob != None and row[int(request_client_dob)] != None:
                try:
                    format = "%m/%d/%Y"
                    client_dob = datetime.strptime(
                        row[int(request_client_dob)], format
                    ).date()
                except ValueError:
                    try:
                        format = "%m/%d/%y"
                        client_dob = datetime.strptime(
                            row[int(request_client_dob)], format
                        ).date()
                    except ValueError:
                        client_dob = None
            else:
                client_dob = None
            if (
                request_policy_rec_date != None
                and row[int(request_policy_rec_date)] != None
            ):
                try:
                    format = "%m/%d/%Y"
                    policy_rec_date = datetime.strptime(
                        row[int(request_policy_rec_date)], format
                    ).date()
                except ValueError:
                    try:
                        format = "%m/%d/%y"
                        policy_rec_date = datetime.strptime(
                            row[int(request_policy_rec_date)], format
                        ).date()
                    except ValueError:
                        policy_rec_date = None
            else:
                policy_rec_date = None
            if request_paid_date != None and row[int(request_paid_date)] != None:
                try:
                    format = "%m/%d/%Y"
                    paid_date = datetime.strptime(
                        row[int(request_paid_date)], format
                    ).date()
                except ValueError:
                    try:
                        format = "%m/%d/%y"
                        paid_date = datetime.strptime(
                            row[int(request_paid_date)], format
                        ).date()
                    except ValueError:
                        paid_date = None
            else:
                paid_date = None
            if request_term_date != None and row[int(request_term_date)] != None:
                try:
                    format = "%m/%d/%Y"
                    term_date = datetime.strptime(
                        row[int(request_term_date)], format
                    ).date()
                except ValueError:
                    try:
                        format = "%m/%d/%y"
                        term_date = datetime.strptime(
                            row[int(request_term_date)], format
                        ).date()
                    except ValueError:
                        term_date = None
            else:
                term_date = None
            agent_name = (
                ("" if agent_firstname == None else row[int(agent_firstname)])
                + ("" if agent_firstname == None and agent_lastname == None else " ")
                + ("" if agent_lastname == None else row[int(agent_lastname)])
            )
            if policy_number == None:
                suscriberid = ""
            else:
                suscriberid = row[int(policy_number)]
                if insured == 1 or insured == '1':
                    suscriberid = suscriberid[3:]

            bob = BobGlobal(
                id_insured=insured,
                agent_name="" if agent_name == None else agent_name,
                agent_npn="" if row[int(
                    agent_npn)] == None else row[int(
                        agent_npn)],
                client_name="" if client_name == None else row[int(
                    client_name)],
                client_lastname=""
                if client_lastname == None
                else row[int(client_lastname)],
                suscriberid=suscriberid,
                num_members=0
                if num_members == None
                or row[int(num_members)] == ""
                or row[int(num_members)] == "N/A"
                else row[int(num_members)],
                pol_hold_state="" if state == None else row[int(state)],
                eleg_commision="" if elegible == None else row[int(elegible)],
                phone_number="" if client_phone == None else row[int(
                    client_phone)],
                policy_status="" if policy_status == None else row[int(
                    policy_status)],
                # Dates
                date_birth="1000-01-01" if client_dob == None else client_dob,
                pol_rec_date="1000-01-01"
                if policy_rec_date == None
                else policy_rec_date,
                effective_date="1000-01-01"
                if effective_date == None
                else effective_date,
                paid_date="1000-01-01" if paid_date == None else paid_date,
                term_date="1000-01-01" if term_date == None else term_date,
            )
            bobs.append(bob)
            if len(bobs) >= 5000:
                BobGlobal.objects.bulk_create(bobs)
                bobs = []
        if bobs:
            BobGlobal.objects.bulk_create(bobs)
        return Response(status=status.HTTP_200_OK)


class ApplicationDashboardSummary(APIView, AgencyManagement, DashboardCommons):
    def get(self, request: HttpRequest):
        user_id = self.dash_get_alternative_user(request)
        pending = self.get_related_applications(user_id, True).count()
        today = date.today()
        completed = (
            self.get_related_clients(user_id, True).filter(
                fechainsert=today).count()
        )
        total = pending + completed
        response = {
            "pending": {
                "value": pending,
                "percent": floor(pending / total * 100) if total != 0 else 0,
            },
            "completed": {
                "value": completed,
                "percent": ceil(completed / total * 100) if total != 0 else 0,
            },
        }
        return Response(response)


class ResetPasswords(APIView, AgencyManagement):
    def post(self, request: HttpRequest):
        user: CustomUser = request.user
        if not user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        target = request.data.get("target")
        if not (target in ["agent", "assistant"]):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        default_pass = "pass1234"
        password = request.data.get("password")
        if not password:
            password = default_pass
        if target == "agent":
            targets = Agent.objects.all().only("email")
        else:
            targets = Assistant.objects.all().only("email")
        users = CustomUser.objects.filter(
            email__in=self.queryset_to_list(targets, "email")
        )
        for u in users:
            u.set_password(password)
            u.save()

        return Response(status=status.HTTP_200_OK)


class DataForPendingDocumentsReport(APIView, AgencyManagement):
    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        agents = (
            self.get_related_agents(user.pk, True)
            .order_by("agent_name", "agent_lastname")
            .values("agent_name", "agent_lastname", "id")
        )
        doc_types = TypePendingdoc.objects.all().order_by("names").values()
        for a in agents:
            a["fullname"] = f"{a['agent_name']} {a['agent_lastname']}"

        return Response(
            {"agents": agents, "doc_types": doc_types}, status=status.HTTP_200_OK
        )


class FilterSearch(APIView, LimitOffsetPagination):
    def get(self, request):
        search = request.GET.get("search")
        model = request.GET.get("model")
        if checkFilterSearchPermissions(request, model) == False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = None
        if model == "user":
            queryset = CustomUser.objects.filter(first_name__icontains=search)
            queryset |= CustomUser.objects.filter(last_name__icontains=search)
            queryset |= CustomUser.objects.filter(email__icontains=search)
            queryset = queryset.order_by("first_name")
            for user in queryset:
                groups = ""
                user_groups = user.groups.all()
                for group in user_groups:
                    if groups == "":
                        groups = group.name
                    else:
                        groups = groups + "," + group.name
                user.groups_name = groups
            results = self.paginate_queryset(queryset, request, view=self)
            serializer = ListUserSerializer(results, many=True)
        if serializer == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.get_paginated_response(serializer.data)


class GetSupousedPaymentLog(APIView, PaymentCommons):
    def get(self, request: APIViewRequest):
        if not request.user.is_admin:
            raise ForbiddenException("Only admins")
        year = self.check_none(request.query_params.get("year"))
        client = self.check_none(request.query_params.get("client"))
        agent = self.check_none(request.query_params.get("agent"))
        month = self.check_none(request.query_params.get("month"))
        if not (year and client and agent and month):
            raise ValidationException(
                "Some value: year, client, agent or month is missing in the query"
            )
        _, log = self.pay_get_total_agent_payment_for_client(
            year, month, agent, client)

        return Response(log)


class GetAlternativeData(APIView, DashboardCommons):
    def get(self, request):
        current = request.user
        if not current.is_admin:
            raise ForbiddenException()
        user_id = self.dash_get_alternative_user(request)
        users = CustomUser.objects.filter(id=user_id)
        role = "User"
        if not users.exists():
            return Response({"user": None, "role": None})
        user = users.get()
        if self.current_is("assistant", user_id):
            role = "Assistant"
        elif self.current_is("agent", user_id):
            role = "Agent"
        elif self.current_is("agency_admin", user_id):
            role = "Agency Admin"
        elif self.current_is("admin", user_id):
            role = "Admin"

        return Response({"user": f"{user.get_full_name()}", "role": role})


class ProtectedMedia(APIView):
    def decode_recursively(self, path):
        decoded_path = unquote(path)

        # Check if further decoding is possible
        if decoded_path != path:
            # Continue decoding recursively
            return self.decode_recursively(decoded_path)
        else:
            # Return the final decoded path
            return decoded_path

    def get(self, request, path):
        if request.user.is_authenticated:
            return serve(request, self.decode_recursively(path), document_root=settings.MEDIA_ROOT)
        else:
            return HttpResponseForbidden("You do not have permission to access this resource.")


class DeleteAgentGlobalExcel(APIView):
    permission_classes = [HasImportAgentExcelPermission]

    def post(self, request):
        AgentGlobalAppointments.objects.all().delete()
        AgentGlobalLicenses.objects.all().delete()
        AgentGlobalCE.objects.all().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ImportAgentGlobalExcel(APIView):
    permission_classes = [HasImportAgentExcelPermission]

    def __aux_get_value(
        self, row, pos, default=0, integer=False, floated=False
    ):
        try:
            value = str(row[pos])
            value = value.replace('"', '').replace('=', '')
            if floated:
                value = float(value)
            elif integer:
                value = int(value)
        except:
            value = default
        return value

    def importLicenses(self, reader):
        first_check = 1
        agent_licenses = []
        with transaction.atomic():
            for pos, row in enumerate(reader):
                if first_check:
                    first_check = 0
                    continue
                npn = self.__aux_get_value(row, 5, None)
                license_type = self.__aux_get_value(row, 8, "")
                license_issue_date = self.__aux_get_value(row, 10, "")
                license_code = self.__aux_get_value(row, 7, "")
                license_active_or_not = self.__aux_get_value(row, 9, "")

                if not npn:
                    continue

                data = AgentGlobalLicenses(
                    npn=npn,
                    license_type=license_type,
                    license_issue_date=license_issue_date,
                    license_code=license_code,
                    license_active_or_not=True if license_active_or_not == 'VALID' else False,

                )

                agent_licenses.append(data)
                if len(agent_licenses) > 5000:
                    AgentGlobalLicenses.objects.bulk_create(agent_licenses)
                    agent_licenses.clear()

            if agent_licenses:
                AgentGlobalLicenses.objects.bulk_create(agent_licenses)

    def importCE(self, reader):
        first_check = 1
        agent_global_ce = []
        with transaction.atomic():
            for pos, row in enumerate(reader):
                if first_check:
                    first_check = 0
                    continue
                npn = self.__aux_get_value(row, 5, None)
                code = self.__aux_get_value(row, 7, None)
                ce_due_date = self.__aux_get_value(row, 10, "")
                ce_req_hours = self.__aux_get_value(row, 13, "")
                ce_completed_hours = self.__aux_get_value(row, 14, "")

                if not npn:
                    continue
                if code != '0240' and code != '0215':
                    continue

                data = AgentGlobalCE(
                    npn=npn,
                    ce_due_date=ce_due_date,
                    ce_req_hours=ce_req_hours,
                    ce_completed_hours=ce_completed_hours
                )
                agent_global_ce.append(data)
                if len(agent_global_ce) > 5000:
                    AgentGlobalCE.objects.bulk_create(agent_global_ce)
                    agent_global_ce.clear()

            if agent_global_ce:
                AgentGlobalCE.objects.bulk_create(agent_global_ce)

    def importAppointments(self, reader):
        first_check = 1
        agent_appointments = []
        with transaction.atomic():
            for pos, row in enumerate(reader):
                if first_check:
                    first_check = 0
                    continue
                license_num = self.__aux_get_value(row, 0, "")
                npn = self.__aux_get_value(row, 5, None)
                agent_name = self.__aux_get_value(row, 1, "")
                business_address = self.__aux_get_value(row, 16, "")+" , " + self.__aux_get_value(row, 17, "")+" , " + self.__aux_get_value(
                    row, 18, "")+" , " + self.__aux_get_value(row, 19, "")+" , " + self.__aux_get_value(row, 20, "")
                county = self.__aux_get_value(row, 21, "")
                mailing_address = self.__aux_get_value(row, 22, "")+" , " + self.__aux_get_value(row, 23, "")+" , " + self.__aux_get_value(
                    row, 24, "")+" , " + self.__aux_get_value(row, 25, "")+" , " + self.__aux_get_value(row, 26, "")
                email = self.__aux_get_value(row, 14, "")
                phone = self.__aux_get_value(row, 15, "")

                company_name = self.__aux_get_value(row, 8, "")
                app_code = self.__aux_get_value(row, 9, "")
                app_type = self.__aux_get_value(row, 10, "")
                active_or_not = self.__aux_get_value(row, 11, "")
                issue_date = self.__aux_get_value(row, 12, "")
                exp_date = self.__aux_get_value(row, 13, "")

                if not npn:
                    continue

                data = AgentGlobalAppointments(
                    npn=npn,
                    license_num=license_num,
                    agent_name=agent_name,
                    business_address=business_address,
                    mailing_address=mailing_address,
                    county=county,
                    email=email,
                    phone=phone,
                    company_name=company_name,
                    issue_date=issue_date,
                    exp_date=exp_date,
                    app_type=app_type,
                    app_code=app_code,
                    active_or_not=True if active_or_not == 'ACTIVE' else False
                )

                agent_appointments.append(data)
                if len(agent_appointments) > 5000:
                    AgentGlobalAppointments.objects.bulk_create(
                        agent_appointments)
                    agent_appointments.clear()

            if agent_appointments:
                AgentGlobalAppointments.objects.bulk_create(agent_appointments)

    def post(self, request):
        file = request.data.get("file")
        decoded_file = file.read().decode()
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        type = request.data.get('type')
        if type == 'Appointments':
            self.importAppointments(reader)
        elif type == 'Licenses':
            self.importLicenses(reader)
        elif type == 'CES':
            self.importCE(reader)

        return Response(status=status.HTTP_201_CREATED)
