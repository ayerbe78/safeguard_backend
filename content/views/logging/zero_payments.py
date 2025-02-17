from ..imports import *


class ZeroPaymentsView(APIView, AgencyManagement, LimitOffsetPagination):
    permission_classes = [HasZeroPaymentLogsPermission]

    def get(self, request: APIViewRequest):
        logs = self.__apply_filters(request)
        logs = self.__apply_search(logs, request)
        logs = self.apply_order_queryset(logs, request, "agent_name")

        page = self.paginate_queryset(logs, request)
        serializer = EmptyPaymentLogEntrySerilizer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_filters(self, request: APIViewRequest):
        user: CustomUser = request.user
        year = self.check_none(request.query_params.get("year"))
        insured = self.check_none(request.query_params.get("insured"))
        assistant = self.check_none(request.query_params.get("assistant"))
        agency = self.check_none(request.query_params.get("agency"))
        agent = self.check_none(request.query_params.get("agent"))
        month = self.check_none(request.query_params.get("month"))
        repayment = self.check_none(request.query_params.get("repayment"))
        state = self.check_none(request.query_params.get("state"))

        if year:
            logs = EmptyPaymentLogEntry.objects.filter(payment_year=year)
        else:
            logs = EmptyPaymentLogEntry.objects.all()

        if insured:
            logs = logs.filter(insured_id=insured)

        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        assistant = self.select_assistant(request.GET.get("assistant"), user.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)

        if agent:
            agents = agents.filter(pk=agent.pk)
        if assistant:
            agents = agents.filter(id_assistant=assistant.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        if not (user.is_admin and not (agent or assistant or agency)):
            logs = logs.filter(agent_id__in=self.queryset_to_list(agents))

        if month:
            logs = logs.filter(Q(payment_month=month) | Q(payment_month=f"0{month}"))

        if repayment:
            logs = logs.filter(repayment=1)

        if state:
            logs = logs.filter(state_id=state)

        return logs

    def __apply_search(self, logs, request):
        search = self.check_none(request.query_params.get("search"))
        if search:
            logs = logs.filter(
                Q(suscriberid__icontains=search)
                | Q(client_name__icontains=search)
                | Q(info_month__icontains=search)
                | Q(agent_npn__icontains=search)
                | Q(agent_name__icontains=search)
                | Q(insured_name__icontains=search)
                | Q(state_sigla__icontains=search)
            )

        return logs


class DataForZeroPaymentsView(APIView, AgencyManagement):
    permission_classes = [HasZeroPaymentLogsPermission]

    def get(self, request):
        selects = self.get_selects(
            request.user.pk, "agents", "states", "insurances", "assistants", "agencies"
        )
        return Response(selects)
