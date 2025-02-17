from rest_framework import serializers
from .models import *
from django.utils.translation import gettext_lazy as _


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Agency


class AgentTaxDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentTaxDocument


# class SelfManagedAgencyPaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = "__all__"
#         model = SelfManagedAgencyPayment


class PreLetterLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PreLetterLog


class AgentStateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentState


class ClientSerializerLite(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        fields = ("id", "full_name")
        model = Client


class ClientMedicaidSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClientMedicaid


class IncomeLetterLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = IncomeLetterLog


class SecondaryOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SecondaryOverride


class AgencyRepaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgencyRepayments


class AssistantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Assistant


class OverrideSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Override


class GetClientConsentLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClientConsentLog


class AgentPaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentPayments


class RepaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Repayments


class FuturePaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = FuturePayments


class ClaimHistorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClaimHistory


class AgentPortalSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentPortal


class ListClientSerializer(serializers.ModelSerializer):
    status_bob = serializers.CharField()

    class Meta:
        fields = (
            "pending",
            "id",
            "names",
            "lastname",
            "suscriberid",
            "aplication_date",
            "id_insured",
            "date_birth",
            "id_agent",
            "id_state",
            "family_menber",
            "status_bob",
            "renewed",
        )
        model = Client


class ListAgentSerializer(serializers.ModelSerializer):
    client_count = serializers.IntegerField()

    class Meta:
        fields = "__all__"
        model = Agent


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = DocumentType


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Event


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Groups


class HealthPlanSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = HealthPlan


class InsuredSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Insured


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Language


class PlanNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PlanName


class PolizaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Poliza


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Product


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Problem


class SendsmsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Sendsms


class SocServiceRefeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SocServiceRefe


class OriginalPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = OriginalPayment


class PaymentExcelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PaymentExcel


class SpecialElectionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SpecialElection


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = State


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Status


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Type


class TypePendingdocSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = TypePendingdoc


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Video


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = City


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = County


class CommAgentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = CommAgent


class CommAgencySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = CommAgency


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Agent


class AgentGlobalAppointmentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentGlobalAppointments


class AgentGlobalLicensesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentGlobalLicenses


class AgentGlobalAppointmentsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = AgentGlobalAppointments


class AgentGlobalLicensesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = AgentGlobalLicenses


class AgentGlobalCESerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = AgentGlobalCE


class SecondaryAgentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'agent_name', 'agent_lastname',
                  'secondary_agent', 'npn', 'telephone', 'exclusive_secondary_agent']
        model = Agent


class SubscriberIdTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SubscriberIdTemplate


class AgentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentDocument


class ClientConsentLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClientConsentLog


class SubassistantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Subassistant


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Client


class ApplicationSerializer(serializers.ModelSerializer):
    problems = serializers.CharField()

    class Meta:
        fields = "__all__"
        model = Client


class MedicareSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Medicare


class ClientMedicareSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClientMedicare


class ProspectManagerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ProspectManager


class UpdocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Updocument


class BobGlobalSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = BobGlobal


class AgentInsuredSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentInsured


class AgentLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentLanguage


class AgentProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentProduct


class AssitStateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AssitState


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Claim


class ClientDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClientDocument


class ClientParientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ClientParient


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = History


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Log


class MedicareSocialSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = MedicareSocial


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Menu


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Payments


class USZipsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = USZips


class PaymentsGlobalSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PaymentsGlobal


class PaymentsGlobalTmpSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PaymentsGlobalTmp


class PaymentsagencySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Paymentsagency


class PaymentsasistentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Paymentsasistent


class PendingDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PendingDocuments


class ApplicationProblemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ApplicationProblem


class PDFNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PDFNotice


class PermisosSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Permisos


class ProstManegerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ProstManeger


class RegistreAsisSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = RegistreAsis


class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Registro


class Table5Serializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Table5


class AssitInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AssitInsurance


class ExtraFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ExtraFields


class AgentOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "agent_name", "agent_lastname")
        model = Agent


class InsuredOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = Insured


class AgencyOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "agency_name")
        model = Agency


class StateOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = State


class EventOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = Event


class StatusOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = Status


class PolizaOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = Poliza


class LanguageOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = Language


class CityOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names")
        model = City


class AssistantOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "assistant_name", "assistant_lastname")
        model = Assistant


class PaymentAgentSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))

    class Meta:
        fields = (
            "agent_name",
            "id_agent",
            "fecha",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class JulDecSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class JulDecClientSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Clien Name"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class JanJunSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))

    class Meta:
        fields = (
            "agent_name",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
        )


class JanJunClientSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Clien Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
        )


class PaymentGlobalAgentSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class AgentPaymentsDetailsByInsuranceSerializer(serializers.Serializer):
    insured_name = serializers.CharField(label=_("Insurance"))
    commission = serializers.CharField(label=_("Commission"))

    class Meta:
        fields = (
            "insured_name",
            "commission",
        )


class PaymentGlobalClientSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Client Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = AgentPayments


class ExportPaymentAgentMonthSerializer(serializers.ModelSerializer):
    policies = serializers.CharField(label=_("Policies"))
    nosub = serializers.CharField(label=_("No Sub."))
    no_elegible = serializers.CharField(label=_("No Elig."))
    cancel = serializers.CharField(label=_("Cancel"))
    payment = serializers.CharField(label=_("Payment"))
    no_payment = serializers.CharField(label=_("No Payment"))
    agent_name = serializers.CharField(label=_("Agent Name"))
    members = serializers.CharField(label=_("Num Members"))
    amount = serializers.SerializerMethodField(label=_("Month Amount"))

    def get_amount(self, obj):
        month = self.context.get('month')
        if month == 'january':
            return obj.get('january')
        elif month == 'february':
            return obj.get('february')
        elif month == 'march':
            return obj.get('march')
        elif month == 'april':
            return obj.get('april')
        elif month == 'may':
            return obj.get('may')
        elif month == 'june':
            return obj.get('june')
        elif month == 'july':
            return obj.get('july')
        elif month == 'august':
            return obj.get('august')
        elif month == 'september':
            return obj.get('september')
        elif month == 'october':
            return obj.get('october')
        elif month == 'november':
            return obj.get('november')
        elif month == 'dicember':
            return obj.get('dicember')

    class Meta:
        fields = (
            "agent_name",
            "policies",
            "nosub",
            "no_elegible",
            "cancel",
            "payment",
            "no_payment",
            "members",
            "amount",
        )
        model = Payments


class ExportPaymentGlobalAgentMonthSerializer(serializers.ModelSerializer):
    policies = serializers.CharField(label=_("Policies"))
    nosub = serializers.CharField(label=_("No Sub."))
    no_elegible = serializers.CharField(label=_("No Elig."))
    cancel = serializers.CharField(label=_("Cancel"))
    payment = serializers.CharField(label=_("Payment"))
    no_payment = serializers.CharField(label=_("No Payment"))
    agent_name = serializers.CharField(label=_("Agent Name"))
    paid_members = serializers.CharField(label=_("Num Members"))
    month = serializers.SerializerMethodField(label=_("Month Amount"))

    def get_month(self, obj):
        keys = list(obj.keys())
        return obj.get(keys[-1])

    class Meta:
        fields = (
            "agent_name",
            "policies",
            "nosub",
            "no_elegible",
            "cancel",
            "payment",
            "no_payment",
            "paid_members",
            "month",
        )
        model = Payments


class ExportPaymentGlobalClientMonthSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Client Name"))
    telephone = serializers.CharField(label=_("Telephone"))
    effective_date = serializers.DateField(label=_("Effective Date"))
    paid_date = serializers.DateField(label=_("Paid Date"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    cancel = serializers.CharField(label=_("Cancel"))
    members_number = serializers.CharField(label=_("Num Members"))
    month = serializers.SerializerMethodField(label=_("Month Amount"))

    def get_month(self, obj):
        keys = list(obj.keys())
        return obj.get(keys[-1])

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "telephone",
            "effective_date",
            "paid_date",
            "cancel",
            "suscriberid",
            "members_number",
            "month",
        )
        model = Payments


class PaymentClientSerializerExtended(serializers.ModelSerializer):
    agent_name = serializers.CharField()
    client_name = serializers.CharField()
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "id_client",
            "id_agent",
            "fecha",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class PaymentClientSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField()
    client_name = serializers.CharField()
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "id_client",
            # "id_agent",
            "fecha",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class AgentExportExcelSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    license = serializers.CharField(label=_("License"))
    npn = serializers.CharField(label=_("NPN"))
    email = serializers.CharField(label=_("Email"))
    email2 = serializers.CharField(label=_("Email2"))
    phone = serializers.CharField(label=_("Phone"))
    phone2 = serializers.CharField(label=_("Phone2"))
    user_cms = serializers.CharField(label=_("User CMS"))
    password_cms = serializers.CharField(label=_("Password CMS"))
    password_sherpa = serializers.CharField(label=_("Password Sherpa"))
    question1 = serializers.CharField(label=_("Question 1"))
    question2 = serializers.CharField(label=_("Question 2"))
    question3 = serializers.CharField(label=_("Question 3"))
    assistant = serializers.CharField(label=_("Assistant"))

    class Meta:
        fields = (
            "agent_name",
            "license",
            "npn",
            "email",
            "email2",
            "phone",
            "phone2",
            "user_cms",
            "password_cms",
            "password_sherpa",
            "question1",
            "question2",
            "question3",
            "assistant",
        )
        model = Agent


class PaymentGlobalSerializer(serializers.ModelSerializer):
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    client_name = serializers.CharField(label=_("Client Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))
    id = serializers.IntegerField(label=_("AgentID"))
    id_insured = serializers.IntegerField(label=_("Insurance"))
    agent_name = serializers.SerializerMethodField(label=_("Agent Name"))

    def get_agent_name(self, obj):
        agent_name = obj.get('agent_name') if obj.get(
            'agent_name') is not None else ""
        agent_lastname = obj.get('agent_lastname') if obj.get(
            'agent_lastname') is not None else ""
        return agent_name + " " + agent_lastname

    class Meta:
        fields = (
            "client_name",
            "suscriberid",
            "fecha",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            "agent_name",
            "id",
            "id_insured",
        )
        model = Payments


class PaymentClientMonthSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Client Name"))
    telephone = serializers.CharField(label=_("Telephone"))
    effective_date = serializers.DateField(label=_("Effective Date"))
    paid_date = serializers.DateField(label=_("Paid Date"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    cancel = serializers.CharField(label=_("Cancel"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))
    # indx_payment = serializers.IntegerField(label=_("Indx"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "id_client",
            "fecha",
            "january",
            "february",
            "march",
            "april",
            "telephone",
            "effective_date",
            "paid_date",
            "suscriberid",
            "cancel",
            # "id_agent",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            # "indx_payment",
        )
        model = Payments


class ExportPaymentClientMonthSerializerExtended(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Client Name"))
    telephone = serializers.CharField(label=_("Telephone"))
    effective_date = serializers.DateField(label=_("Effective Date"))
    paid_date = serializers.DateField(label=_("Paid Date"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    cancel = serializers.CharField(label=_("Cancel"))
    fecha = serializers.FloatField(label=_("Year"))
    indx_payment = serializers.IntegerField(label=_("Indx"))
    members = serializers.CharField(label=_("Num Members"))
    amount = serializers.SerializerMethodField(label=_("Month Amount"))

    def get_amount(self, obj):
        month = self.context.get('month')
        if month == 'january':
            return obj.get('january')
        elif month == 'february':
            return obj.get('february')
        elif month == 'march':
            return obj.get('march')
        elif month == 'april':
            return obj.get('april')
        elif month == 'may':
            return obj.get('may')
        elif month == 'june':
            return obj.get('june')
        elif month == 'july':
            return obj.get('july')
        elif month == 'august':
            return obj.get('august')
        elif month == 'september':
            return obj.get('september')
        elif month == 'october':
            return obj.get('october')
        elif month == 'november':
            return obj.get('november')
        elif month == 'dicember':
            return obj.get('dicember')

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "id_client",
            "fecha",
            "telephone",
            "effective_date",
            "paid_date",
            "suscriberid",
            "cancel",
            "indx_payment",
            "members",
            "amount",
        )
        model = Payments


class PaymentClientMonthSerializerExtended(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    client_name = serializers.CharField(label=_("Client Name"))
    telephone = serializers.CharField(label=_("Telephone"))
    effective_date = serializers.DateField(label=_("Effective Date"))
    paid_date = serializers.DateField(label=_("Paid Date"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    cancel = serializers.CharField(label=_("Cancel"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))
    indx_payment = serializers.IntegerField(label=_("Indx"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "id_client",
            "fecha",
            "telephone",
            "effective_date",
            "paid_date",
            "suscriberid",
            "cancel",
            "january",
            "february",
            "march",
            "april",
            "id_agent",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            "indx_payment",
        )
        model = Payments


class PaymentAgentMonthSerializer(serializers.ModelSerializer):
    policies = serializers.CharField(label=_("Policies"))
    nosub = serializers.CharField(label=_("No Sub."))
    no_elegible = serializers.CharField(label=_("No Elig."))
    cancel = serializers.CharField(label=_("Cancel"))
    payment = serializers.CharField(label=_("Payment"))
    no_payment = serializers.CharField(label=_("No Payment"))
    agent_name = serializers.CharField(label=_("Agent Name"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))
    fecha = serializers.FloatField(label=_("Year"))

    class Meta:
        fields = (
            "agent_name",
            "fecha",
            "id_agent",
            "policies",
            "nosub",
            "no_elegible",
            "cancel",
            "payment",
            "no_payment",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
        )
        model = Payments


class PaymentsAgencySerializer(serializers.ModelSerializer):
    client_name = serializers.CharField()
    agent_name = serializers.CharField()
    insured_name = serializers.CharField()
    agency_name = serializers.CharField()

    class Meta:
        fields = "__all__"
        model = PaymentsGlobalAgency


class PaymentsAgencyExcelSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(label=_("Client Name"))
    agent_name = serializers.CharField(label=_("Agent Name"))
    agency_name = serializers.CharField(label=_("Agency"))
    insured_name = serializers.CharField(label=_("Insurance"))
    month = serializers.SerializerMethodField(label=_("Month"))
    members_number = serializers.IntegerField(label=_("Members"))
    total_commission = serializers.FloatField(label=_("Commission"))

    def get_month(self, obj):
        return obj.month.capitalize()
        # return obj.get("month").capitalize()

    class Meta:
        fields = (
            "client_name",
            "agent_name",
            "agency_name",
            "insured_name",
            "month",
            "members_number",
            "total_commission",
        )
        model = PaymentsGlobalAgency


class OverrideExcelSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(label=_("Client Name"))
    agent_name = serializers.CharField(label=_("Agent Name"))
    insured_name = serializers.CharField(label=_("Insurance"))
    members_number = serializers.IntegerField(label=_("Members"))
    commission = serializers.FloatField(label=_("Commission"))

    class Meta:
        fields = (
            "client_name",
            "agent_name",
            "insured_name",
            "members_number",
            "commission",
        )
        model = Override


class UnprocesedPoliciesExcelSerializer(serializers.Serializer):
    client_name = serializers.CharField(label=_("Client Name"))
    agent_name = serializers.CharField(label=_("Agent Name"))
    suscriberid = serializers.CharField(label=_("Subscriber ID"))
    insured = serializers.CharField(label=_("Insurance"))
    members_number = serializers.IntegerField(label=_("Members"))
    info_month = serializers.CharField(label=_("Paid Month"))
    commission = serializers.FloatField(label=_("Commission"))

    class Meta:
        fields = (
            "client_name",
            "agent_name",
            "insured",
            "suscriberid",
            "members_number",
            "info_month",
            "commission",
        )


class UnAssignedPaymentsExcelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = UnAssignedPayments


class AgentsByCommissionGroupExcelSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    npn = serializers.CharField(label=_("NPN"))
    telephone = serializers.CharField(label=_("Telephone"))
    email = serializers.CharField(label=_("Email"))

    class Meta:
        fields = (
            "agent_name",
            "telephone",
            "npn",
            "email",
        )


class PaymentsGlobalAgencySerializer(serializers.ModelSerializer):
    insured__names = serializers.CharField(label=_("Insurance"))
    agency__agency_name = serializers.CharField(label=_("Agency"))
    commission = serializers.FloatField(label=_("Commission"))
    members = serializers.IntegerField(label=_("Members"))
    month = serializers.SerializerMethodField(label=_("Month"))

    def get_month(self, obj):
        return obj.get("month").capitalize()
        # return obj.month.capitalize()

    class Meta:
        fields = (
            "id",
            "agency__agency_name",
            "insured__names",
            "month",
            "insured_id",
            "agency_id",
            "members",
            "commission",
            "year",
        )
        model = PaymentsGlobalAgency


class PaymentsGlobalAgencyDetailsSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agency"))
    client_name = serializers.CharField(label=_("Client"))
    insured = serializers.CharField(label=_("Insurance"))
    npn = serializers.CharField(label=_("NPN"))
    family_menber = serializers.IntegerField(label=_("Members"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    aplication_date = serializers.CharField(label=_("Application Date"))
    month = serializers.SerializerMethodField(label=_("Month"))
    comission = serializers.FloatField(label=_("Commission"))

    def get_month(self, obj):
        return obj.get("month").capitalize()
        # return obj.month.capitalize()

    class Meta:
        fields = (
            "id",
            "agent_name",
            "client_name",
            "insured",
            "npn",
            "client_name",
            "family_menber",
            "suscriberid",
            "aplication_date",
            "month",
            "comission",
        )
        model = PaymentsGlobalAgency


class OriginalPaymentGlobalSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            "agent",
        )
        model = OriginalPayment


class OriginalPaymentGlobalMonthSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    members = serializers.CharField(label=_("Num Members"))
    amount = serializers.FloatField(label=_("Month Amount"))

    class Meta:
        fields = (
            "agent_name",
            "members",
            "amount",
            "agent"
        )
        model = OriginalPayment


class OriginalPaymentClientSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "suscriber_id",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            "agent",
        )
        model = OriginalPayment


class OriginalPaymentClientMonthSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    members = serializers.CharField(label=_("Num Members"))
    amount = serializers.FloatField(label=_("Month Amount"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "suscriber_id",
            "members",
            "amount",
            "agent",
            "info_month"
        )
        model = OriginalPayment


class OriginalPaymentDiscrepanciesSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    members = serializers.CharField(label=_("Num Members"))
    policy_status = serializers.CharField(label=_("Policy Status"))
    amount = serializers.FloatField(label=_("Month Amount"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "suscriber_id",
            "members",
            "amount",
            "policy_status",
            "agent"
        )
        model = OriginalPayment


class OriginalPaymentDifferencesSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    system_payment = serializers.CharField(label=_("System Payment"))
    original_payment_commission = serializers.FloatField(
        label=_("Original Payment"))
    greatest = serializers.CharField(label=_("Commission"))

    class Meta:
        fields = (
            "agent_name",
            "system_payment",
            "original_payment_commission",
            "greatest"
        )
        model = OriginalPayment


class OriginalPaymentGlobalSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("December"))

    class Meta:
        fields = (
            "agent_name",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            "agent",
        )
        model = OriginalPayment


class OriginalPaymentGlobalMonthSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=_("Agent"))
    members = serializers.CharField(label=_("Num Members"))
    amount = serializers.FloatField(label=_("Month Amount"))

    class Meta:
        fields = (
            "agent_name",
            "members",
            "amount",
            "agent"
        )
        model = OriginalPayment


class AgentCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AgentCommission


class CommissionsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = CommissionsGroup


class GroupCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = GroupCommission


class CommissionsGroupSerializerExtended(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "names", "commissions")
        model = CommissionsGroup

    commissions = GroupCommissionSerializer(many=True)


class ClientExportSerializer(serializers.ModelSerializer):
    client_names = serializers.CharField(label=_("Client Name"))
    telephone = serializers.CharField(label=_("Telephone"))
    suscriberId = serializers.CharField(label=_("Suscriber/Member Id"))
    irthdate = serializers.CharField(label=_("Birthdate"))
    nsurance = serializers.CharField(label=_("Insurance"))
    applicationId = serializers.CharField(label=_("Application Id"))
    state = serializers.CharField(label=_("State"))
    agent_names = serializers.CharField(label=_("Agent Name"))
    member_n = serializers.IntegerField(label=_("# of Insured"))
    agent2 = serializers.CharField(label=_("Agent 2"))
    assistant_names = serializers.CharField(label=_("Assistant"))
    spouse = serializers.CharField(label=_("Spouse Name"))
    princome = serializers.CharField(label=_("Principal Income"))
    conincome = serializers.CharField(label=_("Spouse Income"))
    email = serializers.CharField(label=_("Email"))
    addreess = serializers.CharField(label=_("Address"))
    totalincome = serializers.SerializerMethodField(label=_("Total Income"))

    def get_totalincome(self, obj):
        try:
            princome = float(obj.get("princome"))
        except:
            princome = 0
        try:
            conincome = float(obj.get("conincome"))
        except:
            conincome = 0
        return princome+conincome

    class Meta:
        fields = (
            "client_names",
            "telephone",
            "suscriberId",
            "irthdate",
            "nsurance",
            "applicationId",
            "state",
            "spouse",
            "agent_names",
            "member_n",
            "agent2",
            "assistant_names",
            "princome",
            "conincome",
            "totalincome",
            "email",
            "addreess"
        )
        model = Client


class EmptyPaymentLogEntrySerilizer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = EmptyPaymentLogEntry


class ClientLogSerilizer(serializers.ModelSerializer):
    user_name = serializers.CharField()
    user_email = serializers.CharField()
    client_name = serializers.CharField()
    added_on = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_added_on(self, obj):
        return obj.added_on.strftime("%m/%d/%Y - %H:%M:%S")

    def get_type(self, obj):
        return obj.type.capitalize()

    class Meta:
        fields = (
            "id",
            "added_on",
            "type",
            "user",
            "client",
            "user_name",
            "user_email",
            "client_name",
            "description"
        )
        model = ClientLog


class ApiLogSerilizer(serializers.ModelSerializer):
    user_name = serializers.CharField()
    log_id = serializers.IntegerField()
    added_on = serializers.SerializerMethodField()
    api = serializers.SerializerMethodField()

    def get_added_on(self, obj):
        return obj.added_on.strftime("%m/%d/%Y - %H:%M:%S")

    def get_api(self, obj):
        endpoint = obj.api.removeprefix("http://").removeprefix("https://")
        indx = endpoint.find("/")
        return endpoint[indx:]

    class Meta:
        fields = (
            "id",
            "log_id",
            "added_on",
            "api",
            "method",
            "client_ip_address",
            "status_code",
            "execution_time",
            "user",
            "user_name",
            "user_email",
            "body",
            "response",
        )
        model = ApiLog


class PaymentsGlobalAssistantExcelSerializer(serializers.Serializer):
    assistant = serializers.CharField(label=_("Assistant"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("Dicember"))


class PaymentAssistantSummaryDetailsExcelSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agency"))
    client_name = serializers.CharField(label=_("Client"))
    insured = serializers.CharField(label=_("Insurance"))
    npn = serializers.CharField(label=_("NPN"))
    family_menber = serializers.IntegerField(label=_("Members"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    aplication_date = serializers.CharField(label=_("Application Date"))
    month = serializers.SerializerMethodField(label=_("Month"))
    comission = serializers.FloatField(label=_("Commission"))

    def get_month(self, obj):
        return obj.get("month").capitalize()
        # return obj.month.capitalize()

    class Meta:
        fields = (
            "id",
            "agent_name",
            "client_name",
            "insured",
            "npn",
            "client_name",
            "family_menber",
            "suscriberid",
            "aplication_date",
            "month",
            "comission",
        )
        model = PaymentsGlobalAgency


class PaymentAgentSummaryDetailsExcelSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agency"))
    client_name = serializers.CharField(label=_("Client"))
    date = serializers.CharField(label=_("Date"))
    effective_date = serializers.CharField(label=_("Application Date"))
    insured_name = serializers.CharField(label=_("Insurance"))
    month = serializers.SerializerMethodField(label=_("Month"))
    npn = serializers.CharField(label=_("NPN"))
    num_member = serializers.IntegerField(label=_("Members"))
    suscriberid = serializers.CharField(label=_("Suscriber ID"))
    type = serializers.CharField(label=_("Type"))
    commission = serializers.FloatField(label=_("Commission"))

    def get_month(self, obj):
        return obj.get("month").capitalize()
        # return obj.month.capitalize()

    class Meta:
        fields = (
            "id",
            "agent_name",
            "client_name",
            "date",
            "effective_date",
            "insured_name",
            "month",
            "npn",
            "num_member",
            "type",
            "commission",
        )
        model = PaymentsGlobalAgency


class PaymentsGlobalAssistantExcelSerializerExtended(serializers.Serializer):
    assistant = serializers.CharField(label=_("Assistant"))
    policies = serializers.IntegerField(label=_("Policies"))
    cancel = serializers.IntegerField(label=_("Cancel"))
    no_elegible = serializers.IntegerField(label=_("No Elegible"))
    nosub = serializers.IntegerField(label=_("No Sub"))
    payment = serializers.IntegerField(label=_("Payment"))
    no_payment = serializers.IntegerField(label=_("No Payment"))
    month = serializers.SerializerMethodField(label=_("Commission"))

    def get_month(self, obj):
        keys = list(obj.keys())
        return obj.get(keys[-1])


class PaymentAssistantPerClientExcelSerializer(serializers.Serializer):
    client = serializers.CharField(label=_("Client"))
    assistant = serializers.CharField(label=_("Assistant"))
    january = serializers.FloatField(label=_("January"))
    february = serializers.FloatField(label=_("February"))
    march = serializers.FloatField(label=_("March"))
    april = serializers.FloatField(label=_("April"))
    may = serializers.FloatField(label=_("May"))
    june = serializers.FloatField(label=_("June"))
    july = serializers.FloatField(label=_("July"))
    august = serializers.FloatField(label=_("August"))
    september = serializers.FloatField(label=_("September"))
    october = serializers.FloatField(label=_("October"))
    november = serializers.FloatField(label=_("November"))
    dicember = serializers.FloatField(label=_("Dicember"))


class AgentsByAgencyExcelSerializer(serializers.Serializer):
    agent_names = serializers.CharField(label=_("Agent Name"))
    license_number = serializers.CharField(label=_("License Number"))
    npn = serializers.CharField(label=_("NPN"))
    telephone = serializers.CharField(label=_("Telephone"))
    email = serializers.CharField(label=_("Email"))
    adreess = serializers.CharField(label=_("Address"))
    date_birth = serializers.CharField(label=_("Birthday"))


class ProductionExcelSerializer(serializers.Serializer):
    selected_field_name = serializers.CharField(label=_("Name"))
    policies = serializers.CharField(label=_("Policies Count"))


class AgencyProductionExcelSerializer(serializers.Serializer):
    agency_name = serializers.CharField(label=_("Agency Name"))
    total_policies = serializers.CharField(label=_("Total Policies"))
    total_members = serializers.CharField(label=_("Total Members"))
    Molina_Policies = serializers.CharField()
    Molina_Members = serializers.CharField()
    Ambetter_Policies = serializers.CharField()
    Ambetter_Members = serializers.CharField()
    FloridaBlue_Policies = serializers.CharField()
    FloridaBlue_Members = serializers.CharField()
    BlueCross_Policies = serializers.CharField()
    BlueCross_Members = serializers.CharField()
    OscarHealthInsurance_Policies = serializers.CharField()
    OscarHealthInsurance_Members = serializers.CharField()
    FloridaBlueDental_Policies = serializers.CharField()
    FloridaBlueDental_Members = serializers.CharField()
    Cigna_Policies = serializers.CharField()
    Cigna_Members = serializers.CharField()
    BrightHealth_Policies = serializers.CharField()
    BrightHealth_Members = serializers.CharField()
    Community_Policies = serializers.CharField()
    Community_Members = serializers.CharField()
    FloridaHealthCare_Policies = serializers.CharField()
    FloridaHealthCare_Members = serializers.CharField()
    AvMed_Policies = serializers.CharField()
    AvMed_Members = serializers.CharField()
    FridayHealth_Policies = serializers.CharField()
    FridayHealth_Members = serializers.CharField()
    Aetna_Policies = serializers.CharField()
    Aetna_Members = serializers.CharField()
    UnitedHealthCare_Policies = serializers.CharField()
    UnitedHealthCare_Members = serializers.CharField()


class AgentProductionExcelSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent Name"))
    total_policies = serializers.CharField(label=_("Total Policies"))
    total_members = serializers.CharField(label=_("Total Members"))
    Molina_Policies = serializers.CharField()
    Molina_Members = serializers.CharField()
    Ambetter_Policies = serializers.CharField()
    Ambetter_Members = serializers.CharField()
    FloridaBlue_Policies = serializers.CharField()
    FloridaBlue_Members = serializers.CharField()
    BlueCross_Policies = serializers.CharField()
    BlueCross_Members = serializers.CharField()
    OscarHealthInsurance_Policies = serializers.CharField()
    OscarHealthInsurance_Members = serializers.CharField()
    FloridaBlueDental_Policies = serializers.CharField()
    FloridaBlueDental_Members = serializers.CharField()
    Cigna_Policies = serializers.CharField()
    Cigna_Members = serializers.CharField()
    BrightHealth_Policies = serializers.CharField()
    BrightHealth_Members = serializers.CharField()
    Community_Policies = serializers.CharField()
    Community_Members = serializers.CharField()
    FloridaHealthCare_Policies = serializers.CharField()
    FloridaHealthCare_Members = serializers.CharField()
    AvMed_Policies = serializers.CharField()
    AvMed_Members = serializers.CharField()
    FridayHealth_Policies = serializers.CharField()
    FridayHealth_Members = serializers.CharField()
    Aetna_Policies = serializers.CharField()
    Aetna_Members = serializers.CharField()
    UnitedHealthCare_Policies = serializers.CharField()
    UnitedHealthCare_Members = serializers.CharField()


class ApplicationProductionExcelSerializer(serializers.Serializer):
    received_apps = serializers.CharField(label=_("Received"))
    worked_apps = serializers.CharField(label=_("Worked"))
    received_apps_mean = serializers.CharField(label=_("Received Mean"))
    worked_apps_mean = serializers.CharField(label=_("Worked Mean"))


class AssistantProductionExcelSerializer(serializers.Serializer):
    assistant_name = serializers.CharField(label=_("Name"))
    received_apps = serializers.CharField(label=_("Received"))
    worked_apps = serializers.CharField(label=_("Worked"))
    received_apps_mean = serializers.CharField(label=_("Received Mean"))
    worked_apps_mean = serializers.CharField(label=_("Worked Mean"))


class PaymentAssistantPerClientExcelSerializerExtended(serializers.Serializer):
    client = serializers.CharField(label=_("Client"))
    assistant = serializers.CharField(label=_("Assistant"))
    year = serializers.CharField(label=_("Year"))
    telephone = serializers.CharField(label=_("Telephone"))
    effective_date = serializers.CharField(label=_("Effective Date"))
    paid_date = serializers.CharField(label=_("Paid Date"))
    cancel = serializers.IntegerField(label=_("Cancel"))
    members_number = serializers.IntegerField(label=_("Members Count"))
    suscriberid = serializers.CharField(label=_("Suscriberid"))
    month = serializers.SerializerMethodField(label=_("Commission"))

    def get_month(self, obj):
        keys = list(obj.keys())
        return obj.get(keys[-1])


class PaymentGlobalAgencyAgentSerializer(serializers.Serializer):
    agency_name = serializers.CharField(label=_("Agency"))
    year = serializers.CharField(label=_("Year"))
    month = serializers.CharField(label=_("Month"))
    members = serializers.IntegerField(label=_("Members"))
    commission = serializers.FloatField(label=_("Commission"))


class ClientByCompaniesSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent"))
    npn = serializers.CharField(label=_("NPN"))
    members = serializers.IntegerField(label=_("Members"))
    policies = serializers.FloatField(label=_("Policies"))
    id = serializers.IntegerField(label=_("ID"))


class ExportExcelRepaymentSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent"))
    client_name = serializers.CharField(label=_("Client"))
    year = serializers.CharField(label=_("Year"))
    info_month = serializers.CharField(label=_("Paid Month"))
    insured_name = serializers.CharField(label=_("Insurance"))
    suscriberid = serializers.CharField(label=_("Subscriber ID"))
    members_number = serializers.CharField(label=_("Members"))
    commission = serializers.FloatField(label=_("Commission"))


class ExportExcelReleseadAgentsSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent"))
    npn = serializers.CharField(label=_("NPN"))
    policies = serializers.CharField(label=_("Policies"))
    members = serializers.CharField(label=_("Members"))
    commission = serializers.FloatField(label=_("Commission"))


class ExportExcelAgencyRepaymentSerializer(serializers.Serializer):
    agency_name = serializers.CharField(label=_("Agency"))
    agent_name = serializers.CharField(label=_("Agent"))
    client_name = serializers.CharField(label=_("Client"))
    year = serializers.CharField(label=_("Year"))
    info_month = serializers.CharField(label=_("Paid Month"))
    insured_name = serializers.CharField(label=_("Insurance"))
    members_number = serializers.CharField(label=_("Members"))
    total_commission = serializers.FloatField(label=_("Commission"))
