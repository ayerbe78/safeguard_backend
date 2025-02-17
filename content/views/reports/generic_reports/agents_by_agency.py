from ...imports import *


class AgentsByAgency(
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
        agency_id = self.check_none(request.GET.get("agency"), 0)
        agents = self.get_related_agents(user_id, True)
        query = f"""
            Select 
                concat(a.agent_name,' ',a.agent_lastname) as agent_names,
                a.license_number,
                a.npn,
                a.telephone,
                a.email,
                a.adreess,
                a.date_birth
            from agent a 
            where a.id_agency = {agency_id} 
            and borrado <> 1 
            and a.id in ({self.queryset_to_list(agents, to_string=True)})
            order by agent_names
        """
        return query

    def _get_mapping(self, request: HttpRequest):
        return ["agent_names", "license_number", "npn", "telephone", "email", "adreess", "date_birth"]


class AgentsByAgencyExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, AgentsByAgency
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgentsByAgencyExcelSerializer
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


class AgentsByAgencyExportPdf(AgentsByAgency, PDFCommons):
    permission_classes = [HasExportPDFGenericReportsPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
        agency_id = self.check_none(request.GET.get("agency"), 0)
        agency = Agency.objects.filter(id=agency_id).get()
        data = [
            [
                indx + 1,
                r[0].strip().replace(" ", "\n", 1),
            ]
            + list(r[1:])
            for indx, r in enumerate(results)
        ]

        headers = [
            "Index",
            "Agent Name",
            "License Number",
            "NPN",
            "Telephone",
            "Email",
            "Address",
            "Birthday"
        ]
        return self.pdf_create_table(headers, data, A2, 'Agents in ' + agency.agency_name)
