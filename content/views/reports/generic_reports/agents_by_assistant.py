from ...imports import *
from django.utils.translation import gettext_lazy as _


class AgentsByAssistant(
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
        assistant = self.check_none(request.GET.get("assistant"), None)
        if not assistant:
            raise ValidationException("Missing Filters")
        date_start = self.check_none(request.GET.get("date_start"), None)
        date_end = self.check_none(request.GET.get("date_end"), None)

        year = date.today()
        year = year.year
        date_filter = ""
        if date_start and date_end:
            date_start = datetime.strptime(
                date_start, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = datetime.strptime(
                date_end, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=23, minute=59, second=59, microsecond=999999)
            date_filter = f" AND (a.date_start>'{date_start}' AND a.date_start<'{date_end}' )"

        query = f"""
            SELECT 
                CONCAT(a.agent_name," ", a.agent_lastname) AS fullname,
                a.date_start,
                a.npn,
                COUNT(c.id) AS policies,
                SUM(c.family_menber) AS members

            FROM 
                agent a 
                LEFT JOIN client c ON a.id=c.id_agent and YEAR(c.aplication_date)={year} AND c.borrado<>1 AND (c.tipoclient=1 OR c.tipoclient=3)
            WHERE
                a.borrado<>1  AND a.id_assistant={assistant}
                {date_filter}
            GROUP BY a.id
            ORDER BY fullname
        """
        return query

    def _get_mapping(self, request: HttpRequest):
        return ["agent_name", "date_start", "npn", "policies", "members"]


class AgentsByAssistantExcelSerializer(serializers.Serializer):
    agent_name = serializers.CharField(label=_("Agent"))
    date_start = serializers.CharField(label=_("Date Start"))
    npn = serializers.CharField(label=_("NPN"))
    policies = serializers.CharField(label=_("Policies"))
    members = serializers.CharField(label=_("Members"))


class AgentsByAssistantExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, AgentsByAssistant
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgentsByAssistantExcelSerializer
    xlsx_use_labels = True
    filename = "agents_by_assistant.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class AgentsByAssistantExportPdf(AgentsByAssistant, PDFCommons):
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
            "Date Start",
            "NPN",
            "Policies",
            "Members",
        ]
        return self.pdf_create_table(headers, data, A2, "Agents by Assistant")
