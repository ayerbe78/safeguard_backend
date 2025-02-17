from ..imports import *


class SelfManagedAgencyPaymentView(APIView, LimitOffsetPagination, AgencyManagement, DirectSql):
    permission_classes = [HasSelfManagedAgencyPaymentPermission]

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
            "id_agency",
            "agency_name",
            "insured_name",
            "members_number",
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
                id_agency, 
                agency_name, 
                insured_name, 
                SUM(members_number) AS members_number,
                SUM(commission)
                
            FROM 
                self_managed_agency_payment             
            WHERE
                1 {filters}
            GROUP BY
                id_agency
        """
        search = self.check_none(request.GET.get("search"))
        if search:
            search = self.sql_curate_query(search)
            sql += f" and (LOWER(agency_name) like '%{search.lower()}%')"
        return sql

    def __get_filter_query(self, request: APIViewRequest):
        year = self.check_none(
            request.GET.get("year"), date.today().year)
        year = self.sql_curate_query(year)
        query = f" and year={year} "

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            query += f" and id_insured= {insured}"

        agency = self.check_none(request.GET.get("agency"))
        if agency:
            query += f" and id_agency= {agency}"

        month = self.check_none(request.GET.get("month"))
        if month:
            query += f" and month= '{self.inverse_map_month(self.map_month(month))}'"

        return query


class DataForSelfManagedAgencyPayment(APIView, AgencyManagement):
    permission_classes = [HasSelfManagedAgencyPaymentPermission]

    def get(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "agencies", "insurances")
        return Response(selects)


class ExportExcelSelfManagedAgencyPayment(
    XLSXFileMixin, ReadOnlyModelViewSet, SelfManagedAgencyPaymentView
):
    permission_classes = [HasSelfManagedAgencyPaymentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ExportExcelReleseadAgentsSerializer
    xlsx_use_labels = True
    filename = "self_managed_agency_payment.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        if not request.user.is_admin or request.user.has_perm("content.view_self_managed_agency_payment"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        results = self.get_entries(request)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
