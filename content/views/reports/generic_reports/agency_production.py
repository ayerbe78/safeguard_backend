from ...imports import *


class AgencyProduction(
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
            agency_filter = f" and ag.id_agency={agency} "

        if state:
            state_filter = f" and c.id_state={state} "
        insurances = Insured.objects.all()
        query = "SELECT ag.agency_name, COUNT(c.id) AS total_policies, SUM( c.family_menber) as total_members"
        mapping = ['agency_name', 'total_policies', 'total_members']
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
                agency ag 
                LEFT JOIN agent a ON ag.id=a.id_agency
                left join client c ON a.id = c.id_agent 
            WHERE c.borrado <> 1 and (tipoclient=1 or tipoclient=3) and YEAR(c.aplication_date)={year} {agency_filter} {state_filter}
            GROUP BY ag.id
            ORDER BY ag.agency_name
        """
        return query, mapping


class AgencyProductionExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, AgencyProduction
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgencyProductionExcelSerializer
    xlsx_use_labels = True
    filename = "agents_by_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql, mapping = self._create_sql(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(mapping, results)
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)
