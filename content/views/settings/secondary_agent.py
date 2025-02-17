from ..imports import *


class SecondaryAgentViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasSecondaryAgentPermission]
    serializer_class = SecondaryAgentSerializer
    queryset = Agent.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        if self.current_is('agent', user.pk):
            agent = Agent.objects.filter(email=user.email)
            if len(agent) == 1:
                agent = agent.get()
                entries = Agent.objects.filter(secondary_agent=True, exclusive_secondary_agent=True, id_agency=agent.id_agency) | Agent.objects.filter(
                    secondary_agent=True).exclude(exclusive_secondary_agent=True)
                entries = entries.exclude(
                    borrado=1).order_by("agent_name")
        else:
            entries = Agent.objects.filter(secondary_agent=True).exclude(
                borrado=1).order_by("agent_name")

        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "agent_name")

        page = self.paginate_queryset(entries)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(agent_name__icontains=search) | queryset.filter(
                agent_lastname__icontains=search)
        return queryset

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_secondary_agent(self, request: HttpRequest):
        selects = self.get_selects(request.user.pk, "agents")
        return Response(selects)
