from ...imports import *


class UnAssignedPaymentsView(
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
        if not month or not year or not insured:
            raise ValidationException('Missing Filters')
        parsed_month = self.inverse_map_month(self.map_month(month))

        query = f"""
            SELECT
                client_name,
                agent_name,
                npn,
                state_initials,
                effective_date,
                suscriberid,
                new_ren,
                info_month,
                members,
                commission
            FROM
                unassigned_payments
            WHERE
                month = '{parsed_month}' AND year = {year}  AND id_insured={insured}
        """
        return query

    def _get_mapping(self, request: HttpRequest):
        return ["client_name", 'agent_name', "npn", "state_initials", "effective_date", "suscriberid", 'new_ren', 'info_month', "members", "commission"]


class UnAssignedPaymentsViewExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, UnAssignedPaymentsView
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = UnAssignedPaymentsExcelSerializer
    xlsx_use_labels = True
    filename = "unassigned_payments.xlsx"
    xlsx_ignore_headers = ["id", "id_insured", "month", "year", "created_at"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class UnAssignedPaymentsViewExportPdf(UnAssignedPaymentsView, PDFCommons):
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
            'Agent', "NPN", "State", "Effective Date", "Subscriber ID", 'Type', 'Paid Month', "Members", "Commission"
        ]
        return self.pdf_create_table(headers, data, A1, 'Unprocesed Policies', True)
