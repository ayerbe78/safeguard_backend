from ..imports import *


class ClientLogsView(APIView, AgencyManagement, LimitOffsetPagination):
    permission_classes = [HasClientLogsPermission]

    def get(self, request: APIViewRequest):
        logs = self._get_entries(request)

        logs = self.apply_order_queryset(logs, request, "-added_on")
        page = self.paginate_queryset(logs, request)
        serializer = ClientLogSerilizer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_filters(self, request: APIViewRequest):
        user = request.user
        if not user.is_admin:
            clients = self.get_related_clients(user.pk, True, ("id"))
            client_logs = ClientLog.objects.filter(client__in=clients)
        else:
            client_logs = ClientLog.objects.all()
        client_logs = client_logs.annotate(
            user_name=Concat("user__first_name", V(" "), "user__last_name"),
            user_email=F("user__email"),
            client_name=Concat("client__names", V(" "), "client__lastname"),
        )

        actor = self.check_none(request.query_params.get("actor"))
        if actor:
            client_logs = client_logs.filter(user=actor)

        operation = self.check_none(request.query_params.get("operation"))
        if operation == "insert":
            client_logs = client_logs.filter(type="insert")
        elif operation == "update":
            client_logs = client_logs.filter(type="update")
        elif operation == "delete":
            client_logs = client_logs.filter(type="delete")
        elif operation == "migrate":
            client_logs = client_logs.filter(type="migrate")
        elif operation == "transfer":
            client_logs = client_logs.filter(type="transfer")

        date_start = self.check_none(request.query_params.get("date_start"))
        if date_start:
            date = date_start.replace("/", "-")
            client_logs = client_logs.filter(added_on__gte=date)

        date_end = self.check_none(request.query_params.get("date_end"))
        if date_end:
            date = date_end.replace("/", "-")
            client_logs = client_logs.filter(added_on__lte=date)

        return client_logs

    def __apply_search(self, logs, request: APIViewRequest):
        search = self.check_none(request.query_params.get("search"))
        if search:
            logs = logs.filter(
                Q(user_name__icontains=search)
                | Q(user_email__icontains=search)
                | Q(client_name__icontains=search)
                | Q(client__id__icontains=search)
            )

        return logs

    def _get_entries(self, request: APIViewRequest):
        logs = self.__apply_filters(request)
        logs = self.__apply_search(logs, request)
        return logs


class DataForClientLogs(ClientLogsView):
    permission_classes = [HasClientLogsPermission]

    def get(self, request):
        users = (
            self._get_entries(request)
            .values("user_name", "user_email")
            .annotate(
                id=F("user"),
                count=Count("user"),
            )
            .order_by("user_name")
        )

        return Response(dict(users=users))


class SingleClientLogs(APIView, AgencyManagement, LimitOffsetPagination):
    permission_classes = [HasClientPermission]

    def get(self, request):
        user = request.user
        id_client = request.GET.get('id_client')
        clients = self.get_related_clients(user.pk, True, ["id"])
        clients = self.queryset_to_list(clients, 'id')
        if id_client in clients:
            logs = ClientLog.objects.filter(client=id_client)
            logs = logs.annotate(
                user_name=Concat("user__first_name",
                                 V(" "), "user__last_name"),
                user_email=F("user__email"),
                client_name=Concat("client__names", V(" "),
                                   "client__lastname"),
            )

            logs = self.apply_order_queryset(logs, request, "-added_on")
            page = self.paginate_queryset(logs, request)
            serializer = ClientLogSerilizer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
