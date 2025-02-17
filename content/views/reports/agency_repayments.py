from ..imports import *


class AgencyRepaymentsReport(APIView, LimitOffsetPagination, AgencyManagement, DirectSql):
    permission_classes = [HasAgencyRepaymentsReportPermission]

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
            "agency_name",
            "agent_name",
            "client_name",
            "id_agent",
            "id_client",
            "year",
            "info_month",
            "id_insured",
            "insured_name",
            "members_number",
            "created_at",
            "total_commission"
        ]
        result = self.sql_select_all(query, maps)
        return result

    def __get_query(self, request: APIViewRequest):
        return self.__get_base_query(request) + self.apply_order_sql(
            request, "agency_name"
        )

    def __get_base_query(self, request: APIViewRequest):
        filters = self.__get_filter_query(request)

        sql = f"""
                SELECT 
                    ar.id,
                    ag.agency_name,
                    CONCAT(a.agent_name,' ', a.agent_lastname) as agent_name,
                    CONCAT(c.names,' ', c.lastname) as client_name,
                    ar.id_agent,
                    ar.id_client,
                    ar.year,
                    ar.info_month,
                    ar.id_insured,
                    i.names,
                    ar.members_number,
                    DATE(ar.created_at),
                    ar.total_commission
                FROM `agency_repayment` ar 
                left join agent a on (ar.id_agent=  a.id)
                left join client c on (ar.id_client=  c.id)
                left join insured i on (ar.id_insured=  i.id)
                left join agency ag on (ar.id_agency=  ag.id)
                    
                WHERE 1 {filters}
        """

        return sql

    def __get_filter_query(self, request: APIViewRequest):
        year = self.check_none(
            request.GET.get("year"), date.today().year)
        year = self.sql_curate_query(year)
        query = f" and ar.year={year} "

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            query += f" and ar.id_insured= {insured}"

        agency = self.check_none(request.GET.get("agency"))
        if agency:
            query += f" and ar.id_agency= {agency}"

        agent = self.check_none(request.GET.get("agent"))
        if agent:
            query += f" and ar.id_agent= {agent}"

        # procesed = self.check_none(request.GET.get("procesed"))
        # if procesed == '1':
        #     query += f" and procesed=1 "
        # else:
        #     query += f" and (procesed is null or procesed=0) "

        search = self.check_none(request.GET.get("search"))
        if search:
            search = self.sql_curate_query(search)
            query += f" and (LOWER(agent_name) like '%{search.lower()}%' or LOWER(client_name) like '%{search.lower()}%' )"

        return query


class DataForAgencyRepaymentsReport(APIView, AgencyManagement):
    permission_classes = [HasAgencyRepaymentsReportPermission]

    def get(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "agents", "insurances", "agencies")
        return Response(selects)


class ExportExcelAgencyRepaymentsReport(
    XLSXFileMixin, ReadOnlyModelViewSet, AgencyRepaymentsReport
):
    permission_classes = [HasExportExcelPaymentClientPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ExportExcelAgencyRepaymentSerializer
    xlsx_use_labels = True
    filename = "repayments.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        results = self.get_entries(request)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
