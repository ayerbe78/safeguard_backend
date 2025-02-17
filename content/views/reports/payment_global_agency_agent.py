from ..imports import *


class PaymentGlobalAgencyAgent(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasPaymentAgencyAgentPermission]

    def get(self, request: HttpRequest):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)
        results = self.paginate_queryset(results, request, view=self)
        response = self.get_paginated_response(results)
        return response

    def _get_mapping(self, request: HttpRequest):
        return [
            "id",
            "agency_name",
            "year",
            "month",
            "members",
            "commission",
        ]

    def _create_sql(self, request: HttpRequest) -> str:
        query = (
            self.__get_basic_query(request)
            + self.__get_subquery(request)
            + self.apply_filters(request)
            + self.__apply_ordering(request)
        )
        return query

    def __get_basic_query(self, request: HttpRequest) -> str:
        month = self.map_month(request.GET.get("month")).replace(
            "dicember", "december").capitalize()
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        basic_query = f"""
                        Select 
                            a.id,
                            a.agency_name,
                            {year} as year,
                            '{month}' as month,
                            p.members,
                            p.commission
                    """
        return basic_query

    def __get_subquery(self, request) -> str:
        filters = ""

        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        insured = self.check_none(request.GET.get("insured"))

        month = self.map_month(request.GET.get("month"))
        if insured:
            filters += f" and ap.id_insured = {self.sql_curate_query(str(insured))} "

        sql = f"""
            FROM 
            agency a
            left join
            (
                Select 
                    ag.id_agency,
                    ap.month,
                    sum(ap.members_number) as members,
                    sum(ap.commission) as commission
                    
                FROM
                    agent ag
                    left join agent_payments ap on(ag.id=ap.id_agent)
                WHERE
                    ap.year='{year}' and ap.month='{self.inverse_map_month(month)}' {filters}
                GROUP BY
                    ag.id_agency, ap.month
            ) p
            on (a.id=p.id_agency)
        
        """

        return sql

    def get_sq_filters(self, request: HttpRequest) -> str:
        filters = "WHERE 1 "
        search = self.check_none(request.GET.get("search"))
        agency = self.check_none(request.GET.get("agency"))

        if agency:
            filters += f"and a.id = {self.sql_curate_query(str(agency))} "
        if search:
            filters += f"and LOWER(a.agency_name) like  '%{search.lower()}%'"

        return filters

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "a.agency_name"
    ) -> str:
        order = ""
        default = f" order by {default_order}"
        order_field = self.check_none(request.GET.get("order"))
        desc = self.check_none(request.GET.get("desc"))

        if order_field and order_field in self._get_mapping(request):
            order = f" order by {self.sql_curate_query(order_field)}"
        else:
            order = default
        if desc:
            order += " desc"
        order += f",{default_order}"

        return order

    def apply_filters(self, request: HttpRequest):
        sq_filters = self.get_sq_filters(request)
        payment = self.check_none(request.GET.get("payment"))
        if payment and int(payment) == 1:
            sq_filters += f" and p.commission<>0 "
        elif payment and int(payment) == 2:
            sq_filters += f" and p.commission is NULL or  p.commission =0 "
        return sq_filters


class ExportExcelPaymentGlobalAgencyAgent(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalAgencyAgent
):
    permission_classes = [HasExportExcelPaymentAgencyAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentGlobalAgencyAgentSerializer
    xlsx_use_labels = True
    filename = "payment_global_agency_agent.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGlobalAgencyAgent(PaymentGlobalAgencyAgent, PDFCommons):
    permission_classes = [HasExportAgencyAgentPaymentPDFPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)

        month = self.map_month(request.GET.get("month"))
        data = [[indx + 1] + list(r[1:]) for indx, r in enumerate(results)]

        month_name = month.replace(
            "dicember", "december").capitalize()

        headers = [
            "Index",
            "Agency",
            "Year",
            "Month",
            "Paid Members",
            "Commission",
        ]
        return self.pdf_create_table(headers, data, A3, f'Payment Global Agency Agent Report / {month_name}', True)


class AgencyAgentPaymentsDetailsByInsurance(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentAgencyAgentPermission]

    def get(self, request: HttpRequest):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(self._get_mapping(request), results)
        return Response(results)

    def _create_sql(self, request):
        month = request.GET.get("month")
        month = self.inverse_map_month(month.lower().replace(
            "december", "dicember"))
        id_agency = request.GET.get("agency")
        year = self.check_none(request.GET.get(
            "year"), str(date.today().year))

        sql = f"""
            SELECT
                p.id_insured,
                p.insured_name,
                p.commission
            FROM
                agency a
            LEFT JOIN(
                SELECT ag.id_agency,
                    ap.id_insured,
                    ap.insured_name,
                    SUM(ap.commission) AS commission
                FROM
                    agent ag
                LEFT JOIN agent_payments ap ON
                    (ag.id = ap.id_agent)
                WHERE
                    ap.year = '{year}' AND ap.month = '{month}'
                GROUP BY
                    ag.id_agency,
                    ap.month,
                    ap.id_insured
            ) p ON (a.id = p.id_agency)
            
            WHERE a.id={id_agency}
            ORDER BY 
                p.commission DESC
        """
        return sql

    def _get_mapping(self, request):
        return ['id_insured', 'insured_name', 'commission']


class ExportExcelAgencyAgentPaymentsDetailsByInsurance(
    XLSXFileMixin, ReadOnlyModelViewSet, AgencyAgentPaymentsDetailsByInsurance
):
    permission_classes = [HasExportExcelPaymentAgencyAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgentPaymentsDetailsByInsuranceSerializer
    xlsx_use_labels = True
    filename = "payment_global_agency_agent.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfAgencyAgentPaymentsDetailsByInsurance(AgencyAgentPaymentsDetailsByInsurance, PDFCommons):
    permission_classes = [HasExportAgencyAgentPaymentPDFPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
        agency = self.select_agency(request.GET.get('agency'), request.user.pk)
        month = request.GET.get("month")
        data = [[indx + 1] + list(r[1:]) for indx, r in enumerate(results)]

        month_name = month.replace(
            "dicember", "december").capitalize()
        headers = [
            "Index",
            "Insurance",
            "Commission"
        ]
        return self.pdf_create_table(headers, data, A4, f"{agency.agency_name}/ {month_name}", True)
