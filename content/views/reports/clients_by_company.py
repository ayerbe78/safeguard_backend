from ..imports import *


class FilterClientCompany(APIView, LimitOffsetPagination, AgencyManagement, DirectSql):
    permission_classes = [HasClientByCompanyPermission]

    def get(self, request: APIViewRequest):
        user: CustomUser = request.user
        self.check_permission(user, "content.view_clientbycompanies")
        entries, mapping = self.get_query(request)
        entries = self.sql_select_all(entries, mapping)
        page = self.paginate_queryset(entries, request, view=self)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(entries)

    def get_mapping(self):
        return ["id", "Agent Name", "NPN"]

    def get_query(self, request: APIViewRequest):

        year = self.check_none(
            request.query_params.get("year"), date.today().year)
        year = self.sql_curate_query(year)
        select_part, join_part, mapping = self.__get_subquery(request)
        filters = self.__get_filter_query(request)

        sql = (
            f"select a.id, CONCAT(a.agent_name,' ', a.agent_lastname) as agent_name, a.npn {select_part} from agent a {join_part} {filters}")
        return sql, mapping

    def __get_subquery(self, request):
        year = self.check_none(
            request.query_params.get("year"), date.today().year)
        year = self.sql_curate_query(year)

        user = request.user
        # agent = self.select_agent(request.query_params.get("agent"), user.pk)
        # if agent:
        #     agents = self.get_related_agents(
        #         user.pk, True, ["id"]).filter(id=agent.pk)
        # else:
        #     agents = self.get_related_agents(user.pk, True, ["id"])

        insurances = self.check_none(
            request.query_params.get("insurances"), "")
        insurances = insurances.split(',')
        select_part = ""
        join_part = ""
        mapping = self.get_mapping()
        for insured in insurances:
            insurance = Insured.objects.filter(id=insured).get()
            insurance_name = insurance.names.replace(
                " ", "").replace("\t", "").replace("\n", "")
            select_part += f" , {insurance_name}.members as {insurance_name}_members, {insurance_name}.policies as {insurance_name}_policies "
            join_part += f""" 
                left join (
                    Select id_agent, sum(family_menber) members, count(id) policies
                    FROM client
                    WHERE borrado <> 1 and tipoclient <> 2 and tipoclient <> 4 and YEAR(aplication_date)='{year}'
                    and id_insured={insured}
                    group by id_agent 
                ) {insurance_name}
                on (a.id={insurance_name}.id_agent) 

            """
            mapping.append(f"{insurance.names} Members")
            mapping.append(f"{insurance.names} Policies")
        return select_part, join_part, mapping

    def __get_filter_query(self, request: APIViewRequest):
        query = ""

        search = self.check_none(request.query_params.get("search"))
        if search:
            search = self.sql_curate_query(search)
            query += f""" where (CONCAT_WS(' ',a.agent_name, a.agent_lastname) like '%{search}%'
                        or a.npn like '%{search}%') """

        order_by = request.GET.get('order').split()
        desc = self.sql_curate_query(request.GET.get('desc'))
        if order_by:
            query += f"Order By {order_by[0]}_{order_by[1].lower()} {'DESC' if int(desc)  else ''}, agent_name"
        else:
            query += "Order By agent_name"
        return query


class FilterClientCompanyExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, FilterClientCompany
):
    permission_classes = [HasExportExcelClientByCompaniesPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ClientByCompaniesSerializer
    xlsx_use_labels = True
    filename = "agents_by_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        entries, mapping = self.get_query(request)
        mapping = ["id", "agent_name", 'npn', 'members', 'policies']
        entries = self.sql_select_all(entries, mapping)

        serializer = self.get_serializer(entries, many=True)

        return Response(serializer.data)


class ClientsByCompaniesExportPdf(FilterClientCompany, PDFCommons):
    permission_classes = [HasExportPDFClientsByCompaniesPermission]

    def get(self, request):
        entries, mapping = self.get_query(request)
        entries = self.sql_select_all(entries)
        data = [
            [
                indx + 1,
                r[1].strip().replace(" ", "\n", 1),
                r[2],
                r[3],
                r[4]
            ]
            for indx, r in enumerate(entries)
        ]
        headers = [
            "Index",
            "Agent Name",
            "NPN",
            "Members",
            "Policies"
        ]
        return self.pdf_create_table(headers, data, A3, 'Clients By Company')


class DataForClientByCompanies(APIView, AgencyManagement):
    permission_classes = [HasClientByCompanyPermission]

    def get(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "agents", "insurances")
        return Response(selects)
