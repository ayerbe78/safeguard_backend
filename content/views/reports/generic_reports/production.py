from ...imports import *


class Production(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasGenericReportsPermission]

    def get(self, request: HttpRequest):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)
        results = self.paginate_queryset(results, request, view=self)
        response = self.get_paginated_response(results)
        return response

    def _create_sql(self, request: HttpRequest) -> str:
        user_id = request.user.pk
        agency = self.check_none(request.GET.get("agency"), 0)
        insured = self.check_none(request.GET.get("insured"), 0)
        agent = self.check_none(request.GET.get("agent"), 0)
        assistant = self.check_none(request.GET.get("assistant"), 0)
        state = self.check_none(request.GET.get("state"), 0)
        group_by = self.check_none(request.GET.get("group_by"), "State")
        year = self.check_none(request.GET.get("year"), None)
        if not year:
            raise ValidationException('Missing filters')

        agency_filter, insured_filter, agent_filter, state_filter = '', '', '', ''

        if group_by == "State":
            group_by_query = " c.id_state order by s.names"
            selected_field_name = "s.names"
        elif group_by == "Insurance":
            group_by_query = " c.id_insured order by i.names"
            selected_field_name = "i.names"
        elif group_by == "Agent":
            group_by_query = " c.id_agent order by a.agent_name"
            selected_field_name = "CONCAT(a.agent_name,' ', a.agent_lastname)"

        if agency:
            agency_filter = f" and a.id_agency={agency} "
        if insured:
            insured_filter = f" and c.id_insured={insured} "
        if assistant:
            assistant = Assistant.objects.filter(id=assistant)
            if len(assistant) == 1:
                assistant = assistant.get()
                assistant_user = CustomUser.objects.filter(
                    email=assistant.email)
                if len(assistant_user) == 1:
                    assistant_user = assistant_user.get()
                    clients = self.get_related_clients(assistant_user.id)
                    clients = self.queryset_to_list(clients, 'id', True)
            agents = self.get_related_agents(user_id, False)
            agents = agents.filter(id_assistant=assistant.id)
            agents = self.queryset_to_list(agents, 'id', True)
            agent_filter = f" and c.id_agent in ({agents}) and c.id in ({clients}) "

        if agent and self.select_agent(agent, user_id):
            agent_filter = f" and c.id_agent={agent} "
        if state:
            state_filter = f" and c.id_state={state} "

        query = f"""
            Select  count(c.id) as policies, {selected_field_name}
            from client c
                join state s on c.id_state=s.id
                join agent a on c.id_agent=a.id
                join insured i on c.id_insured=i.id
            where 
            c.borrado <> 1 and (tipoclient=1 or tipoclient=3) and YEAR(c.aplication_date)='{year}'  
            {agency_filter}  {insured_filter} {agent_filter}  {state_filter}
            group by {group_by_query}
        """
        return query

    def _get_mapping(self, request: HttpRequest):
        return ["policies", "selected_field_name"]


class ProductionExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, Production
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ProductionExcelSerializer
    xlsx_use_labels = True
    filename = "agents_by_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ProductionExportPdf(Production, PDFCommons):
    permission_classes = [HasExportPDFGenericReportsPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
        data = [
            [
                indx + 1,
                r[1],
                r[0],
            ]
            for indx, r in enumerate(results)
        ]

        headers = [
            "Index",
            "Name",
            "Policies"
        ]
        return self.pdf_create_table(headers, data, A4, 'Production')
