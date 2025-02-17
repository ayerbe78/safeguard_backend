from ..imports import *
from . import _resources as log_res


class GeneralLogsView(APIView, Common, LimitOffsetPagination):
    permission_classes = [HasGeneralLogsPermission]

    def get(self, request: APIViewRequest):
        logs = self.__apply_filters(request)
        logs = self.__filter_by_resource(logs, request)
        logs = self.__apply_search(logs, request)
        logs = self.apply_order_queryset(logs, request, "-added_on")

        page = self.paginate_queryset(logs, request)
        serializer = ApiLogSerilizer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_filters(self, request):
        logs = ApiLog.objects.all().annotate(
            user_name=Concat("user__first_name", V(" "), "user__last_name"),
            log_id=F("id"),
        )

        date_start = self.check_none(request.query_params.get("date_start"))
        if date_start:
            dt_object = datetime.strptime(
                date_start, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=0, minute=0, second=0, microsecond=0)
            logs = logs.filter(added_on__gte=dt_object)

        date_end = self.check_none(request.query_params.get("date_end"))
        if date_end:
            dt_object = datetime.strptime(
                date_end, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=23, minute=59, second=59, microsecond=999999)
            logs = logs.filter(added_on__lte=dt_object)

        method = self.check_none(request.query_params.get("method"))
        if method == "post":
            logs = logs.filter(method="POST")
        elif method == "put":
            logs = logs.filter(Q(method="PUT") | Q(method="PATCH"))
        elif method == "delete":
            logs = logs.filter(method="DELETE")

        status = self.check_none(request.query_params.get("status"))
        if status == "1":
            logs = logs.filter(status_code__startswith="2")
        elif status == "2":
            logs = logs.filter(status_code__startswith="4")
        elif status == "3":
            logs = logs.filter(status_code__startswith="5")

        actor = self.check_none(request.query_params.get("actor"))
        if actor:
            logs = logs.filter(user=actor)

        return logs

    def __apply_search(self, logs, request):
        search = self.check_none(request.query_params.get("search"))
        if search:
            logs = logs.filter(
                Q(api__icontains=search)
                | Q(user_name__icontains=search)
                | Q(user_email__icontains=search)
                | Q(status_code__contains=search)
                | Q(body__contains=search)
            )

        return logs

    def __filter_by_resource(self, logs, request):
        resource = self.check_none(request.query_params.get("resource"))
        if not resource:
            return logs

        aux_resource = []
        aux_prefix = None

        if resource == log_res.MAIL:
            aux_resource = [log_res.MAIL]
        elif resource == log_res.SMS:
            aux_resource = [log_res.SMS]
        elif resource == log_res.ASSISTANT:
            aux_resource = [log_res.ASSISTANT]
        elif resource == log_res.AGENCY:
            aux_resource = [log_res.AGENCY]
        elif resource == log_res.AGENT_COMM:
            aux_resource = [log_res.AGENT_COMM]
        elif resource == log_res.CITY:
            aux_resource = [log_res.CITY]
        elif resource == log_res.AGENCY_COMM:
            aux_resource = [log_res.AGENCY_COMM]
        elif resource == log_res.COMM_GROUPS:
            aux_resource = [log_res.COMM_GROUPS]
        elif resource == log_res.COUNTY:
            aux_resource = [log_res.COUNTY]
        elif resource == log_res.DOCUMENT_TYPE:
            aux_resource = [log_res.DOCUMENT_TYPE]
        elif resource == log_res.EVENT:
            aux_resource = [log_res.EVENT]
        elif resource == log_res.GROUP_COMM:
            aux_resource = [log_res.GROUP_COMM]
        elif resource == log_res.GROUPS:
            aux_resource = [log_res.GROUPS]
        elif resource == log_res.HEALTH_PLAN:
            aux_resource = [log_res.HEALTH_PLAN]
        elif resource == log_res.INSURED:
            aux_resource = [log_res.INSURED]
        elif resource == log_res.LANGUAJE:
            aux_resource = [log_res.LANGUAJE]
        elif resource == log_res.PLAN_NAME:
            aux_resource = [log_res.PLAN_NAME]
        elif resource == log_res.POLICY:
            aux_resource = [log_res.POLICY]
        elif resource == log_res.PRODUCT:
            aux_resource = [log_res.PRODUCT]
        elif resource == log_res.SOC_SERVICE_REF:
            aux_resource = [log_res.SOC_SERVICE_REF]
        elif resource == log_res.SPECIAL_ELECTION:
            aux_resource = [log_res.SPECIAL_ELECTION]
        elif resource == log_res.STATE:
            aux_resource = [log_res.STATE]
        elif resource == log_res.STATUS:
            aux_resource = [log_res.STATUS]
        elif resource == log_res.TYPE:
            aux_resource = [log_res.TYPE]
        elif resource == log_res.VIDEO:
            aux_resource = [log_res.VIDEO]
        elif resource == log_res.CLAIM:
            aux_resource = [log_res.CLAIM]
        elif resource == log_res.CLIENT:
            aux_resource = [log_res.CLIENT]
        elif resource == log_res.APPLICATION:
            aux_resource = [log_res.APPLICATION]
        elif resource == log_res.AGENT:
            aux_resource = [log_res.AGENT]
        elif resource == log_res.AGENT_DOCUMENT:
            aux_resource = [log_res.AGENT_DOCUMENT]
        elif resource == log_res.CLIENT_DOCUMENT:
            aux_resource = [log_res.CLIENT_DOCUMENT]
        elif resource == log_res.CLIENT_DEPENDANT:
            aux_resource = [log_res.CLIENT_DEPENDANT]
        elif resource == log_res.CLIENT_NOTE:
            aux_resource = [log_res.CLIENT_NOTE]
        elif resource == log_res.PENDING_DOCUMENT:
            aux_resource = [log_res.PENDING_DOCUMENT]
        elif resource == log_res.LOGIN:
            aux_prefix = "auth"
            aux_resource = [log_res.LOGIN]
        elif resource == log_res.PAYMENTS:
            aux_resource = [
                "import_payment_csv",
                "delete_payment_csv",
                "make_repayment",
                "payment_agency",
                "payment/assistant",
                "import_bob",
            ]
        elif resource == log_res.USERS:
            aux_prefix = "auth"
            aux_resource = [
                "user_update",
                "register",
                "edit_user_permissions",
                "new_edit_user_permissions",
                "remove_permission_from_user",
            ]
        elif resource == log_res.PERMISSIONSGROUPS:
            aux_prefix = "auth"
            aux_resource = [
                "edit_group",
                "create_group",
                "delete_group",
                "add_permission_to_group",
                "add_user_to_group",
                "remove_user_from_group",
                "remove_permission_from_group",
                "edit_group_permissions",
                "new_edit_group_permissions",
            ]

        logs = self.__aux_filter_by_resource(logs, aux_resource, aux_prefix)
        return logs

    def __aux_filter_by_resource(self, logs, resources: list, prefix: str = "api"):
        search_list = Q()
        for r in resources:
            search_param = f"/{prefix if prefix else 'api'}/{r}/"
            search_list |= Q(api__icontains=search_param) | Q(
                api__endswith=search_param[:-1]
            )
        logs = logs.filter(search_list)
        return logs


class DataForGeneralLogsView(APIView, Common):
    permission_classes = [HasGeneralLogsPermission]

    def get(self, request: APIViewRequest):
        users = (
            CustomUser.objects.values("id")
            .annotate(
                user_name=Concat("first_name", V(" "), "last_name"),
                user_email=F("email"),
            )
            .order_by("user_name")
        )
        resources = self.__get_resources_selects(request)
        return Response(dict(users=users, resources=resources))

    def __get_resources_selects(self, request):
        resources = dict(
            MAIL=log_res.MAIL,
            SMS=log_res.SMS,
            CLIENT=log_res.CLIENT,
            APPLICATION=log_res.APPLICATION,
            AGENT=log_res.AGENT,
            ASSISTANT=log_res.ASSISTANT,
            AGENCY=log_res.AGENCY,
            AGENT_COMM=log_res.AGENT_COMM,
            CITY=log_res.CITY,
            AGENCY_COMM=log_res.AGENCY_COMM,
            COMM_GROUPS=log_res.COMM_GROUPS,
            COUNTY=log_res.COUNTY,
            DOCUMENT_TYPE=log_res.DOCUMENT_TYPE,
            EVENT=log_res.EVENT,
            GROUP_COMM=log_res.GROUP_COMM,
            GROUPS=log_res.GROUPS,
            HEALTH_PLAN=log_res.HEALTH_PLAN,
            INSURED=log_res.INSURED,
            LANGUAJE=log_res.LANGUAJE,
            PLAN_NAME=log_res.PLAN_NAME,
            POLICY=log_res.POLICY,
            PRODUCT=log_res.PRODUCT,
            SOC_SERVICE_REF=log_res.SOC_SERVICE_REF,
            SPECIAL_ELECTION=log_res.SPECIAL_ELECTION,
            STATE=log_res.STATE,
            STATUS=log_res.STATUS,
            TYPE=log_res.TYPE,
            VIDEO=log_res.VIDEO,
            CLAIM=log_res.CLAIM,
            AGENT_DOCUMENT=log_res.AGENT_DOCUMENT,
            CLIENT_DOCUMENT=log_res.CLIENT_DOCUMENT,
            CLIENT_DEPENDANT=log_res.CLIENT_DEPENDANT,
            CLIENT_NOTE=log_res.CLIENT_NOTE,
            PENDING_DOCUMENT=log_res.PENDING_DOCUMENT,
            LOGIN=log_res.LOGIN,
            PAYMENTS=log_res.PAYMENTS,
            USERS=log_res.USERS,
            PERMISSIONS_GROUPS=log_res.PERMISSIONSGROUPS,
        )
        resources = list(
            (
                dict(id=v, name=k.replace("_", " ").capitalize())
                for k, v in resources.items()
            )
        )
        resources = self.apply_order_dict_list(resources, request, "name")
        return resources
