from ..imports import *


class ReleseadAgentsReport(APIView, LimitOffsetPagination, AgencyManagement, DirectSql):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: APIViewRequest):
        if not request.user.is_admin or request.user.has_perm("content.view_releasedagents"):
            return Response(status=status.HTTP_403_FORBIDDEN)
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
            "npn",
            "policies",
            "members",
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
                    a.id, CONCAT(a.agent_name,' ', a.agent_lastname) agent_name, a.npn, p.policies, p.members, p.commission
                FROM agent a
                        LEFT JOIN 
                        (SELECT 
                            a_number, COUNT(id) AS policies, SUM(n_member) AS members, SUM(commission) AS commission
                        FROM payments_global 
                        WHERE 1 {filters}
                        GROUP BY a_number
                        ) p ON a.npn = p.a_number
                        
                WHERE a.released=1
        """
        search = self.check_none(request.GET.get("search"))
        if search:
            search = self.sql_curate_query(search)
            sql += f" and (LOWER(agent_name) like '%{search.lower()}%')"
        return sql

    def __get_filter_query(self, request: APIViewRequest):
        year = self.check_none(
            request.GET.get("year"), date.today().year)
        year = self.sql_curate_query(year)
        query = f" and pyear={year} "

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            query += f" and id_insured= {insured}"

        month = self.check_none(request.GET.get("month"))
        if month:
            query += f" and month= {self.inverse_map_month(self.map_month(month))}"

        return query


class DataForReleseadAgentsReport(APIView, AgencyManagement):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin or request.user.has_perm("content.view_releasedagents"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = request.user
        selects = self.get_selects(user.pk, "insurances")
        return Response(selects)


class ExportExcelReleseadAgentsReport(
    XLSXFileMixin, ReadOnlyModelViewSet, ReleseadAgentsReport
):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ExportExcelReleseadAgentsSerializer
    xlsx_use_labels = True
    filename = "released_agents.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        if not request.user.is_admin or request.user.has_perm("content.view_releasedagents"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        results = self.get_entries(request)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
