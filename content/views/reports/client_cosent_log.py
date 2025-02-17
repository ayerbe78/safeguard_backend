from ..imports import *


class ClientConsentLogViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasClientConsentLogPermission]
    serializer_class = ClientConsentLogSerializer
    queryset = Agent.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        clients_id = self.get_related_clients(
            user.pk, True, ['id']) | self.get_related_applications(user.pk, True, ['id'])
        year = request.GET.get('year', date.today().year)
        client_logs = ClientConsentLog.objects.filter(
            id_client__in=clients_id, year=year)

        id_agent = int(request.GET.get('agent', 0))
        if id_agent != 0:
            client_logs = client_logs.filter(id_agent=id_agent)

        signed = int(request.GET.get('signed', 0))
        if signed and signed == 1:
            client_logs = client_logs.filter(signed=True)
        elif signed == 2:
            client_logs = client_logs.exclude(signed=True)

        entries = self.__apply_search(client_logs, request)
        entries = self.apply_order_queryset(entries, request, "agent_name")

        page = self.paginate_queryset(entries)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(agent_name__icontains=search) | queryset.filter(
                client_name__icontains=search)
        return queryset

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_secondary_agent(self, request: HttpRequest):
        selects = self.get_selects(request.user.pk, "agents")
        return Response(selects)
