from email.mime import application
from rest_framework.permissions import BasePermission
from content.models import Agent, Assistant, Client
from content.business.business import AgencyManagement
from django.conf import settings

# Groups


class AppGroups:
    Admin = "Admin"
    Secretary = "Secretary"
    Safety = "Safety"


SAFE_METHODS = ["GET"]


def isAgent(user):
    return user.groups.filter(name__icontains="Agent").exists()


def isAssistant(user):
    return user.groups.filter(name="Assistant").exists()


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class HasClientPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_client"):
            return True
        if request.method == "POST" and user.has_perm("content.add_client"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_client"):
            return True
        if request.method == "DELETE" and user.has_perm("content.delete_client"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        clients = self.get_related_clients(user.pk, True)
        if clients.filter(id=obj.id):
            return True

        return False


class HasApplicationPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_application"):
            return True
        if request.method == "POST" and user.has_perm("content.add_application"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_application"):
            return True
        if request.method == "DELETE" and user.has_perm("content.delete_application"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        application = self.get_related_applications(user.pk, True)
        if application.filter(id=obj.id):
            return True

        return False


class HasClientMedicaidPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_clientmedicaid"):
            return True
        if request.method == "POST" and user.has_perm("content.add_clientmedicaid"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_clientmedicaid"):
            return True
        if request.method == "DELETE" and user.has_perm("content.delete_clientmedicaid"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin or self.is_simple_user(user.pk):
            return True
        medicaid_clients = self.get_related_medicaid_clients(user.pk, True)
        if medicaid_clients.filter(id=obj.id):
            return True

        return False


class HasUserPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_admin:
            return False
        # if request.method == 'GET' and user.has_perm("content.view_client") :
        #     return True
        # if request.method == 'POST' and user.has_perm("content.add_client") :
        #     return True
        if request.method == "PUT" or request.method == "PATCH":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if obj == user:
            return True
        return False


class HasDependantPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and (
            user.has_perm("content.view_client")
            or user.has_perm("content.view_application")
        ):
            return True
        if request.method == "POST" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        if request.method == "PUT" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        if request.method == "DELETE" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        entries = self.get_related_clients(user.pk, True)
        entries |= self.get_related_applications(user.pk, True)
        if entries.filter(id=obj.id_client).exists():
            return True
        return False


class HasPendindDocumentsPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_client"):
            return True
        if (
            request.method == "POST"
            and user.has_perm("content.add_client")
            or user.has_perm("content.change_client")
        ):
            return True
        if request.method == "PUT" and user.has_perm("content.change_client"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_client"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        entries = self.get_related_clients(user.pk, True)
        entries |= self.get_related_applications(user.pk, True)
        if entries.filter(id=obj.id_client).exists():
            return True
        return False


class HasLanguageByAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if (
            request.method == "POST"
            and user.has_perm("content.add_agent")
            or user.has_perm("content.change_agent")
        ):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agente == agent.id:
                    return True
            return False
        return False


class HasInsurancesByAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if (
            request.method == "POST"
            and user.has_perm("content.add_agent")
            or user.has_perm("content.change_agent")
        ):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agente == agent.id:
                    return True
            return False
        return False


class HasAssistStateByAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if (
            request.method == "POST"
            and user.has_perm("content.add_agent")
            or user.has_perm("content.change_agent")
        ):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agente == agent.id:
                    return True
            return False
        return False


class HasAssistInsuranceByAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if (
            request.method == "POST"
            and user.has_perm("content.add_agent")
            or user.has_perm("content.change_agent")
        ):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agente == agent.id:
                    return True
            return False
        return False


class HasAgentTaxDocsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agenttaxdocument"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agenttaxdocument"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agenttaxdocument"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agenttaxdocument"):
            return True
        if request.method == "DELETE" and user.has_perm("content.delete_agenttaxdocument"):
            return True
        return False


class HasAgentDocsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if (
            request.method == "POST"
            and user.has_perm("content.add_agent")
            or user.has_perm("content.change_agent")
        ):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agent == agent.id:
                    return True
            return False
        return False


class HasClientDocumentPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and (user.has_perm("content.view_clientdocument")):
            return True
        if request.method == "POST" and (user.has_perm("content.add_clientdocument")):
            return True
        if request.method == "PUT" and (user.has_perm("content.change_clientdocument")):
            return True
        if request.method == "DELETE" and (
            user.has_perm("content.delete_clientdocument")
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        entries = self.get_related_clients(user.pk, True)
        entries |= self.get_related_applications(user.pk, True)
        if entries.filter(id=obj.id_client).exists():
            return True
        return False


class HasClientNotesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_client"):
            return True
        if request.method == "POST" and user.has_perm("content.add_client"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_client"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_client"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            client = Client.objects.filter(id=obj.id_client)
            if len(client) == 1:
                client = client.get()
            if client.id_agent == agent.id:
                return True
            else:
                return False
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            client = Client.objects.filter(id=obj.client_id)
            if len(client) == 1:
                client = client.get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if client.id_agent == agent.id:
                    return True
            return False
        return False


class HasClientPendingDocsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_client"):
            return True
        if request.method == "POST" and user.has_perm("content.add_client"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_client"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_client"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            client = Client.objects.filter(id=obj.id_client)
            if len(client) == 1:
                client = client.get()
            if client.id_agent == agent.id:
                return True
            else:
                return False
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            client = Client.objects.filter(id=obj.client_id)
            if len(client) == 1:
                client = client.get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if client.id_agent == agent.id:
                    return True
            return False
        return False


class HasAgentPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        agents = self.get_related_agents(user.pk, True)
        if agents.filter(id=obj.id):
            return True

        return False


class HasAgentDocumentPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        agents = self.get_related_agents(user.pk, True)
        if agents.filter(id=obj.id_agent):
            return True

        return False


class HasAgentInsuredPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agent == agent.id:
                return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agent == agent.id:
                    return True
        return False


class HasAgentPortalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        if request.method == "DELETE" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agent == agent.id:
                return True
        elif isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agent == agent.id:
                    return True
        else:
            if request.method == "PUT" and user.has_perm("content.change_agent"):
                return True
            if request.method == "PATCH" and user.has_perm("content.change_agent"):
                return True
            if request.method == "GET" and user.has_perm("content.view_agent"):
                return True
            if request.method == "DELETE" and user.has_perm("content.change_agent"):
                return True

        return False


class HasAgentLanguagePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agent == agent.id:
                return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agent == agent.id:
                    return True
        return False


class HasAgentStatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agent == agent.id:
                return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agent == agent.id:
                    return True
        return False


class HasAssitInsurancePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agente == agent.id:
                return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agente == agent.id:
                    return True
        return False


class HasAssitStatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agent"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agente == agent.id:
                return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agente == agent.id:
                    return True
        return False


class HasPreLetterLogPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_preletterlog"):
            return True
        if request.method == "POST" and user.has_perm("content.add_preletterlog"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_preletterlog"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_preletterlog"):
            return True
        if request.method == "DELETE" and user.has_perm("content.delete_preletterlog"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if isAgent(user):
            agent = Agent.objects.filter(email=user.email).get()
            if obj.id_agent == agent.id:
                return True
        if isAssistant(user):
            assistant = Assistant.objects.filter(email=user.email).get()
            agents = Agent.objects.filter(id_assistant=assistant.id)
            for agent in agents:
                if obj.id_agent == agent.id:
                    return True
        return False


class HasAgencyPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_agency"):
            return True
        if request.method == "POST" and user.has_perm("content.add_agency"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_agency"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_agency"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        agencies = self.get_related_agencies(user.pk, True)
        if agencies.filter(id=obj.id).exists():
            return True

        return False


class HasAssistantPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_assistant"):
            return True
        if request.method == "POST" and user.has_perm("content.add_assistant"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_assistant"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_assistant"):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        assistants = self.get_related_assistants(user.pk, True)
        if assistants.filter(id=obj.id):
            return True

        return False


class HasDocumentTypePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and (
            user.has_perm("content.view_documenttype")
            or user.has_perm("content.view_client")
            or user.has_perm("content.view_application")
        ):
            return True
        if request.method == "POST" and user.has_perm("content.add_documenttype"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_documenttype"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_documenttype"):
            return True
        return False


class HasEventPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_event"):
            return True
        if request.method == "POST" and user.has_perm("content.add_event"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_event"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_event"):
            return True
        return False


class HasSubscriberIdTemplatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET":
            return True
        if request.method == "POST" and user.has_perm("content.add_subidtemplate"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_subidtemplate"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_subidtemplate"):
            return True
        return False


class HasImportPaymentCSVPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm("content.add_importpaymentcsv"):
            return True
        return False


class HasGenerateOriginalPaymentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm("content.add_generateoriginalpayment"):
            return True
        return False


class HasImportBOBPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm("content.add_importbob"):
            return True
        return False


class HasImportAgentExcelPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm("content.add_agentexcel"):
            return True
        return False


class HasDeletePaymentCSVPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm("content.delete_deletepayment"):
            return True
        return False


class HasExportExcelAgentListPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.export_excel_agent"):
            return True
        return False


class HasExportExcelClientByCompaniesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.export_excel_clientbycompanies"):
            return True
        return False


class HasExportGlobalPaymentPDFPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentinsuredonly"
        ):
            return True
        return False


class HasExportClientPaymentPDFPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentglobalclient"
        ):
            return True
        return False


class HasExportExcelPaymentDiscrepanciesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentdiscrepancies"
        ):
            return True
        return False


class HasExportPDFPaymentDiscrepanciesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentdiscrepancies"
        ):
            return True
        return False


class HasExportPDFClientsByCompaniesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_clientbycompanies"
        ):
            return True
        return False


class HasExportExcelPaymentDifferencesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentdifferences"
        ):
            return True
        return False


class HasExportPDFPaymentDifferencesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentdifferences"
        ):
            return True
        return False


class HasExportExcelPaymentAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentglobalagent"
        ):
            return True
        return False


class HasExportExcelPaymentAgencyAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentglobalagencyagent"
        ):
            return True
        return False


class HasExportExcelPaymentClientOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentclientoriginal"
        ):
            return True
        return False


class HasExportPDFPaymentClientOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentclientoriginal"
        ):
            return True
        return False


class HasExportExcelPaymentDiscrepanciesOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentdiscrepanciesoriginal"
        ):
            return True
        return False


class HasExportPDFPaymentDiscrepanciesOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentdiscrepanciesoriginal"
        ):
            return True
        return False


class HasExportExcelPaymentGlobalOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentglobaloriginal"
        ):
            return True
        return False


class HasExportPDFPaymentGlobalOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentglobaloriginal"
        ):
            return True
        return False


class HasExportExcelPaymentGlobalAgencyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentglobalagency"
        ):
            return True
        return False


class HasExportExcelPaymentAgencyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_generalpayment"
        ):
            return True
        return False


class HasExportExcelPaymentBobPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentinsuredonly"
        ):
            return True
        return False


class HasExportExcelPaymentClientPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentglobalclient"
        ):
            return True
        return False


class HasExportExcelAssistantProductionPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_assistantproduction"
        ):
            return True
        return False


class HasExportAgentPaymentPDFPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentglobalagent"
        ):
            return True
        return False


class HasExportAgencyAgentPaymentPDFPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentglobalagencyagent"
        ):
            return True
        return False


class HasExportPDFPaymentGlobalAgencyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentglobalagency"
        ):
            return True
        return False


class HasExportPDFPaymentAgencyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_generalpayment"
        ):
            return True
        return False


class HasExportPDFPaymentGloabalAssistantPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentglobalassistant"
        ):
            return True
        return False


class HasExportExcelPaymentGloabalAssistantPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentglobalassistant"
        ):
            return True
        return False


class HasExportExcelPaymentAssistantPerClientPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_paymentoverrideassistant"
        ):
            return True
        return False


class HasExportExcelGenericReportsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_excel_genericreports"
        ):
            return True
        return False


class HasExportPDFPaymentAssistantPerClientPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_paymentoverrideassistant"
        ):
            return True
        return False


class HasExportPDFGenericReportsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.export_pdf_genericreports"
        ):
            return True
        return False


class HasMakeRepaymentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm(
            "content.change_importpaymentcsv"
        ):
            return True
        return False


class HasGroupsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_groups"):
            return True
        if request.method == "POST" and user.has_perm("content.add_groups"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_groups"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_groups"):
            return True
        return False


class HasPaymentAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_paymentglobalagent"):
            return True
        return False


class HasPaymentAgencyAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_paymentglobalagencyagent"):
            return True
        return False


class HasSelfManagedAgencyPaymentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_selfmanagedagencypayment"):
            return True
        return False


class HasPaymentClientPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm(
            "content.view_paymentglobalclient"
        ):
            return True
        return False


class HasPaymentInsuredOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_paymentinsuredonly"):
            return True
        return False


class HasHealthPlanPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_healthplan"):
            return True
        if request.method == "POST" and user.has_perm("content.add_healthplan"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_healthplan"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_healthplan"):
            return True
        return False


class HasInsuredPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_insured"):
            return True
        # if request.method == "GET" and user.is_authenticated:
        #     return True
        if request.method == "POST" and user.has_perm("content.add_insured"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_insured"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_insured"):
            return True
        return False


class HasLanguagePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_language"):
            return True
        if request.method == "POST" and user.has_perm("content.add_language"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_language"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_language"):
            return True
        return False


class HasSecondaryAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_secondaryagent") or user.is_agent:
            return True
        if request.method == "PATCH" and user.has_perm("content.change_secondaryagent"):
            return True
        return False


class HasClientConsentLogPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_clientconsentlog") or user.is_agent:
            return True
        return False


class HasIncomeLetterLogPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_incomeletterlog") or user.is_agent:
            return True
        return False


class HasPlanNamePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_planname"):
            return True
        if request.method == "POST" and user.has_perm("content.add_planname"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_planname"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_planname"):
            return True
        return False


class HasPolizaPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_poliza"):
            return True
        if request.method == "POST" and user.has_perm("content.add_poliza"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_poliza"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_poliza"):
            return True
        return False


class HasProductPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_product"):
            return True
        if request.method == "POST" and user.has_perm("content.add_product"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_product"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_product"):
            return True
        return False


class HasProblemPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_problem"):
            return True
        if request.method == "POST" and user.has_perm("content.add_problem"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_problem"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_problem"):
            return True
        return False


class HasSocServiceRefePErmission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_socservicerefe"):
            return True
        if request.method == "POST" and user.has_perm("content.add_socservicerefe"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_socservicerefe"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_socservicerefe"):
            return True
        return False


class HasSpecialElectionPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_specialelection"):
            return True
        if request.method == "POST" and user.has_perm("content.add_specialelection"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_specialelection"):
            return True
        if request.method == "PATCH" and user.has_perm(
            "content.change_specialelection"
        ):
            return True
        return False


class HasStatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_state"):
            return True
        if request.method == "POST" and user.has_perm("content.add_state"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_state"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_state"):
            return True
        return False


class HasStatusPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_status"):
            return True
        if request.method == "POST" and user.has_perm("content.add_status"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_status"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_status"):
            return True
        return False


class HasClaimPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_claim"):
            return True
        if request.method == "POST" and user.has_perm("content.add_claim"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_claim"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_claim"):
            return True
        if request.method == "DELETE" and user.has_perm("content.delete_claim"):
            return True
        return False


class HasTypePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_type"):
            return True
        if request.method == "POST" and user.has_perm("content.add_type"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_type"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_type"):
            return True
        return False


class HasTypePendingDocPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_typependingdoc"):
            return True
        if request.method == "POST" and user.has_perm("content.add_typependingdoc"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_typependingdoc"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_typependingdoc"):
            return True
        return False


class HasVideoPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_video"):
            return True
        if request.method == "POST" and user.has_perm("content.add_video"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_video"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_video"):
            return True
        return False


class HasCityPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_city"):
            return True
        if request.method == "POST" and user.has_perm("content.add_city"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_city"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_city"):
            return True
        return False


class HasSecondaryOverridePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_secondaryoverride"):
            return True
        if request.method == "POST" and user.has_perm("content.add_secondaryoverride"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_secondaryoverride"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_secondaryoverride"):
            return True
        return False


class HasCountyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_county"):
            return True
        if request.method == "POST" and user.has_perm("content.add_county"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_county"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_county"):
            return True
        return False


class HasCommAgentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_commagent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_commagent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_commagent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_commagent"):
            return True
        return False


class HasDataForPaymentCharPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if isAgent(user):
            return True
        if isAssistant(user):
            return True
        return False


class HasCommAgencyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_commagency"):
            return True
        if request.method == "POST" and user.has_perm("content.add_commagency"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_commagency"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_commagency"):
            return True
        return False


class HasBobGlobalPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and (
            (
                user.has_perm("content.view_client")
                or user.has_perm("content.view_bobglobal")
            )
        ):
            suscriberid = request.GET.get("suscriberid")
            if suscriberid:
                clients = self.get_related_clients(user.pk, True)
                if clients.filter(suscriberid=suscriberid):
                    return True
                else:
                    return False

            return True
        return False


class HasClientByCompanyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_clientbycompanies")
        return False


class HasRepaymentsReportPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_repaymentsreport")
        return False


class HasAssistantProductionReportPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_assistantproductionreport")
        return False


class HasAgencyRepaymentsReportPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_agencyrepayment")
        return False


class HasPaymentDiscrepancyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentdiscrepancies")
        return False


class HasPaymentGlobalOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentglobaloriginal")
        return False


class HasPaymentClientOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentclientoriginal")
        return False


class HasPaymentDiscrepanciesOriginalPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentdiscrepanciesoriginal")
        return False


class HasPaymentDifferencesPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentdifferences")
        return False


class HasPaymentOverrideAssistantPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentoverrideassistant")
        return False


class HasGenericReportsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_genericreports")
        return False


class HasGeneralPaymentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_generalpayment")
        if request.method == "POST":
            return user.has_perm("content.add_generalpayment")
        return False


class HasOverridePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_override")
        if request.method == "POST":
            return user.has_perm("content.add_override")
        return False


class HasPaymentGlobalAgencyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET":
            return user.has_perm("content.view_paymentglobalagency")
        return False


class HasPaymentAssistantPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "POST" and user.has_perm(
            "content.create_paymentglobalassistant"
        ):
            return True
        if request.method == "GET" and user.has_perm(
            "content.view_paymentglobalassistant"
        ):
            return True
        return False


class HasAgentCommissionPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_commagent"):
            return True
        if request.method == "POST" and user.has_perm("content.add_commagent"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_commagent"):
            return True
        if request.method == "PATCH" and user.has_perm("content.change_commagent"):
            return True
        return False


class HasCommissionGroupPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_commissionsgroup"):
            return True
        if request.method == "POST" and user.has_perm("content.add_commissionsgroup"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_commissionsgroup"):
            return True
        if request.method == "PATCH" and user.has_perm(
            "content.change_commissionsgroup"
        ):
            return True
        return False


class HasGroupCommissionPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_groupcommission"):
            return True
        if request.method == "POST" and user.has_perm("content.add_groupcommission"):
            return True
        if request.method == "PUT" and user.has_perm("content.change_groupcommission"):
            return True
        if request.method == "PATCH" and user.has_perm(
            "content.change_groupcommission"
        ):
            return True
        return False


class HasHistoryPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and (
            user.has_perm("content.view_client")
            or user.has_perm("content.view_application")
        ):
            return True
        if request.method == "POST" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        if request.method == "PUT" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        if request.method == "PATCH" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        if request.method == "DELETE" and (
            user.has_perm("content.change_client")
            or user.has_perm("content.change_application")
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        clients = self.get_related_clients(user.pk, True)
        clients |= self.get_related_applications(user.pk, True)
        if clients.filter(id=obj.id_client):
            return True

        return False


class HasClientYearDetailsPermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        id_client = request.GET.get("client")
        clients = self.get_related_clients(user.pk, True)
        if request.method == "GET" and (
            user.has_perm("content.view_client") and clients.filter(
                pk=id_client)
        ):
            return True
        return False


class HasDetailPaymentInPaymentTablePermission(BasePermission, AgencyManagement):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        id_client = request.GET.get("client")
        clients = self.get_related_clients(user.pk, True)
        if request.method == "GET" and (
            user.has_perm("content.view_client") and clients.filter(
                pk=id_client)
        ):
            return True
        return False


class HasPhoneNumberPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if (
            request.method == "GET" or request.method == "POST"
        ) and user.company_phone_number is not None:
            return True
        return False


class HasTwilioPermission(BasePermission):
    def has_permission(self, request, view):
        remote_addr = request.META["REMOTE_ADDR"]
        if settings.TWILIO_ADDR == "" or remote_addr == settings.TWILIO_ADDR:
            return True
        return False


class HasZeroPaymentLogsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_zero_payments_logs"):
            return True

        return False


class HasClientLogsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_client_logs"):
            return True

        return False


class HasGeneralLogsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_admin:
            return True
        if request.method == "GET" and user.has_perm("content.view_general_logs"):
            return True

        return False


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_agent


class IsAssistant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_assistant


class IsAssistantAndAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_assistant or request.user.is_admin


class IsSubAssistant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_subassistant


def checkFilterSearchPermissions(request, model):
    user = request.user
    if not user.is_authenticated:
        return False
    if user.is_admin:
        return True
    if model == "plan_name":
        if request.method == "GET" and user.has_perm("content.view_planname"):
            return True
    elif model == "product":
        if request.method == "GET" and user.has_perm("content.view_product"):
            return True
    elif model == "user":
        user = request.user
        return False
    elif model == "state":
        if request.method == "GET" and user.has_perm("content.view_state"):
            return True
    elif model == "city":
        if request.method == "GET" and user.has_perm("content.view_city"):
            return True

    elif model == "county":
        if request.method == "GET" and user.has_perm("content.view_county"):
            return True

    elif model == "language":
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
    elif model == "insured":
        if request.method == "GET" and user.has_perm("content.view_insured"):
            return True
    elif model == "health_plan":
        if request.method == "GET" and user.has_perm("content.view_healthplan"):
            return True
    elif model == "special_election":
        if request.method == "GET" and user.has_perm("content.view_specialelection"):
            return True
    elif model == "type":
        if request.method == "GET" and user.has_perm("content.view_type"):
            return True
    elif model == "status":
        if request.method == "GET" and user.has_perm("content.view_status"):
            return True
    elif model == "policy":
        if request.method == "GET" and user.has_perm("content.view_policy"):
            return True
    elif model == "document_type":
        if request.method == "GET" and user.has_perm("content.view_documenttype"):
            return True
    elif model == "event":
        if request.method == "GET" and user.has_perm("content.view_event"):
            return True
    elif model == "agency":
        if request.method == "GET" and user.has_perm("content.view_agency"):
            return True
    elif model == "bob_global":
        if request.method == "GET" and user.has_perm("content.view_bobglobal"):
            return True
    elif model == "groups":
        if request.method == "GET" and user.has_perm("content.view_groups"):
            return True
    elif model == "comm_agent":
        if request.method == "GET" and user.has_perm("content.view_commagent"):
            return True
    elif model == "comm_agency":
        if request.method == "GET" and user.has_perm("content.view_commagency"):
            return True
    elif model == "agent":
        if request.method == "GET" and user.has_perm("content.view_agent"):
            return True
    elif model == "assistant":
        if request.method == "GET" and user.has_perm("content.view_assistant"):
            return True
    elif model == "client":
        if request.method == "GET" and user.has_perm("content.view_client"):
            return True
    elif model == "application":
        if request.method == "GET" and user.has_perm("content.view_application"):
            return True

    return False
