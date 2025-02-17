from ..imports import *


class PaymentGLobalOnlyCommons(AgencyManagement, DirectSql):
    def get_entries(self, request):
        query = self.__get_full_query(request)
        entries = self.sql_select_all(query)

        return entries

    def get_mapping(self):
        return [
            "client_name",
            "fecha",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "dicember",
            "suscriberid",
            "agent_name",
            "agent_lastname",
            "id",
            "id_insured"
        ]

    def __get_full_query(self, request):
        return (
            self.__get_base_query(request)
            + self.__get_filters(request)
            + self.__apply_order(request)
        )

    def __get_filters(self, request: APIViewRequest):
        user = request.user
        filters = " WHERE 1 "

        if not user.is_admin:
            clients = self.get_related_clients(user.pk, True)
            clients |= self.get_related_applications(user.pk, True)
            clients = clients.exclude(
                Q(suscriberid=None)
                | Q(suscriberid="0")
                | Q(suscriberid="N/A")
                | Q(suscriberid="n/a")
                | Q(suscriberid="na")
                | Q(suscriberid="NA")
                | Q(suscriberid="")
            )
            joiner = "','"
            comma = "'"
            filters += f" and n.p_number in ({comma+self.queryset_to_list(clients,'suscriberid',True, joiner)+comma if clients.exists() else 'null'}) "

        insured = self.check_none(request.query_params.get("insured"))
        if insured:
            filters += f" and n.id_insured = {insured}"

        search = self.check_none(request.query_params.get("search"))
        if search:
            filters += (
                f" and (n.c_name like'%{search}%' or n.p_number like '%{search}%')"
            )
        return filters

    def __get_base_query(self, request: APIViewRequest):
        year = self.check_none(
            request.query_params.get("year"), date.today().year)
        year = self.sql_curate_query(str(year))
        sql = (f"""
            select 
               n.c_name as client_name,n.pyear as fecha, jan.commission as january, feb.commission as february, mar.commission as march, 
               apr.commission as april, may.commission as may, jun.commission as june, jul.commission as july, aug.commission as august, 
               sep.commission as september, oct.commission as october, nov.commission as november, dece.commission as dicember,n.p_number as suscriberid,
                n.agent_name, n.agent_lastname, n.id , n.id_insured
            from 
                (SELECT 
                    pg.c_name,pg.pyear,pg.p_number,ag.agent_name,ag.agent_lastname, ag.id, pg.id_insured 
                FROM payments_global pg LEFT JOIN client cl ON (pg.p_number = cl.suscriberid and cl.borrado<>1 and  (cl.tipoclient=1 or cl.tipoclient=3) and YEAR(cl.aplication_date)={year}) 
                    LEFT JOIN agent ag ON (cl.id_agent = ag.id) 
                where pg.pyear = {year}
                GROUP by pg.p_number order by pg.c_name) n 
            left join (SELECT pg.c_name, sum(pg.commission) commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 1 group by pg.p_number) jan on n.p_number = jan.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear =
            {year} and pg.month = 2 group by pg.p_number) feb on n.p_number = feb.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 3 group by pg.p_number) mar on n.p_number = mar.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 4 group by pg.p_number) apr on n.p_number = apr.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 5 group by pg.p_number) may on n.p_number = may.p_number left join  (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 6 group by pg.p_number) jun on n.p_number = jun.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 7 group by pg.p_number) jul on n.p_number = jul.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 8 group by pg.p_number) aug on n.p_number = aug.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 9 group by pg.p_number) sep on n.p_number = sep.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 10 group by pg.p_number) oct on n.p_number = oct.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 11 group by pg.p_number) nov on n.p_number = nov.p_number left join (SELECT pg.c_name, sum(pg.commission)commission, pg.p_number FROM payments_global pg where pg.pyear = 
            {year}  and pg.month = 12 group by pg.p_number) dece on n.p_number = dece.p_number
        """
               )
        return sql

    def __apply_order(self, request: APIViewRequest):
        sql = ""
        default = "client_name"
        order = self.check_none(request.query_params.get("order"))
        desc = self.check_none(request.query_params.get("desc"))
        if order:
            sql += f" order by {self.sql_curate_query(order)} "
            if desc:
                sql += " desc "
        else:
            sql += f" order by {default} "
        return sql


class SearchFiltersPaymentGlobalOnly(
    APIView, LimitOffsetPagination, PaymentGLobalOnlyCommons
):
    permission_classes = [HasPaymentInsuredOnlyPermission]
    serializer_class = PaymentGlobalSerializer

    def get(self, request: APIViewRequest):
        results = self.get_entries(request)
        maps = self.get_mapping()
        results = self.sql_map_results(maps, results)

        results = self.paginate_queryset(results, request, view=self)
        serializer = self.serializer_class(results, many=True)
        return self.get_paginated_response(serializer.data)


class DataForPaymentInsuredOnly(APIView, AgencyManagement):
    permission_classes = [HasPaymentInsuredOnlyPermission]
    serializer_class = AssitStateSerializer

    def get(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "insurances")
        return Response(selects)


class ExportExcelPaymentInsuredOnly(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGLobalOnlyCommons
):
    permission_classes = [HasExportExcelPaymentBobPermission]
    serializer_class = PaymentGlobalSerializer
    renderer_classes = (XLSXRenderer,)
    xlsx_use_labels = True
    filename = "payment_agent.xlsx"
    xlsx_ignore_headers = ["id_agent"]

    def list(self, request, *args, **kwargs):
        entries = self.get_entries(request)
        maps = self.get_mapping()
        entries = self.sql_map_results(maps, entries)
        self.__handle_month(request)

        serializer = self.serializer_class(entries, many=True)
        return Response(serializer.data)

    def __handle_month(self, request: APIViewRequest):
        month = self.map_month(request.query_params.get("month"))
        if month:
            ignores = self.get_mapping()
            ignores.remove(month)
            ignores.remove("client_name")
            ignores.remove("fecha")
            self.xlsx_ignore_headers = ignores


class ExportPdfPaymentInsuredOnly(APIView, PaymentGLobalOnlyCommons, PDFCommons):
    permission_classes = [HasExportGlobalPaymentPDFPermission]

    def get(self, request):
        entries = self.get_entries(request)

        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))
        if not month:
            data = [[i + 1] + list(r[:-4]) for i, r in enumerate(entries)]
            headers = [
                "Indx",
                "Client Name",
                "Year",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            return self.pdf_create_table(headers, data, A2, f'Report for {insured[0].names if insured else "Insurances"}')
        else:
            data = [
                [i + 1, r[0], r[1], r[1 + int(month)]] for i, r in enumerate(entries)
            ]
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
            headers = [
                "Indx",
                "Client Name",
                "Year",
                month_name,
            ]
            return self.pdf_create_table(headers, data, A4, f'Report for {insured[0].names if insured else "Insurances"} / {month_name}', True)


class ImportedPaymentsDetail(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentInsuredOnlyPermission]

    def get(self, request):
        month = self.check_none(request.GET.get('month'))
        id_insured = self.check_none(request.GET.get('id_insured'))
        suscriberid = self.check_none(request.GET.get('suscriberid'))
        year = self.check_none(request.GET.get('year'))
        if not month or not year or not id_insured or not suscriberid:
            raise ValidationException('Missing Data')
        sql = f"""
            SELECT 
                c_name, agent_name, a_number, p_number, info_month, new_ren, commission, e_date, p_state, n_member
            FROM 
                payments_global
            WHERE
                id_insured = {id_insured} AND (MONTH='{month}' OR MONTH='0{month}') AND pyear={year} AND p_number='{suscriberid}'
        """
        entries = self.sql_select_all(sql)
        results = self.sql_map_results([
            "c_name", "agent_name", "a_number", "p_number", "info_month", "new_ren", "commission", "e_date", "p_state", "n_member"

        ], entries)

        total = 0

        for row in results:
            total += row.get('commission')
        return Response({"data": results, "total": total})
