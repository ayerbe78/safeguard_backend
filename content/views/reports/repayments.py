from ..imports import *


class RepaymentsReport(APIView, LimitOffsetPagination, AgencyManagement, DirectSql):
    permission_classes = [HasRepaymentsReportPermission]

    def get(self, request: APIViewRequest):
        entries = self.get_entries(request)
        page = self.paginate_queryset(entries, request, view=self)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(entries)

    def get_entries(self, request):
        query = self.__get_query(request)
        maps = [
            "id",
            "agent_name",
            "client_name",
            "id_agent",
            "id_client",
            "year",
            "info_month",
            "id_insured",
            "insured_name",
            "suscriberid",
            "members_number",
            "created_at",
            "commission"
        ]
        result = self.sql_select_all(query, maps)
        return result

    def __get_query(self, request: APIViewRequest):
        return self.__get_base_query(request) + self.apply_order_sql(
            request, "agent_name"
        )

    def __get_base_query(self, request: APIViewRequest):
        filters = self.__get_filter_query(request)

        sql = f"""
                SELECT 
                    id,
                    agent_name,
                    client_name,
                    id_agent,
                    id_client,
                    year,
                    info_month,
                    id_insured,
                    insured_name,
                    suscriberid,
                    members_number,
                    DATE(created_at),
                    commission
                FROM `repayments` 
                    
                WHERE 1 {filters}
        """

        return sql

    def __get_filter_query(self, request: APIViewRequest):
        year = self.check_none(
            request.GET.get("year"), date.today().year)
        year = self.sql_curate_query(year)
        query = f" and year={year} "

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            query += f" and id_insured= {insured}"

        agent = self.check_none(request.GET.get("agent"))
        if agent:
            query += f" and id_agent= {agent}"

        # procesed = self.check_none(request.GET.get("procesed"))
        # if procesed == '1':
        #     query += f" and procesed=1 "
        # else:
        #     query += f" and (procesed is null or procesed=0) "

        search = self.check_none(request.GET.get("search"))
        if search:
            search = self.sql_curate_query(search)
            query += f" and (LOWER(agent_name) like '%{search.lower()}%' or LOWER(client_name) like '%{search.lower()}%' or LOWER(suscriberid) like '%{search.lower()}%')"

        return query


class DataForRepaymentsReport(APIView, AgencyManagement):
    permission_classes = [HasRepaymentsReportPermission]

    def get(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "agents", "insurances")
        return Response(selects)


class ExportExcelRepaymentsReport(
    XLSXFileMixin, ReadOnlyModelViewSet, RepaymentsReport
):
    permission_classes = [HasExportExcelPaymentClientPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ExportExcelRepaymentSerializer
    xlsx_use_labels = True
    filename = "repayments.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        results = self.get_entries(request)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
