from ..imports import *


class PreLetterLogViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasPreLetterLogPermission]
    serializer_class = PreLetterLogSerializer
    queryset = PreLetterLog.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        agents_id = self.get_related_agents(user.pk, True, ['id'])
        year = request.GET.get('year', date.today().year)
        client_logs = PreLetterLog.objects.filter(
            id_agent__in=agents_id, year=year)

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
