from ..imports import *


class BobGlobalSerializerExtended(serializers.ModelSerializer):
    client_full_name = serializers.CharField()

    class Meta:
        fields = "__all__"
        model = BobGlobal


class BobGlobalViewSet(viewsets.ReadOnlyModelViewSet, AgencyManagement, DirectSql):
    permission_classes = [HasBobGlobalPermission]
    serializer_class = BobGlobalSerializer

    def get_queryset(self):
        today = date.today()
        return BobGlobal.objects.filter(effective_date__year=today.year)

    def list(self, request, *args, **kwargs):
        bobs = BobGlobal.objects.all()
        bobs = self.__apply_filters(bobs, request)
        bobs = self.__apply_search(bobs, request)
        bobs = self.apply_order_queryset(bobs, request, "agent_name")

        results = self.paginate_queryset(bobs)
        serializer = BobGlobalSerializerExtended(results, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_filters(self, queryset, request):
        user: CustomUser = request.user
        agent_filter = self.check_none(request.GET.get("agent"))
        agent = self.current_is('agent', user.pk)
        if agent or agent_filter:
            queryset = queryset.filter(
                agent_npn=Agent.objects.get(id=agent if agent else agent_filter).npn)
        year = self.check_none(request.GET.get("year"))
        if year:
            queryset = queryset.filter(effective_date__year=year)
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            queryset = queryset.filter(id_insured=insured)
        policy = self.check_none(request.GET.get("status"))
        if policy:
            queryset = queryset.filter(policy_status=policy)

        return queryset.annotate(
            client_full_name=Concat("client_name", V(" "), "client_lastname")
        )

    def __apply_search(self, queryset, request: APIViewRequest):
        search = self.check_none(request.query_params.get("search"))
        if search:
            queryset = queryset.filter(
                Q(agent_name__icontains=search)
                | Q(client_full_name__icontains=search)
                | Q(suscriberid__icontains=search)
                | Q(phone_number__icontains=search)
            )
        return queryset

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_bob(self, request: HttpRequest):
        user = request.user
        selects = self.get_selects(user.pk, "insurances", "agents")
        return Response(selects)

    @action(methods=["get"], detail=False, url_path="lite")
    def lite_info(self, request: APIViewRequest):
        user: CustomUser = request.user
        year = self.check_none(
            request.query_params.get("year"), date.today().year)
        year = self.sql_curate_query(year)
        insurance = self.check_none(request.query_params.get("insured"), 0)
        insurance = self.sql_curate_query(insurance)
        option = self.check_none(request.query_params.get("option"), "cancel")

        clients = self.get_related_clients(user.pk, True)
        clients_ids = self.queryset_to_list(clients, to_string=True)

        if option == "late":
            filters = "b.paid_date < CURDATE() and b.paid_date > '1980-01-02'"
        elif option == "no":
            filters = "b.eleg_commision = 'No'"
        else:
            filters = "b.term_date <= CURDATE()"

        sql = f"""SELECT insured.names as insured, agent_name,
            concat(client_name,' ',client_lastname) as client,
            b.suscriberid,b.num_members,b.pol_hold_state,b.eleg_commision,
            b.pol_rec_date,b.effective_date,b.paid_date,b.term_date
            FROM bob_global b INNER JOIN client on client.suscriberid = 
            b.suscriberid join insured on b.id_insured
            = insured.id where client.id in ({clients_ids}) 
            {f'and client.id_insured = {insurance} and b.id_insured = {insurance}' if int(insurance) != 0 else ''}
            and SUBSTRING(aplication_date,1,4) = '{year}' and {filters}
            """

        result = self.sql_select_all(
            sql,
            (
                "insured",
                "agent_name",
                "client",
                "suscriberid",
                "num_members",
                "pol_hold_state",
                "eleg_commision",
                "pol_rec_date",
                "effective_date",
                "paid_date",
                "term_date",
            ),
        )

        page = self.paginate_queryset(result)
        return self.get_paginated_response(page)
