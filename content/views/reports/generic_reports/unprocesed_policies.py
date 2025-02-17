from ...imports import *


class UnprocesedPolicies(
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
        month = self.check_none(request.GET.get("month"))
        year = self.check_none(request.GET.get("year"))
        insured = self.check_none(request.GET.get("insured"))
        if not month or not year:
            raise ValidationException('Missing Filters')
        parsed_month = self.inverse_map_month(self.map_month(month))
        info_month = f'{month}/1/{year}'
        insured_filter = ''
        if insured:
            insured_filter = f"AND id_insured={insured}"
        query = f"""
            SELECT
                pg.c_name,
                pg.agent_name,
                pg.p_number,
                pg.n_member,
                i.names,
                pg.info_month,
                pg.commission
            FROM
                (
                SELECT
                    p_number,
                    c_name,
                    n_member,
                    id_insured,
                    commission,
                    info_month,
                    a.agent_name
                FROM
                    payments_global
                    LEFT JOIN 
                        (Select concat(agent_name,' ',agent_lastname) as agent_name,npn from agent where borrado <>1 group by npn) a  
                    ON a_number =a.npn
                WHERE
                    MONTH = '{parsed_month}' AND pyear = {year}  {insured_filter}
                GROUP BY
                    p_number, info_month
            ) pg
            LEFT JOIN(
                SELECT
                    suscriberid, info_month
                FROM
                    agent_payments
                WHERE
                    MONTH = '{parsed_month}' AND YEAR = {year}  {insured_filter}
                GROUP BY
                    suscriberid, info_month
            ) ap
            ON
                (pg.p_number = ap.suscriberid and pg.info_month = ap.info_month)
            JOIN insured i ON
                pg.id_insured = i.id
            WHERE
                ap.suscriberid IS NULL
            ORDER BY
                pg.c_name
        """
        return query

    def _get_mapping(self, request: HttpRequest):
        return ["client_name", 'agent_name', "suscriberid", "members_number", "insured", 'info_month', 'commission']


class UnprocesedPoliciesExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, UnprocesedPolicies
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = UnprocesedPoliciesExcelSerializer
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


class UnprocesedPoliciesExportPdf(UnprocesedPolicies, PDFCommons):
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
            "Client",
            "Agent",
            "Subscriber ID",
            "Members Count",
            "Insurance",
            "Paid Month",
            "Commission",
        ]
        return self.pdf_create_table(headers, data, A2, 'Unprocesed Policies', True)
