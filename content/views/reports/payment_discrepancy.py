from ..imports import *


class PaymentDiscrepancies(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentDiscrepancyPermission]

    def get(self, request: APIViewRequest):
        entries = self.get_entries(request)
        maps = self.get_mappings()
        entries = self.sql_map_results(maps, entries)

        results = self.paginate_queryset(entries, request, view=self)
        return self.get_paginated_response(results)

    def get_entries(self, request):
        user: CustomUser = request.user
        self.check_permission(user, "content.view_paymentdiscrepancies")
        entries = self.sql_select_all(self.__get_query(request))

        return entries

    def get_mappings(self):
        return [
            "id",
            "agent_name",
            "client_name",
            "suscriberid",
            "num_members",
            "date_birth",
            "pol_hold_state",
            "effective_date",
            "paid_date",
            "term_date",
        ]

    def __get_query(self, request):
        return (
            self.__get_basic_query(request)
            + self.__get_order_query(request)
        )

    def __get_basic_query(self, request):
        year = self.check_none(
            request.query_params.get("year"), date.today().year)
        month = self.check_none(
            request.query_params.get("month"))
        year = self.sql_curate_query(year)
        insured = self.check_none(request.query_params.get("insured"))
        if not insured or not month:
            raise ValidationException('Missing Filters')
        filter_dates = self.check_none(
            request.query_params.get("filter_dates"))
        date_filter = ""
        if filter_dates == '1' or filter_dates == 1:
            date_filter = " AND b.paid_date > CURDATE() AND b.term_date > CURDATE()"

        query = f"""
            SELECT DISTINCT
                b.id,
                b.agent_name,
                CONCAT(b.client_name, ' ', b.client_lastname) AS client_name,
                b.suscriberid,
                b.num_members,
                b.date_birth,
                b.pol_hold_state,
                b.effective_date,
                b.paid_date,
                b.term_date
            FROM
                bob_global b
            LEFT JOIN 
                (
                    Select * from payments_global where month='{self.inverse_map_month(self.map_month(month))}' and pyear={year} and id_insured={insured}
                    group by p_number
                ) p ON b.suscriberid = p.p_number 
            WHERE
                1 {date_filter} AND YEAR(b.effective_date)={year} AND b.id_insured = {insured} AND p.id IS NULL

        """
        return query

    def __get_order_query(self, request: APIViewRequest):
        sql = ""
        search = self.check_none(request.query_params.get("search"))
        if search:
            search = self.sql_curate_query(search)
            sql += f""" and (concat(a.agent_name, ' ', a.agent_lastname) like '%{search}%'
                        or concat(c.names, ' ',c.lastname) like '%{search}%' 
                        or b.suscriberid like '%{search}%')"""
        default = "agent_name"
        order = self.check_none(request.query_params.get("order"))
        desc = self.check_none(request.query_params.get("desc"))
        if order:
            sql += f" order by {self.sql_curate_query(order)} "
            if desc:
                sql += " desc "
        else:
            sql += f" order by {default} "
        return sql


class DataForPaymentDiscrepancies(APIView, AgencyManagement):
    permission_classes = [HasPaymentDiscrepancyPermission]

    def get(self, request: APIViewRequest):
        user = request.user
        selects = self.get_selects(user.pk, "insurances")
        return Response(selects)


class PaymentDiscrepanciesExportExcelSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(label=("Agent"))
    client_name = serializers.CharField(label=("Client"))
    suscriberid = serializers.CharField(label=("Policy Number"))
    num_members = serializers.CharField(label=("Number of Members"))
    date_birth = serializers.CharField(label=("Date of Birth"))
    pol_hold_state = serializers.CharField(label=("State"))
    effective_date = serializers.CharField(label=("Effective Date"))
    paid_date = serializers.CharField(label=("PTD"))
    term_date = serializers.CharField(label=("Termination Date"))

    class Meta:
        fields = (
            "agent_name",
            "client_name",
            "suscriberid",
            "num_members",
            "date_birth",
            "pol_hold_state",
            "effective_date",
            "paid_date",
            "term_date",
        )
        model = Agent


class ExportExcelPaymentDiscrepancies(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentDiscrepancies
):
    permission_classes = [HasExportExcelPaymentDiscrepanciesPermission]
    serializer_class = PaymentDiscrepanciesExportExcelSerializer
    renderer_classes = (XLSXRenderer,)
    xlsx_use_labels = True
    filename = "payment_agent.xlsx"
    xlsx_ignore_headers = ["id_client"]

    def list(self, request):
        entries = self.get_entries(request)
        maps = self.get_mappings()
        entries = self.sql_map_results(maps, entries)
        return Response(entries)


class ExportPdfPaymentDiscrepancies(PaymentDiscrepancies, PDFCommons):
    permission_classes = [HasExportPDFPaymentDiscrepanciesPermission]

    def get(self, request):
        entries = self.get_entries(request)
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))
        data = [
            [
                i,
                r[1].replace(" ", "\n", 1) if r[1] else "",
                r[2].replace(" ", "\n", 1) if r[2] else "",
            ]
            + list(r[3:])
            for i, r in enumerate(entries)
        ]
        headers = [
            "Indx",
            "Agent",
            "Client",
            "SuscID",
            "#Mem",
            "DOB",
            "State",
            "Effective Date",
            "PDT",
            "Term Date",
        ]
        return self.pdf_create_table(headers, data, A1, f'Payment Discrepancies for {insured[0].names}' if insured else "Payment Discrepancies")
