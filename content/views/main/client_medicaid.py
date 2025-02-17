from ..imports import *


class ClientMedicaidView(viewsets.ModelViewSet, AgencyManagement, LimitOffsetPagination):
    permission_classes = [HasClientMedicaidPermission]
    serializer_class = ClientMedicaidSerializer
    queryset = ClientMedicaid.objects.all()

    def filter_query(self, request, clients):
        search = self.check_none(request.query_params.get("search"))
        agent = self.check_none(request.query_params.get("agent"))
        if agent:
            clients = clients.filter(id_agent=agent)
        if search:
            clients = clients.filter(
                Q(name__icontains=search)
                | Q(lastname__icontains=search)
            )
        return clients

    def list(self, request):
        user = request.user
        if user.is_admin or self.is_simple_user(user.pk):
            clients = ClientMedicaid.objects.all()
        else:
            clients = self.get_related_medicaid_clients(user.pk, True)
        filtered_clients = self.filter_query(request, clients)

        page = self.paginate_queryset(filtered_clients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_clients, many=True)
        return Response(serializer.data)


class DataForClientMedicaid(APIView, AgencyManagement):
    permission_classes = [HasClientMedicaidPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "agents", 'status'))
