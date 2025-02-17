from ..imports import *


class PendingDocumentsViewSet(
    viewsets.ModelViewSet, AgencyManagement, LimitOffsetPagination
):
    permission_classes = [HasPendindDocumentsPermission]
    serializer_class = PendingDocumentsSerializer
    queryset = PendingDocuments.objects.all()

    def list(self, request: HttpRequest):

        docs, clients = self.__apply_filters(request)
        types = TypePendingdoc.objects.all()

        result = docs.values()
        for d in result:
            client = clients.get(id=d["id_client"])
            try:
                doc_type = types.get(id=d["id_tipopendoc"])
            except:
                doc_type = None
            d["client"] = f"{client.names} {client.lastname}"
            d["type"] = doc_type.names if doc_type else None
            d["id_agent"] = client.id_agent
            d["id_client"] = client.id
            d["client_phone"] = client.telephone
            d["client_email"] = client.email
        result = self.apply_order_dict_list(result, request, "client")

        page = self.paginate_queryset(result)
        return self.get_paginated_response(page)

    def __apply_filters(self, request):
        user: CustomUser = request.user
        agent = self.select_agent(request.GET.get("agent"), user.pk)

        if agent:
            clients = self.get_related_clients(
                user.pk, True).filter(id_agent=agent.pk)
            clients |= self.get_related_applications(user.pk, True).filter(
                id_agent=agent.pk
            )
        else:
            clients = self.get_related_clients(user.pk, True)
            clients |= self.get_related_applications(user.pk, True)

        clients = clients.annotate(
            client_full_name=Concat("names", V(" "), "lastname"))
        search = self.check_none(request.GET.get("search"), "")
        clients = clients.filter(client_full_name__icontains=search)

        year = self.check_none(request.GET.get("year"), date.today().year)
        a = date(int(year), 1, 1)
        b = date(int(year) + 1, 1, 1)
        docs = PendingDocuments.objects.filter(
            id_client__in=self.queryset_to_list(clients),
            end_date__range=[a, b],
        )
        # .filter(
        #     Q(nota__icontains=search)
        #     | Q(upload_date__icontains=search)
        #     | Q(end_date__icontains=search)
        # )

        doc_type = self.check_none(request.GET.get("type"))
        if doc_type:
            docs = docs.filter(id_tipopendoc=doc_type)

        return docs, clients

    @action(methods=["get"], detail=False, url_path="data")
    def data_for(self, request):
        selects = self.get_selects(request.user.pk, "agents")
        doc_types = TypePendingdoc.objects.all().order_by("names").values()
        selects.update({"doc_types": doc_types})
        return Response(selects)


class PendingDocsDashboardSummary(APIView, AgencyManagement, DashboardCommons):
    def get(self, request: HttpRequest):
        user_id = self.dash_get_alternative_user(request)
        clients = self.get_related_clients(user_id, True)
        clients |= self.get_related_applications(user_id, True)
        x = date.today()
        a = date(x.year, 1, 1)
        b = date(x.year + 1, 1, 1)
        docs = PendingDocuments.objects.filter(
            id_client__in=self.queryset_to_list(clients), end_date__range=[a, b]
        )
        return Response({"count": docs.count()})
