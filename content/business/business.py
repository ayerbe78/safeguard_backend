import logging
from operator import itemgetter
from django.contrib.auth.models import Group
from django.db import connection
from content.business.exceptions.custom_exceptions import (
    BusinessException,
    ForbiddenException,
    ValidationException,
)
from content.models import *
from customauth.models import CustomUser
from django.db.models import Q, F
from django.core.exceptions import FieldError
from rest_framework.pagination import LimitOffsetPagination

from cryptography.fernet import Fernet
import base64
from django.conf import settings
from html.parser import HTMLParser
from django.http import HttpResponse, HttpResponseForbidden, HttpRequest
from functools import wraps
from twilio import twiml
from twilio.request_validator import RequestValidator

import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle, colors
from django.http import FileResponse

from datetime import datetime, date
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Footer',
           alignment=TA_CENTER, fontSize=12, spaceBefore=25))


logger = logging.getLogger("django")


class Common:
    """
    A class containing utility functions for handling data and performing common tasks.
    """

    def format_date(self, date_input):
        if isinstance(date_input, (datetime, date)):
            return date_input.strftime('%m/%d/%Y')
        elif isinstance(date_input, str):
            try:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')
                return date_obj.strftime('%m/%d/%Y')
            except ValueError as e:
                raise ValueError() from e
        else:
            raise TypeError()

    def get_company_numbers_for_mass_sending(self):
        """
            Returns the Twilio numbers asigned to mass sending of sms
        """
        return [
            '7864601597',
            '7864604941',
            '7864601003',
            '7865898584',
            '7864810633',
            '7864810110',
            '7864656202',
            '7864810282',
            '7869334854',
            '7863221657',
            '7864811757',
            '7864103526',
            '7864810239',
            '7862071606',
            '7864810519',
            '7864752624',
            '7867517384',
            '7868828596',
            '7864850539',
            '7864605631',
            '7868829825',
            '7864801318',
            '7867676680',
            '7864601724',
            '7868766699',
            '7862071102',
            '7864604682',
            '7867306462',
            '7864810531',
        ]

    def check_new_payment(self, month=0, year=0):
        """
            Checks if should be used the format of the new payments or the old ones in Safeguard
        """
        month = int(month)
        year = int(year)
        new_payments = False
        if year < 2023:
            new_payments = False
        elif month < 7 and year == 2023:
            new_payments = False
        else:
            new_payments = True
        return new_payments

    def check_none(self, x, y=None):
        """
        Check if a value is None or an empty string, returning an alternative value if it is.

        Args:
            x: The value to check.
            y: The alternative value to return if x is None or an empty string (default is None).

        Returns:
            The original value x if it's not None or an empty string, otherwise the alternative value y.
        """
        return (
            x
            if x
            and str(x).strip() != "0"
            and str(x).strip() != ""
            and str(x).strip() != "false"
            else y
        )

    def map_month(self, month_indx) -> str:
        """
        Convert a month index to its corresponding month name.

        Args:
            month_indx: The month index (1-12).

        Returns:
            The name of the month as a string, or None if the index is not valid.
        """
        try:
            month_indx = int(month_indx)

            if month_indx == 1:
                month = "january"
            elif month_indx == 2:
                month = "february"
            elif month_indx == 3:
                month = "march"
            elif month_indx == 4:
                month = "april"
            elif month_indx == 5:
                month = "may"
            elif month_indx == 6:
                month = "june"
            elif month_indx == 7:
                month = "july"
            elif month_indx == 8:
                month = "august"
            elif month_indx == 9:
                month = "september"
            elif month_indx == 10:
                month = "october"
            elif month_indx == 11:
                month = "november"
            elif month_indx == 12:
                month = "dicember"
            else:
                month = None
        except:
            month = None
        return month

    def inverse_map_month(self, month_name) -> str:
        """
        Convert a month name to its corresponding month index.

        Args:
            month_name: The month name.

        Returns:
            The month index as a string, or None if the month is not valid.
        """
        try:
            if month_name == "january":
                month = "01"
            elif month_name == "february":
                month = "02"
            elif month_name == "march":
                month = "03"
            elif month_name == "april":
                month = "04"
            elif month_name == "may":
                month = "05"
            elif month_name == "june":
                month = "06"
            elif month_name == "july":
                month = "07"
            elif month_name == "august":
                month = "08"
            elif month_name == "september":
                month = "09"
            elif month_name == "october":
                month = "10"
            elif month_name == "november":
                month = "11"
            elif month_name == "dicember":
                month = "12"
            else:
                month = None
        except:
            month = None
        return month

    def check_permission(
        self, user: CustomUser, permission: str, ignore_admin: bool = False
    ):
        """
        Check if a user has the specified permission.

        Args:
            user: The user to check the permission for.
            permission: The permission to check.
            ignore_admin: If True, ignore admin status when checking permission (default is False).

        Raises:
            ForbiddenException: If the user doesn't have the specified permission.
        """
        if ignore_admin:
            if not user.has_perm(permission):
                raise ForbiddenException()
        elif not (user.is_admin or user.has_perm(permission)):
            raise ForbiddenException()

    def get_month_list(self) -> list:
        """
        Get a list of all month names.

        Returns:
            A list of month names as strings.
        """
        return [
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
        ]

    def get_user_by_user_type_id(self, type, type_id):
        """
        Returns the user_id corresponding to the specified type_id

        Args:
            type: The user type to match for (e.g., "agent", "assistant").
            type_id: The ID of the type to match.
        Returns:
            The user_id of the specified type, otherwise None.
        """
        if type == "agent":
            try:
                agent = Agent.objects.get(id=type_id)
                email = agent.email
            except:
                return None
        elif type == "assistant":
            try:
                assistant = Assistant.objects.get(id=type_id)
                email = assistant.email
            except:
                return None
        else:
            return None

        try:
            return CustomUser.objects.get(email=email).pk
        except:
            return None

    def current_is(self, type: str, user_id: int):
        """
        Check if the current user is of the specified type.

        Args:
            type: The user type to check for (e.g., "agent", "assistant", "agency_admin", "admin").
            user_id: The ID of the user to check.

        Returns:
            The user's type primary key if the user is of the specified type, otherwise None.
        """
        try:
            user = CustomUser.objects.get(pk=user_id)
            if not user:
                return None
        except:
            return None
        if type == "agent":
            try:
                agent = Agent.objects.get(email=user.email)
                return agent.pk
            except:
                return None
        elif type == "assistant":
            try:
                assistant = Assistant.objects.get(email=user.email)
                return assistant.pk
            except:
                return None
        elif type == "agency_admin":
            agencies = Agency.objects.filter(admin_id=user_id)

            if not agencies.exists():
                return None

            return user_id
        elif type == "admin":
            try:
                user = CustomUser.objects.get(pk=user_id, is_admin=True)
                return user.pk
            except:
                return None
        else:
            return None

    def apply_order_queryset(self, queryset, request, defaultOrder: str):
        """
        Apply ordering to a queryset based on request parameters.

        Args:
            queryset: The queryset to apply ordering to.
            request: The request containing the order and desc parameters.
            defaultOrder: The default order field to use if none is specified.

        Returns:
            The ordered queryset.
        """
        order = self.check_none(request.query_params.get("order"))
        desc = self.check_none(request.query_params.get("desc"), 0)
        if order:
            try:
                queryset = queryset.order_by(
                    f"{'-'+order if desc else order}", defaultOrder
                )
            except FieldError:
                queryset = queryset.order_by(defaultOrder)
        else:
            queryset = queryset.order_by(defaultOrder)
        return queryset

    def apply_order_sql(self, request, defaultOrder: str):
        """
        Generate an SQL order clause based on request parameters.

        Args:
            request: The request containing the order and desc parameters.
            defaultOrder: The default order field to use if none is specified.

        Returns:
            The generated SQL order clause as a string.
        """
        sql = ""
        default = defaultOrder
        order = self.check_none(request.query_params.get("order"))
        desc = self.check_none(request.query_params.get("desc"))
        if order:
            sql += f" order by {self.sql_curate_query(order)} "
            if desc:
                sql += " desc "
        else:
            sql += f" order by {default} "
        return sql

    def apply_order_dict_list(self, queryset, request, defaultOrder: str):
        """
        Apply ordering to a list of dictionaries based on request parameters.

        Args:
            queryset: The list of dictionaries to apply ordering to.
            request: The request containing the order and desc parameters.
            defaultOrder: The default order field to use if none is specified.

        Returns:
            The ordered list of dictionaries.
        """
        order_default = defaultOrder
        order = self.check_none(request.GET.get("order"), order_default)
        desc = self.check_none(request.GET.get("desc"), False)
        desc = 1 if desc else 0

        def key_func(x):
            return str(x[order]) if x[order] else ""

        try:
            queryset = sorted(queryset, key=key_func, reverse=desc)
        except KeyError:
            order = order_default
            queryset = sorted(queryset, key=key_func, reverse=desc)

        return queryset

    def date_from_text(
        self,
        date_string: str,
        date_format: str = "%m/%d/%Y",
        multiple_formats: list[str] = None,
    ):
        """
        Convert a date string to a date object based on the specified format(s).

        Args:
            date_string: The date string to convert.
            date_format: The format to use when parsing the date (default is "%m/%d/%Y").
            multiple_formats: A list of additional formats to try if the initial format fails (default is None).

        Returns:
            The converted date object, or None if the date string could not be parsed using the specified format(s).
        """
        if not multiple_formats:
            correct_date = self.__aux_date_from_text(date_string, date_format)
        else:
            for f in multiple_formats:
                correct_date = self.__aux_date_from_text(date_string, f)
                if correct_date:
                    break
        return correct_date

    def __aux_date_from_text(self, date_string: str, date_format: str):
        """
        Auxiliary function to try converting a date string to a date object using the specified format.

        Args:
            date_string: The date string to convert.
            date_format: The format to use when parsing the date.

        Returns:
            The converted date object, or None if the date string could not be parsed using the specified format.
        """
        correct_date = None
        try:
            correct_date = datetime.strptime(date_string, date_format).date()
        except:
            try:
                correct_date = datetime.strptime(
                    date_string, date_format.replace("Y", "y")
                ).date()
            except:
                correct_date = None
        return correct_date

    def get_insured_by_id(self, insured_id: int = 0):
        """
            Returns an insurance instance from an ID
        """
        insured = Insured.objects.filter(
            id=int(insured_id if insured_id is not None else 0))
        if insured:
            return insured
        else:
            return None


class AgencyManagement(Common):
    """
    A class that extends the Common class and contains methods to manage and fetch related agents, agencies,
    assistants, clients, and applications.
    """

    def get_related_agents(
        self, user_id: int, include_self: bool = False, only: list = []
    ):
        """
        Get related agents based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            include_self: If True, includes the user's own agent record if they are an agent.
            only: A list of specific fields to fetch for the agents.

        Returns:
            A queryset of related agents.
        """
        user = self.__get_current(user_id)

        if len(only):
            allAgents = Agent.objects.exclude(borrado=1).only(*only)
        else:
            allAgents = Agent.objects.exclude(borrado=1)

        if user.is_admin or self.is_simple_user(user.pk):
            return allAgents

        queryset = Agent.objects.none()
        agencies = self.get_related_agencies(user_id)
        for a in list(agencies):
            queryset |= allAgents.filter(id_agency=a.pk)

        if user.is_agent:
            if include_self:
                agent = allAgents.filter(email=user.email)
                if agent.exists():
                    queryset |= agent

        if user.is_assistant:
            assistant = Assistant.objects.get(email=user.email)
            queryset |= allAgents.filter(id_assistant=assistant.pk)
        return queryset

    def get_related_agencies(self, user_id: int, include_self: bool = False, only: list = []):
        """
        Get related agencies based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            include_self: If True, includes the user's own agency record if they are an agent or assistant.

        Returns:
            A queryset of related agencies.
        """
        user = self.__get_current(user_id)

        if user.is_admin or self.is_simple_user(user.pk):
            return Agency.objects.all()

        admin_agencies = Agency.objects.filter(admin_id=user_id)

        agencies = admin_agencies
        for a in list(admin_agencies):
            agencies |= self.__get_agencies_recursive(a.pk)
        if include_self:
            if user.is_agent:
                agent = Agent.objects.filter(email=user.email)
                if agent.exists():
                    agencies |= Agency.objects.filter(id=agent.get().id_agency)
            if user.is_assistant:
                assistant = Assistant.objects.get(email=user.email)
                agents = list(
                    Agent.objects.filter(
                        id_assistant=assistant.pk).only("id_agency")
                )

                def get_agency(agent: Agent) -> int:
                    return agent.id_agency

                agencies |= Agency.objects.filter(
                    pk__in=list(map(get_agency, agents)))
        if len(only):
            agencies = agencies.only(*only)
        return agencies

    def get_related_assistants(self, user_id, include_self: bool = False):
        """
        Get related assistants based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            include_self: If True, includes the user's own assistant record if they are an assistant.

        Returns:
            A queryset of related assistants.
        """
        user = self.__get_current(user_id)

        if user.is_admin or self.is_simple_user(user.pk):
            return Assistant.objects.filter(agency=None).exclude(borrado=1)

        agents = list(
            self.get_related_agents(user_id, include_self).only("id_assistant")
        )

        def get_assistant(agent: Agent) -> int:
            return agent.id_assistant

        asistants = Assistant.objects.filter(
            pk__in=list(map(get_assistant, agents))).exclude(borrado=1)

        if include_self:
            if user.is_assistant:
                asistants |= Assistant.objects.filter(email=user.email)

            if user.is_agent:
                agent = Agent.objects.get(email=user.email)
                asistants |= Assistant.objects.filter(pk=agent.id_assistant)

        return asistants

    def get_related_clients(
        self,
        user_id,
        include_self: bool = False,
        only: list = [],
        include_deleted=False,
        year=None
    ):
        """
        Get related clients based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            include_self: If True, includes the user's own client record if they are an agent.
            only: A list of specific fields to fetch for the clients.
            include_deleted: If True, includes clients that have been marked as deleted.
            year: An string or number with a year to filter by the clients

        Returns:
            A queryset of related clients.
        """
        assistant_id = self.current_is("assistant", user_id)
        agents = self.get_related_agents(user_id, include_self, ["id"])

        if assistant_id:
            clients = self.get_assistant_clients(assistant_id)
        else:
            clients = (
                Client.objects.exclude(id_agent=0)
                .filter(Q(tipoclient=0) | Q(tipoclient=1) | Q(tipoclient=3))
                .filter(id_agent__in=agents)
            )

        if len(only):
            clients = clients.only(*only)

        if not include_deleted:
            clients = clients.exclude(borrado=1)
        if year:
            clients = clients.exclude(~Q(aplication_date__year=year))
        return clients

    def get_related_applications(
        self, user_id, include_self: bool = False, only: list = []
    ):
        """
        Get related applications based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            include_self: If True, includes the user's own application record if they are an agent or assistant.
            only: A list of specific fields to fetch for the applications.

        Returns:
            A queryset of related applications.
        """
        assistant_id = self.current_is("assistant", user_id)
        agents = self.get_related_agents(user_id, include_self)

        if assistant_id:
            clients = self.get_assistant_clients(assistant_id, True)
        else:
            clients = (
                Client.objects.exclude(Q(id_agent=0) | Q(borrado=1))
                .filter(Q(tipoclient=2) | Q(tipoclient=4))
                .filter(id_agent__in=self.queryset_to_list(agents))
            )

        if len(only):
            clients = clients.only(*only)

        return clients

    def get_related_medicaid_clients(
        self, user_id, include_self: bool = False, only: list = []
    ):
        """
        Get related medicaid clients based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            include_self: If True, includes the user's own medicaid clients record if they are an agent or assistant.
            only: A list of specific fields to fetch for the medicaid clients.

        Returns:
            A queryset of related medicaid clients.
        """
        agents = self.get_related_agents(user_id, include_self, ["id"])
        clients = ClientMedicaid.objects.filter(id_agent__in=agents)
        if len(only):
            clients = clients.only(*only)

        return clients

    def get_assistant_clients(
        self, assistant_id, applications_view=False, include_deleted=False
    ):
        """
        Get clients related to a specific assistant.

        Args:
            assistant_id: The ID of the assistant.
            applications_view: If True, filters applications instead fo clients.
            include_deleted: If True, includes clients that have been marked as deleted.

        Returns:
            A queryset of clients or applications related to the specified assistant.
        """
        agents = Agent.objects.filter(
            id_assistant=assistant_id).exclude(borrado=1)
        all_clients = Client.objects.exclude(
            id_agent=0).filter(id_agent__in=agents)
        if not include_deleted:
            all_clients = all_clients.exclude(borrado=1)
        if applications_view:
            all_clients = all_clients.filter(Q(tipoclient=2) | Q(tipoclient=4))
        else:
            all_clients = all_clients.filter(
                Q(tipoclient=0) | Q(tipoclient=1) | Q(tipoclient=3)
            )

        assistant_clients = Client.objects.none()
        for agent in agents:
            assist_insurances = AssitInsurance.objects.filter(
                id_asistente=assistant_id, id_agente=agent.pk
            )
            assist_states = AssitState.objects.filter(
                id_asistente=assistant_id, id_agente=agent.pk
            )
            positions = assist_insurances.values("posicion").distinct()
            for p in positions:
                position = p["posicion"]
                p_assist_insurances = (
                    assist_insurances.filter(posicion=position)
                    .values("id_insurance")
                    .distinct()
                )
                p_assist_states = (
                    assist_states.filter(posicion=position)
                    .values("id_state")
                    .distinct()
                )
                pai_ids = self.queryset_to_list(
                    p_assist_insurances, "id_insurance")
                pas_ids = self.queryset_to_list(p_assist_states, "id_state")

                selection_clients = all_clients.filter(
                    id_state__in=pas_ids, id_insured__in=pai_ids, id_agent=agent.pk
                )
                assistant_clients |= selection_clients

        return assistant_clients

    def is_simple_user(self, user_id) -> bool:
        if not CustomUser.objects.filter(id=user_id).exists():
            return False
        if self.current_is("agent", user_id):
            return False
        if self.current_is("assistant", user_id):
            return False
        if Agency.objects.filter(admin_id=user_id).exists():
            return False
        return True

    def __get_agencies_recursive(self, agency_id: int):
        agencies = Agency.objects.filter(parent_id=agency_id)
        for a in list(agencies):
            agencies |= self.__get_agencies_recursive(a.pk)
        return agencies

    def select_agent(self, agent_id, user_id) -> Agent:
        """
        Select an agent based on their ID and the user's relationship to them.

        Args:
            agent_id: The ID of the agent.
            user_id: The ID of the user.

        Returns:
            The selected agent instance if the agent exists and is related to the user, else None.
        """
        if not agent_id or str(agent_id) == "0" or not user_id:
            return None
        agents = self.get_related_agents(user_id, include_self=True)
        exists = agents.filter(pk=agent_id).exists()
        return agents.get(pk=agent_id) if exists else None

    def select_agency(self, agency_id, user_id) -> Agency:
        """
        Select an agency based on its ID and the user's relationship to it.

        Args:
            agency_id: The ID of the agency.
            user_id: The ID of the user.

        Returns:
            The selected agency instance if the agency exists and is related to the user, else None.
        """
        if not agency_id or str(agency_id) == "0" or not user_id:
            return None
        agencies = self.get_related_agencies(user_id, include_self=True)
        exists = agencies.filter(pk=agency_id).exists()
        return agencies.get(pk=agency_id) if exists else None

    def select_assistant(self, assistant_id, user_id) -> Assistant:
        """
        Select an assistant based on their ID and the user's relationship to them.

        Args:
            assistant_id: The ID of the assistant.
            user_id: The ID of the user.

        Returns:
            The selected assistant instance if the assistant exists and is related to the user, else None.
        """
        if not assistant_id or str(assistant_id) == "0" or not user_id:
            return None
        assistants = self.get_related_assistants(user_id, include_self=True)
        exists = assistants.filter(pk=assistant_id).exists()
        return assistants.get(pk=assistant_id) if exists else None

    def queryset_to_list(
        self, queryset, param="id", to_string=False, joiner: str = ","
    ):
        """
        Convert a queryset to a list or a string based on a specific parameter.

        Args:
            queryset: The queryset to convert.
            param: The parameter to fetch from the queryset.
            to_string: If True, returns a string instead of a list.
            joiner: The character used to join the elements of the list when returning a string.

        Returns:
            A list or a string of the queryset values based on the specified parameter.
        """
        array = list(queryset.values())
        result = self.dict_list_to_list(array, param, to_string, joiner)
        return result

    def dict_list_to_list(
        self, dict_list: list, param="id", to_string=False, joiner: str = ","
    ):
        """
        Convert a list of dictionaries to a list or a string based on a specific parameter.

        Args:
            dict_list: The list of dictionaries to convert.
            param: The parameter to fetch from the dictionaries.
            to_string: If True, returns a string instead of a list.
            joiner: The character used to join the elements of the list when returning a string.

        Returns:
            A list or a string of the dictionary values based on the specified parameter.
        """
        result = set(map(lambda a: str(a[param]), dict_list))
        if to_string:
            result = joiner.join(result)
            result = result if result.strip() != "" else "null"
            return result
        else:
            return list(result)

    def get_selects(self, user_id, *selecteds):
        """
        Get querysets used for selects for specified entities based on the user's role and relationship.

        Args:
            user_id: The ID of the user.
            selecteds: A list of entity names (e.g., "agents", "assistants", "agencies", "insurances", "states", "commission_groups","permission_groups", "status").

        Returns:
            A dictionary containing querysets for the specified entities.
        """
        selects = {}
        if "agents" in selecteds:
            selects["agents"] = (
                self.get_related_agents(user_id, True)
                .values(
                    "id", "id_assistant", "id_agency", "agent_name", "agent_lastname"
                )
                .order_by("agent_name", "agent_lastname")
            )
        if "assistants" in selecteds:
            selects["assistants"] = (
                self.get_related_assistants(user_id, True)
                .values("id", "assistant_name", "assistant_lastname")
                .order_by("assistant_name", "assistant_lastname")
            )
        if "agencies" in selecteds:
            selects["agencies"] = (
                self.get_related_agencies(user_id, True)
                .values("id", "agency_name")
                .order_by("agency_name")
            )
        if "insurances" in selecteds:
            selects["insurances"] = (
                Insured.objects.all().values("id", "names").order_by("names")
            )
        if "states" in selecteds:
            selects["states"] = (
                State.objects.all().values("id", "names").order_by("names")
            )
        if "commission_groups" in selecteds:
            selects["commission_groups"] = (
                CommissionsGroup.objects.all().values("id", "names").order_by("names")
            )
        if "permission_groups" in selecteds:
            selects["permission_groups"] = (
                Group.objects.all().values("id", "name").order_by("name")
            )
        if "status" in selecteds:
            selects["status"] = (
                Status.objects.all().values("id", "names").order_by("names")
            )

        return selects

    def __get_current(self, user_id):
        user: CustomUser = CustomUser.objects.get(pk=user_id)
        return user


# Deprecated
class SorterPagination(LimitOffsetPagination, Common):
    def order_paginate_queryset(self, queryset, request, view=None, order_default=None):
        if isinstance(queryset, list):
            raise BusinessException("Queryset is a List")

        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []

        order = self.check_none(request.GET.get("order"), order_default)
        desc = self.check_none(request.GET.get("desc"), None)
        try:
            if order:
                queryset.order_by(f"{'-' if desc else ''}{order}")
        except:
            try:
                if order_default:
                    queryset.order_by(f"{'-' if desc else ''}{order_default}")
                else:
                    first_key = queryset[0].values().keys()[0]
                    queryset.order_by(first_key)
            except:
                pass
        return list(queryset[self.offset: self.offset + self.limit])

    def order_paginate_list(self, queryset, request, order_default=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []

        order = self.check_none(request.GET.get("order"), order_default)
        desc = self.check_none(request.GET.get("desc"), False)
        desc = 1 if desc else 0

        try:
            if order:
                queryset = sorted(
                    queryset, key=itemgetter(order), reverse=desc)
        except Exception as e:
            try:
                if order_default:
                    queryset = sorted(
                        queryset, key=itemgetter(order_default), reverse=desc
                    )
                else:
                    first_key = queryset[0].keys()[0]
                    queryset = sorted(queryset, key=itemgetter(
                        first_key), reverse=desc)
            except Exception as e:
                pass
        return list(queryset[self.offset: self.offset + self.limit])


class DirectSql:
    """Class with common use cases for interacting with database using sql directly"""

    def print_query_decorator(function):
        """
        A decorator that prints the query string if debug is set to True.

        Args:
            function: The function to be decorated.

        Returns:
            The decorated function that prints the query string if debug is set to True.
        """
        debug = False

        def print_query(*args, **kwargs):
            if kwargs:
                if kwargs.get("query"):
                    if debug:
                        print(kwargs.get("query"))
                else:
                    if debug:
                        print(args[1])
            else:
                if debug:
                    print(args[1])
            return function(*args, **kwargs)

        return print_query

    @print_query_decorator
    def sql_select_all(self, query: str, maps: list = None) -> list:
        """
        Execute a SELECT ALL SQL query and return the result.

        Args:
            query: The SQL query string to execute.
            maps: An optional list of column names to map the results.

        Returns:
            A list containing the results of the executed query.
        """
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        if maps:
            result = self.sql_map_results(maps, result)

        return result

    @print_query_decorator
    def sql_select_paginated(self, query: str, limit: int, offset: int) -> list:
        """
        Execute a paginated SELECT SQL query and return the result.

        Args:
            query: The SQL query string to execute.
            limit: The maximum number of records to return.
            offset: The starting point of the records to return.

        Returns:
            A list containing the paginated results of the executed query.
        """
        query += f" limit {limit} offset {offset}"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    @print_query_decorator
    def sql_select_first(self, query: str) -> tuple:
        """
        Execute a SELECT SQL query and return the first result.

        Args:
            query: The SQL query string to execute.

        Returns:
            A tuple containing the first result of the executed query.
        """
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result

    @print_query_decorator
    def sql_select_many(self, query: str, size: int) -> list:
        """
        Execute a SELECT SQL query and return the specified number of results.

        Args:
            query: The SQL query string to execute.
            size: The number of records to return.

        Returns:
            A list containing the specified number of results of the executed query.
        """
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchmany(size)
        cursor.close()
        return result

    def sql_map_results(self, names: list, cursor: list) -> list:
        """
        Map the results of an executed SQL query using the provided column names.

        Args:
            names: A list of column names to map the results.
            cursor: A list containing the results of the executed query.

        Returns:
            A list containing dictionaries with the mapped results of the executed query.
        """
        result = []
        for c in cursor:
            new_item = {}
            for i, n in enumerate(names):
                new_item[n] = c[i]
            result.append(new_item)
        return result

    def sql_curate_query(self, query: str, only_first: bool = True) -> str:
        """
        Curate an SQL query by removing semicolons and, optionally, splitting the query string.

        Args:
            query: The SQL query string to curate.
            only_first: If True, split the query string and return only the first part.

        Returns:
            A curated SQL query string.
        """
        new_query = str(query).replace(";", "")
        if only_first:
            new_query = new_query.split(" ")[0]
        return new_query


class CryptographyUtils:
    """Class with utilities for cryptographic functions"""

    def encrypt(self, pas: str):
        """
        Encrypt a given string using Fernet encryption with a pre-defined key.

        Args:
            pas: The string to be encrypted.

        Returns:
            The encrypted string in base64 urlsafe format or None if an exception occurs.
        """
        try:
            pas = str(pas)
            str_secret: str = settings.ENCRYPT_KEY
            cipher_pass = Fernet(str_secret.encode("ascii"))
            encrypt_pass = cipher_pass.encrypt(pas.encode("ascii"))
            encrypt_pass = base64.urlsafe_b64encode(
                encrypt_pass).decode("ascii")
            return encrypt_pass
        except Exception as e:
            print(e)
            logger.error(e)
            return None

    def decrypt(self, pas):
        """
        Decrypt a given base64 urlsafe encoded string using Fernet decryption with a pre-defined key.

        Args:
            pas: The base64 urlsafe encoded string to be decrypted.

        Returns:
            The decrypted string or None if an exception occurs.
        """
        try:
            pas = base64.urlsafe_b64decode(pas)
            str_secret: str = settings.ENCRYPT_KEY
            cipher_pass = Fernet(str_secret.encode("ascii"))
            decod_pass = cipher_pass.decrypt(pas).decode("ascii")
            return decod_pass
        except Exception as e:
            print(e)
            logger.error(e)
            return None


class HTMLFilter(HTMLParser):
    """
    A custom HTML parser that extracts and concatenates the text content from an HTML string.

    Inherits from the HTMLParser class in the html.parser module.
    """

    text = ""

    def handle_data(self, data):
        """
        Handle the text content of an HTML element.

        Args:
            data: The text content of an HTML element.
        """
        self.text += data


class TwilioCommons:
    """
    A utility class for handling Twilio-related functionalities.
    """

    def twilio_validate_post_request(self, request: HttpRequest):
        """
        Validate an incoming POST request from Twilio.

        Args:
            request: The incoming HttpRequest object.

        Raises:
            ForbiddenException: If the request is not valid according to Twilio's RequestValidator.
        """
        validator = RequestValidator(settings.SMS_TOKEN)
        url = f"https://{request.get_host()}{request.get_full_path()}"
        request_valid = validator.validate(
            url,
            request.POST,
            request.META.get("HTTP_X_TWILIO_SIGNATURE", ""),
        )
        if not request_valid:
            raise ForbiddenException()


class CompanySMSCommons:
    """
    A utility class that provides methods for handling phone numbers and user
    phone number related queries in the context of a company.
    """

    def sms_ready_phone_number(self, phone: str):
        """
        Converts a phone number string into a standardized format by removing
        special characters and ensuring the number starts with a "+" and the
        country code (default is "+1" for US).

        Args:
            phone (str): The phone number string to standardize.

        Returns:
            str: The standardized phone number string.
        """
        phone = (
            phone.replace("(", "").replace(")", "").replace(
                " ", "").replace("-", "")
        )
        phone = phone if phone.startswith("+") else f"+1{phone}"
        return phone

    def sms_get_user_by_phone(self, phone: str):
        """
        Retrieves a user by their phone number. The method supports various
        formats of the phone number.

        Args:
            phone (str): The phone number to search for.

        Returns:
            CustomUser: The user object if a single user is found, None if no user is found.
            Raises ValidationException if multiple users are found with the same phone number.
        """
        phone_code = (
            "+1"
            if phone.startswith("+1") and len(phone) == 12
            else phone[0: len(phone) - 10]
            if phone.startswith("+")
            else ""
        )
        phone_no_plus = phone[len(phone_code):]
        phone_no_plus_parenthesis = f"({phone_no_plus[:3]}){phone_no_plus[3:]}"
        phone_no_plus_parenthesis_minus = (
            f"({phone_no_plus[:3]}){phone_no_plus[3:6]}-{phone_no_plus[6:]}"
        )
        phone_parenthesis = phone_code + phone_no_plus_parenthesis
        phone_parenthesis_minus = phone_code + phone_no_plus_parenthesis_minus
        users = CustomUser.objects.filter(
            Q(personal_phone_number=phone)
            | Q(personal_phone_number=phone_no_plus)
            | Q(personal_phone_number=phone_no_plus_parenthesis)
            | Q(personal_phone_number=phone_no_plus_parenthesis_minus)
            | Q(personal_phone_number=phone_parenthesis)
            | Q(personal_phone_number=phone_parenthesis_minus)
            | Q(company_phone_number=phone)
            | Q(company_phone_number=phone_no_plus)
            | Q(company_phone_number=phone_no_plus_parenthesis)
            | Q(company_phone_number=phone_no_plus_parenthesis_minus)
            | Q(company_phone_number=phone_parenthesis)
            | Q(company_phone_number=phone_parenthesis_minus)
        )
        if users.count() == 1:
            return users.get()
        elif users.count() > 1:
            ValidationException(
                "There are more than one users with same phone number")
        else:
            return None

    def sms_check_no_user_with_same_phone(self, phone, exclude_user_id):
        """
        Checks if there are any users with the same phone number, excluding
        the user specified by `exclude_user_id`.

        Args:
            phone (str): The phone number to check.
            exclude_user_id (int): The user ID to exclude from the search.

        Returns:
            bool: True if there is no user with the same phone number, False otherwise.
            Raises ValidationException if a user with the same phone number exists.
        """
        phone = self.sms_ready_phone_number(phone)
        user = self.sms_get_user_by_phone(phone)
        if not user or user.pk == exclude_user_id:
            return True
        else:
            ValidationException("There is a user with same phone already")


class PDFCommons:
    """
    A utility class for handling PDF-related tasks, such as creating tables
    and generating PDF files.
    """

    def pdf_create_table(
        self,
        headers: list,
        data: list,
        page_size=letter,
        title='Report',
        footer=False,
        filename="Report"
    ):
        """
        Creates a PDF table with the given headers and data, and returns it
        as a FileResponse.

        Args:
            headers (list): The headers of the table.
            data (list): The data to be displayed in the table.
            page_size (tuple, optional): The page size of the PDF. Defaults to A3.
            rowHeights (list, optional): The heights of the rows. Defaults to None.
            colWidths (list, optional): The widths of the columns. Defaults to None.
            repeatRows (int, optional): The number of header rows to be repeated
                on each page. Defaults to 1.

        Returns:
            FileResponse: A FileResponse containing the generated PDF.
        """
        pdf_buffer = io.BytesIO()
        row_height = 1 * inch
        left_margin = 1 * inch
        right_margin = 1 * inch
        top_margin = 1 * inch
        bottom_margin = 1 * inch

        my_doc = SimpleDocTemplate(pdf_buffer, pagesize=page_size,
                                   leftMargin=left_margin, rightMargin=right_margin,
                                   topMargin=top_margin, bottomMargin=bottom_margin)
        elements = []

        # Add header
        elements.append(Paragraph(title, styles['Title']))

        # Add table
        to_render = [headers]
        to_render.extend(data)

        # Increase font size and row heights

        table = Table(
            to_render, rowHeights=[row_height] * (len(data) + 1)
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("FONTSIZE", (0, 0), (-1, -1), 16),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEADING", (0, 0), (-1, -1), 16),
                ]
            )
        )
        elements.append(table)

        # Add footer with total
        if footer:
            total = sum([float(row[-1] if row[-1] else 0) for row in data])
            footer_text = f"Total: ${total:.2f}"

            footer_style = ParagraphStyle(
                name='CustomFooterStyle',
                # You can adjust the parent style as needed
                parent=styles['Normal'],
                fontSize=25,
                alignment=1,  # 0=left, 1=center, 2=right
                fontName='Helvetica-Bold'  # Replace with your desired font
            )
            # Create a Paragraph element for the footer with the custom style
            footer_paragraph = Paragraph(footer_text, footer_style)

            elements.append(Spacer(1, 200))  # Add some space above the footer
            elements.append(footer_paragraph)

        my_doc.build(elements)
        pdf_buffer.seek(0)
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename+".pdf")


class PaymentCommons(DirectSql, AgencyManagement):
    """
    The PaymentCommons class inherits from DirectSql and AgencyManagement and provides
    methods related to payment calculations and handling for agents and clients.
    """

    def pay_get_agent_year_commission(
        self,
        agent_id,
        insured_id,
        year,
        state_sigla,
        type: str,
        florida_month,
        florida_year,
        has_assistant: bool = False
    ):
        """
        Calculate and return the agent's commission for a given year, state, and type.
        Includes automatic handling if agent is from Florida Blue or other insurance

        Args:
            agent_id (int): The agent's ID.
            insured_id (int): The ID of the insured.
            year (int): The year to consider for the commission calculation(it should be the year of infoMonth for not Florida Blue agents).
            state_sigla (str): The state abbreviation.
            type (str): The type of commission (e.g., "RENEW", "oep", "new", "set").
            florida_month (int): The month for Florida state calculations(must be current requested month, not infoMonth's).
            florida_year (int): The year for Florida state calculations(must be current requested year, not infoMonth's).

        Returns:
            float: The calculated commission.
        """
        commission = 0.0
        ren, tier1, tier2, tier3, tier4, assistant_debuf = (
            10.0,
            15.0,
            20.0,
            25.0,
            30.0,
            3.0,
        )

        if int(insured_id) == 3:
            year_correction_filter = ''
            try:
                agent = Agent.objects.get(id=agent_id)
            except Exception as e:
                logger.warning(
                    f"There was no agent with id {agent_id} in the system")
            if (year == '2022' or year == 2022):
                if type.upper().startswith("RENEW"):
                    return 10
                else:
                    return 15
            if (year == '2023' or year == 2023):
                if type.upper().startswith("RENEW"):
                    if int(florida_month) != 2 and int(florida_month) != 3 and int(florida_month) != 4:
                        return ren

            if (year == '2024' or year == 2024):
                year_correction_filter = "AND spg.new_ren NOT LIKE '%RENEW%'"
                ren, tier1, tier2, assistant_debuf = (
                    15.0,
                    15.0,
                    30.0,
                    3.0,
                )
                if type.upper().startswith("RENEW"):
                    return ren - assistant_debuf if has_assistant else ren

            sql = f"""
            select 
                sum(pg.n_member)members, a.id 
            FROM 
                payments_global pg 
                join
                    (select 
                        c.suscriberid,c.id_agent 
                    from 
                        client c 
                    where 
                        year(c.aplication_date) = {year} and (c.tipoclient = 0 or c.tipoclient = 1 or c.tipoclient = 3) and c.borrado<>1
                    group by 
                    c.suscriberid,c.id_agent
                    ) c on c.suscriberid=pg.p_number 
                join 
                    agent a on c.id_agent = a.id 
                    
                where 
                    pg.id in 
                    (select 
                        max(spg.id) 
                    from payments_global spg 
                    where
                        spg.pyear = {florida_year} and spg.month = {florida_month} and spg.id_insured = 3  {year_correction_filter}
                    group by(spg.p_number))
                    
                    and a.id = {agent_id} group by a.id
            """
            florida_blue_commission = self.sql_select_first(sql)
            if not florida_blue_commission:
                return commission
            members = int(florida_blue_commission[0])
            if (year == '2023' or year == 2023) and members >= 60:
                commission = tier4
            elif (year == '2023' or year == 2023) and members >= 40:
                commission = tier3
            elif members >= 20:
                commission = tier2
            else:
                commission = tier1
            if has_assistant:
                commission -= assistant_debuf
        else:
            sql = f"""SELECT c.comm_new, c.comm_rew, c.comm_set FROM agent_commission c
                INNER JOIN state ON state.id = c.id_state WHERE c.id_agent = {int(agent_id)}
                AND c.id_insured = {int(insured_id)} AND c.yearcom = {int(year)} AND
                state.sigla  LIKE '%{state_sigla}%'"""
            result = self.sql_select_first(sql)
            if not result:
                sql = f"""SELECT c.comm_new, c.comm_rew, c.comm_set FROM group_commission c
                    JOIN agent a on c.id_group = a.id_commission_group
                    INNER JOIN state ON state.id = c.id_state WHERE a.id = {int(agent_id)}
                    AND c.id_insured = {int(insured_id)} AND c.yearcom = {int(year)} AND
                    state.sigla  LIKE '%{state_sigla}%'"""
                result = self.sql_select_first(sql)

            if not result:
                return commission

            if type.lower() == "oep" or type.lower() == "new":
                commission = float(result[0])
            elif type.lower() == "set":
                commission = float(result[2])
            else:
                commission = float(result[1])
        return commission

    def pay_get_agent_payment_using_commission(
        self, client_payment, agent_commission, num_members
    ):
        """
        Calculate and return the agent's payment using their commission and the number of members.

        Args:
            client_payment (float): The client's payment amount.
            agent_commission (float): The agent's commission.
            num_members (int): The number of members.

        Returns:
            float: The calculated agent's payment.
        """
        commission = float(agent_commission) * int(num_members)
        if float(client_payment) == 0:
            return 0
        return -commission if float(client_payment) < 0.0 else commission

    def pay_get_total_agent_payment_for_client(
        self, year, month, agent, client_id=None, suscriber=None
    ):
        """
        Calculate and return the total payment for a specific client, year, and month that should be done to the specific agent.
        Including posible multiple payments of the client with diferent infoMonth.
        This method calculates the hypothetical payment for the agent based on actual related data, does not use the actual payment in the payment table.
        Args:
            year (int): The year to consider for the payment calculation.
            month (int): The month to consider for the payment calculation.
            agent (int): The agent's ID.
            client_id (int, optional): The client's ID, can be null if a suscriber id is passed.
            suscriber (str, optional): The client's subscriber ID, only used if no client id is passed.

        Returns:
            tuple: A tuple containing the total payment (float) and the log (list) of the process.
        """
        log = self.update_log("Starting check...", [])

        clients = self.__find_client(client_id, suscriber)
        if not clients.exists():
            self.update_log("Client does not exists", log)
            return 0.0, log

        clients = clients.filter(id_agent=agent)
        if not clients.exists():
            self.update_log("Agent has not that client", log)
            return 0.0, log

        if clients.count() > 1:
            self.update_log(
                f"There are more than une client for this payment(clients.count()). This should not be. Clients:{self.queryset_to_list(clients, to_string=True)}",
                log,
            )

        client = clients.get()
        pyments_global = PaymentsGlobal.objects.filter(
            pyear=year, p_number=client.suscriberid
        ).filter(Q(month=month) | Q(month="0" + month))
        if not pyments_global.exists():
            self.update_log(
                "There is no Payment Global for this selction", log)
            return 0.0, log

        self.update_log(
            f"""There are {pyments_global.count()} entries in payment global for this selection :{self.queryset_to_list(pyments_global)}""",
            log,
        )

        query = f"""select sum(case when(pg.commission > 0) then pg.n_member else 0 end),
            sum(case when(pg.commission < 0) then pg.n_member else 0 end), pg.p_number,
            pg.p_state,pg.new_ren,pg.info_month,pg.id FROM payments_global pg where pg.id in
            ({self.queryset_to_list(pyments_global, to_string=True)}) GROUP by pg.info_month"""
        data = self.sql_select_all(query)
        self.update_log(
            f"There are {len(data)} dates for commission: {list(map(lambda a : a[5], data))}",
            log,
        )
        total_paid = 0.0
        for row in data:
            comm_year = self.date_from_text(row[5])
            if not comm_year:
                self.update_log(
                    f"""The date for commission could not be parsed in payment global with id {row[6]} so commission for this payment will be 0""",
                    log,
                )
                agent_comm = 0
            else:
                agent_comm = self.pay_get_agent_year_commission(
                    agent,
                    client.id_insured,
                    comm_year.year,
                    row[3],
                    row[4],
                    month,
                    year,
                )
            paid_comm = self.pay_get_agent_payment_using_commission(
                1, agent_comm, row[0]
            ) + self.pay_get_agent_payment_using_commission(-1, agent_comm, row[1])
            self.update_log(
                f"""The payment for date {row[5]} is {paid_comm}. The client sucriber is {row[2]},its members total count is {row[0]-row[1]}, the agent commission is {agent_comm}, the state is {row[3]}, the type is {row[4]} and the insured is {client.id_insured}.""",
                log,
            )
            total_paid += paid_comm

        self.update_log(
            f"The total payment for year {year} and month {month} should be {total_paid}",
            log,
        )
        made_payment = self.pay_get_made_payments_for_agent(
            year, month, agent, client.pk, suscriber
        )
        self.update_log(
            f"The total payment for year {year} and month {month} in Payments table was {made_payment}",
            log,
        )

        return total_paid, log

    def pay_get_made_payments_for_agent(
        self, year, month, agent, client=None, suscriber=None, withId=False
    ):
        """
        Get the made payments for an agent in a specific year, month, and client.

        Args:
            year (int): The year to consider for the payment retrieval.
            month (int): The month to consider for the payment retrieval.
            agent (int): The agent's ID.
            client (int, optional): The client's ID, can be null if a suscriber id is passed.
            suscriber (str, optional): The client's subscriber ID, only used if no client id is passed.
            withId (bool, optional): If True, return the payment ID in the response.

        Returns:
            tuple[float, int]: The payment value and payment id if withId param is true.
            float: The payment value if withId param is false (default behavior)
        """
        clients = self.__find_client(client, suscriber)
        if not clients:
            return None
        client = clients.get()
        payment = Payments.objects.filter(
            id_agent=agent, id_client=client.pk, fecha=year
        )
        if not payment.exists():
            return None

        month = self.map_month(month)
        month_payment = payment.values(month)

        if withId:
            return month_payment[0], payment[0].pk

        return month_payment[0]

    def pay_get_actual_payments_for_agent(
        self, payment_ids: str, months: str, indx_payment: int = None
    ):
        """
        Get the actual payments for an agent based on provided payment IDs and months.
        This method attemps to reflect all payments made to an agent based on payment_global table data
        and using the method 'pay_get_agent_year_commission' for guessing the commission of the agent, so its
        based on actual related data.
        Args:
            payment_ids (str): A string of payment IDs separated by commas.
            months (str): A string of months separated by commas.
            indx_payment (int, optional): The payment index.

        Returns:
            tuple: A tuple containing the payment data (list) and the total commission (float).
        """
        # query = f"""SELECT a.agent_name,a.agent_lastname,c.names,i.names,a.npn,
        #     c.suscriberid,pg.n_member,p.fecha, pg.e_date,pg.new_ren,c.lastname,
        #     pg.info_month,pg.fecha,pg.month,pg.id, pg.commission,i.id,pg.pyear,
        #     pg.p_state,a.id,pg.month FROM payments p left join agent a on p.id_agent=a.id
        #     left join client c on p.id_client=c.id left join insured i on
        #     c.id_insured=i.id left join payments_global pg on
        #     ((c.suscriberid=pg.p_number) and (p.fecha=pg.pyear) and pg.month
        #     in ({months}))
        #     where p.id in ({payment_ids})"""
        query = f"""SELECT a.agent_name,a.agent_lastname,c.names,c.inames,a.npn,
            c.suscriberid,c.n_member,p.fecha, c.e_date,c.new_ren,c.lastname,
            c.info_month,c.fecha,c.month,c.pgid, c.commission,c.iid,c.pyear,
            c.p_state,a.id,c.month,p.id FROM payments p left join agent a on p.id_agent=a.id
            join (select c.id,c.names, c.lastname, i.names inames,pg.fecha,pg.month,
            pg.id pgid,pg.commission,i.id iid,pg.pyear,pg.p_state,c.suscriberid,
            pg.n_member, pg.e_date, pg.new_ren, pg.info_month from client c left join
            insured i on c.id_insured = i.id left join payments_global pg on
            (c.suscriberid=pg.p_number and pg.month in ({months}))) c on 
            (p.id_client=c.id and p.fecha=c.pyear) where p.id in ({payment_ids})"""
        response = self.sql_select_all(query)
        data = []
        total_commission = 0
        for row in response:
            paid_agent_commission = 0
            comm_date = self.date_from_text(row[11])
            if comm_date:
                e_year = comm_date.year
                e_month = self.map_month(comm_date.month)
            else:
                e_month = None
                e_year = None
            # if indx_payment:
            #     pay_control = PaymentsControl.objects.filter(
            #         index_payment=indx_payment, id_payment=row[21], month=row[20]
            #     )
            #     if pay_control.exists():
            #         paid_agent_commission = pay_control[0].commision

            if row[6] and comm_date:
                agent_comm = self.pay_get_agent_year_commission(
                    int(row[19]),
                    row[16],
                    comm_date.year,
                    row[18],
                    row[9],
                    row[20],
                    row[17],
                )
                paid_agent_commission = self.pay_get_agent_payment_using_commission(
                    row[15], agent_comm, row[6]
                )

            data.append(
                {
                    "agent_name": self.check_none(row[0], "")
                    + " "
                    + self.check_none(row[1], ""),
                    "client_name": self.check_none(row[2], "")
                    + " "
                    + self.check_none(row[10], ""),
                    "insured_name": row[3],
                    "npn": row[4],
                    "suscriberid": row[5],
                    "num_member": row[6],
                    "effective_date": row[8],
                    "type": row[9],
                    "date": str(row[20]) + "/01/" + str(row[17]),
                    "month": f"{e_month.capitalize() if e_month else 'None'}/{e_year if e_year else 'None'}",
                    "commission": paid_agent_commission,
                    "state": row[18],
                }
            )
            total_commission += paid_agent_commission

        return data, total_commission

    def update_log(self, data, log: list = []):
        """
        Update the log with new data.

        Args:
            data (dict): The data to be added to the log.
            log (list, optional): The existing log. Defaults to an empty list.

        Returns:
            list: The updated log containing the new data.
        """
        log.append({f"{len(log) + 1}": data})
        return log

    def pay_get_max_indx_payment(self, insured, year, month):
        """
        Get the maximum index_payment value for a given insured, year, and month.

        Args:
            insured (int): The insured ID.
            year (int): The year for which the maximum index_payment is required.
            month (int): The month for which the maximum index_payment is required.

        Returns:
            int: The maximum index_payment value for the specified insured, year, and month.
        """
        query = f"""select max(pc.index_payment) from payments_control pc
            where pc.id_insured = {insured} and pc.year_made = {year} and
            pc.month = {month}"""
        result = self.sql_select_first(query)
        if result and result[0]:
            return int(result[0])
        else:
            return 0

    def pay_get_max_agent_index_payment(self, insured, year, month, agent=None):
        """
        Get the maximum index_payment value for a given insured, year, and month.

        Args:
            insured (int): The insured ID.
            year (int): The year for which the maximum index_payment is required.
            month (int): The month for which the maximum index_payment is required.

        Returns:
            int: The maximum index_payment value for the specified insured, year, and month.
        """
        agent_filter = ''
        if agent:
            agent_filter = f"and ap.id_agent={agent}"
        query = f"""select max(ap.payment_index) from agent_payments ap
            where ap.id_insured = {insured} {agent_filter} and ap.year = {year} and
            ap.month = {month}"""
        result = self.sql_select_first(query)
        if result and result[0]:
            return int(result[0])
        else:
            return 0

    def __find_client(self, client_id=None, suscriber_id=None):
        if not (client_id or suscriber_id):
            return None

        if client_id:
            clients = Client.objects.filter(id=client_id)
        else:
            clients = Client.objects.filter(suscriberid=suscriber_id)

        if not clients.exists():
            return None

        return clients


class DashboardCommons(Common):
    """
    This class contains methods for common operations related to the dashboard.
    It inherits from the Common class.
    """

    def dash_get_alternative_user(self, request):
        """
        Get the alternative user ID based on the request query parameters.

        Args:
            request (Request): The HTTP request containing the user information and query parameters.

        Returns:
            int: The alternative user's primary key (ID) if available, or the current user's primary key.
        """
        current_user: CustomUser = request.user

        if not current_user.is_admin:
            return current_user.pk

        alternative = self.check_none(request.query_params.get("alternative"))

        if not alternative:
            return current_user.pk

        user = None
        if alternative.startswith("ag"):
            alternative_id = alternative[2:]
            try:
                user = Agent.objects.get(id=alternative_id)
            except Exception as e:
                pass
        elif alternative.startswith("as"):
            alternative_id = alternative[2:]
            try:
                user = Assistant.objects.get(id=alternative_id)
            except Exception as e:
                pass

        alt_id = None
        if user:
            try:
                alt_user = CustomUser.objects.get(email=user.email)
                alt_id = alt_user.pk
            except Exception as e:
                pass

        user_id = alt_id if alt_id else current_user.pk

        return user_id
