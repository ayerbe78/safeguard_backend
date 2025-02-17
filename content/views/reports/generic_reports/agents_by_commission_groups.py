from ...imports import *


class AgentsByCommissionGroup(
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
        commission_group = self.check_none(request.GET.get("commission_group"))
        query = f"""
            SELECT
               CONCAT(agent_name,' ', agent_lastname) as agent_name,
               npn,
               telephone,
               email
            FROM
                agent
            
            WHERE id_commission_group={commission_group}
            
            ORDER BY
                agent_name
        """
        return query

    def _get_mapping(self, request: HttpRequest):
        return ['agent_name', "npn", "telephone", "email"]


class AgentsByCommissionGroupExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, AgentsByCommissionGroup
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgentsByCommissionGroupExcelSerializer
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


class AgentsByCommissionGroupExportPdf(AgentsByCommissionGroup, PDFCommons):
    permission_classes = [HasExportPDFGenericReportsPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
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
            "Agent",
            "NPN",
            "Telephone",
            "Email"
        ]
        return self.pdf_create_table(headers, data, A3, 'Agents')
