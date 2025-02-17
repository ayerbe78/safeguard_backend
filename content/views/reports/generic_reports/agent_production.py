from ...imports import *


class AgentProduction(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasGenericReportsPermission]

    def get(self, request: HttpRequest):
        sql, mapping = self._create_sql(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(mapping, results)
        results = self.paginate_queryset(results, request, view=self)
        response = self.get_paginated_response(results)
        return response

    def _create_sql(self, request: HttpRequest) -> str:
        agency = self.check_none(request.GET.get("agency"), 0)
        state = self.check_none(request.GET.get("state"), 0)
        year = self.check_none(request.GET.get("year"), None)
        if not year:
            raise ValidationException('Missing filters')
        agency_filter, state_filter = '', ''

        if agency:
            agency_filter = f" and a.id_agency={agency} "

        if state:
            state_filter = f" and c.id_state={state} "
        insurances = Insured.objects.all()
        query = "SELECT concat(a.agent_name,' ',a.agent_lastname) as agent_name , COUNT(c.id) AS total_policies, SUM( c.family_menber) as total_members"
        mapping = ['agent_name', 'total_policies', 'total_members']
        for insurance in insurances:
            insurance_name = insurance.names.replace(
                " ", "").replace("\t", "").replace("\n", "")
            query += f"""
                , SUM(case when c.id_insured={insurance.id} then 1 ELSE 0 end) AS {insurance_name}_policies, SUM(case when c.id_insured={insurance.id} then c.family_menber ELSE 0 end) AS {insurance_name}_members
            """
            mapping.append(f"{insurance_name}_Members")
            mapping.append(f"{insurance_name}_Policies")
        query += f"""
            FROM 
                agent a 
                left join client c ON a.id = c.id_agent and 
                c.borrado <> 1 and (tipoclient=1 or tipoclient=3) and YEAR(c.aplication_date)={year}  {state_filter}
            WHERE
                1 {agency_filter}
            GROUP BY a.id
            ORDER BY agent_name
        """
        return query, mapping


class AgentProductionExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, AgentProduction
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgentProductionExcelSerializer
    xlsx_use_labels = True
    filename = "agents_by_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql, mapping = self._create_sql(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(mapping, results)
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)
