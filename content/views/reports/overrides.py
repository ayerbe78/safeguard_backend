from ..imports import *
import re


class OverrideViewSet(APIView, AgencyManagement, LimitOffsetPagination, DirectSql):
    permission_classes = [HasOverridePermission]

    def get(self, request: HttpRequest):
        entries = self._get_entries(request)
        total = 0.0
        for r in entries:
            try:
                total += r.commission
            except:
                pass
        page = self.paginate_queryset(entries, request, view=self)
        if int(request.GET.get('payment', 0)) == 2:
            response = self.get_paginated_response(page)
        else:
            serilizer = OverrideSerializer(page, many=True)
            response = self.get_paginated_response(serilizer.data)
        response.data["total"] = total
        return response

    def _get_entries(self, request):
        payment = self.check_none(request.GET.get("payment"))
        if payment and int(payment) == 2:
            entries = self.__get_no_payment_query(request)
        else:
            entries = self.__apply_filters(request)
            entries = self.__apply_search(entries, request)
            entries = self.apply_order_queryset(
                entries, request, "client_name")

        return entries

    def __get_no_payment_query(self, request: HttpRequest) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        insured = self.check_none(request.GET.get("insured"))
        search = self.check_none(request.GET.get("search"), "")
        insured_filter = f"and c.id_insured={insured}" if insured else ""
        month = self.inverse_map_month(
            self.map_month(request.GET.get("month")))
        user = request.user
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        clients = self.get_related_clients(
            user.pk, True, ["id", "id_agent"], True)

        if agent:
            agents = agents.filter(pk=agent.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        clients = clients.filter(id_agent__in=self.queryset_to_list(agents))

        client_filter = f" AND c.id in ({self.queryset_to_list(clients, to_string=True)})" if not (
            user.is_admin and not (agent or agency)) else ""
        inner_client_filter = f" AND o.id_client in ({self.queryset_to_list(clients, to_string=True)})" if not (
            user.is_admin and not (agent or agency)) else ""

        sql = f"""
            Select
                c.id,
                CONCAT(c.names, " ", c.lastname) AS client_name,
                CONCAT(c.agent_name, " ", c.agent_lastname) AS agent_name,
                i.names as insured_name,
                c.family_menber,
                CASE WHEN fsq.commission IS NOT NULL THEN fsq.commission ELSE 0.0 END AS commission  
            FROM 
                (Select c.id, c.id_agent, c.names,c.lastname, c.family_menber, a.agent_name, a.agent_lastname, c.borrado, c.aplication_date, c.id_insured, c.suscriberid, c.tipoclient from client c left join agent a on c.id_agent = a.id) c
                LEFT JOIN(
                    SELECT *
                    FROM
                        override o
                    WHERE
                        1 AND o.id_insured = 1 AND o.month = '{month}' AND o.year = '{year}' {inner_client_filter}
                    GROUP BY
                        o.suscriberid
                ) fsq ON (c.suscriberid=fsq.suscriberid) 
                
                LEFT JOIN insured i ON c.id_insured = i.id
        
                
            WHERE
                c.borrado <> 1 {client_filter} AND SUBSTRING(c.aplication_date, 1, 4) = '{year}' 
                    AND(fsq.id IS NULL OR fsq.commission = 0) 
                    {insured_filter} AND(c.tipoclient = 1 OR c.tipoclient = 3) AND(
                     LOWER(CONCAT(c.names, ' ', c.lastname)) LIKE '%{search.lower()}%' OR LOWER(c.suscriberid) LIKE '%{search.lower()}%'
                )
            ORDER BY
                client_name,
                agent_name
        """
        results = self.sql_select_all(sql)
        results = self.sql_map_results([
            "id",
            "client_name",
            "agent_name",
            "insured_name",
            "members_number",
            "commission"
        ], results)
        return results

    def __apply_filters(self, request):
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            result = Override.objects.filter(id_insured=insured)
        else:
            result = Override.objects.all()

        month = self.check_none(request.GET.get("month"))
        if month:
            try:
                result = result.filter(
                    month=self.inverse_map_month(self.map_month(int(month))))
            except:
                pass

        year = self.check_none(request.GET.get("year"))
        if year:
            try:
                result = result.filter(year=year)
            except:
                pass

        result = result.exclude(commission=0)

        return result

    def __apply_search(self, queryset, request):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(agent_name__icontains=search) | Q(
                    client_name__icontains=search) | Q(
                    suscriberid__icontains=search)
            )
        return queryset


class DataForOverride(APIView, AgencyManagement):
    permission_classes = [HasOverridePermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "insurances"))


class ExportExcelPaymentAgency(
    XLSXFileMixin, ReadOnlyModelViewSet, OverrideViewSet
):
    permission_classes = [HasExportExcelPaymentAgencyPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = OverrideExcelSerializer
    xlsx_use_labels = True
    filename = "payment_override.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request: APIViewRequest):

        results = self._get_entries(request)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfOverride(OverrideViewSet, PDFCommons):
    permission_classes = [HasExportPDFPaymentAgencyPermission]

    def get(self, request):
        results = self._get_entries(request)
        data = [
            [
                i + 1,
                re.sub(r"\s+", "\n", r.client_name.strip()),
                r.agent_name.strip().replace(" ", "\n", 1),
                r.insured_name,
                r.members_number,
                r.commission,
            ]
            for i, r in enumerate(results)
        ]
        headers = [
            "Indx",
            "Client Name",
            "Agent Name",
            "Insurance",
            "Members",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A1, 'Override Report', True)
