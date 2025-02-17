from ..imports import *
import re


class PaymentDifferences(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentDifferencesPermission]

    def get(self, request: HttpRequest):
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)
        results = self.map_results_extended(results)
        serializer = OriginalPaymentDifferencesSerializer(
            results, many=True)

        response = self.get_paginated_response(serializer.data)
        return response

    def get_entries(self, request):
        order = self.__apply_ordering(request)
        year = self.check_none(request.GET.get("year"))
        if not year:
            today = date.today()
            year = today.year

        insured = self.check_none(request.GET.get("insured"))

        search = self.check_none(request.GET.get("search"))
        if search:
            search_sql = (
                f""" and (concat(a.agent_name,' ',a.agent_lastname) like '%{search}%')"""
            )
        else:
            search_sql = ""

        month = self.check_none(request.GET.get("month"))
        if not year or not month or not insured:
            raise ValidationException(
                "Missing Required Filters in Request"
            )
        month_str = self.map_month(month)
        sql = f"""
        SELECT a.agent_name, a.agent_lastname, sp.total_commission as system_payment, op.total_commission as original_payment_commission,
        GREATEST(IFNULL(sp.total_commission,0), IFNULL(op.total_commission,0)) AS greatest
        FROM 
        agent a left join 
        (
        SELECT 
            ap.id_agent,
            SUM(ap.commission) AS total_commission
        FROM
            agent_payments ap
        WHERE
            ap.year ='{year}'AND ap.id_insured = {insured} and ap.month= '{self.inverse_map_month(month_str)}'
        group by ap.id_agent
        ) as sp on (a.id=sp.id_agent)
        left join 
        (
        Select op.agent, sum(op.commission) as total_commission
        FROM original_payment op 
        WHERE op.insured={insured} and (op.month='0{month}' or op.month='{month}') and op.year='{year}' 
        GROUP BY op.agent
        ) as op on (a.id=op.agent)
        WHERE 1 {search_sql}
        {order}

        """
        return self.sql_select_all(sql)

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "agent_name"
    ) -> str:
        order = ""
        default = f"order by {default_order}"
        order_field = self.check_none(request.GET.get("order"))
        order_field = "agent_fullname" if order_field == "agent_name" else order_field
        desc = self.check_none(request.GET.get("desc"))
        orderables = [
            "agent_name",
            "agent_lastname",
            "system_payment",
            "original_payment_commission",
            "greatest"
        ]

        # if order_field and order_field in orderables:
        if order_field and order_field in orderables:
            order = f"order by {self.sql_curate_query(order_field)}"
        else:
            order = default
        if desc:
            order += " desc"

        return order

    def map_results_extended(self, results: list) -> list:
        response = []
        for el in results:
            response.append(
                {
                    "agent_name": self.check_none(el[0], "")+" " + self.check_none(el[1], ""),
                    "system_payment": el[2],
                    "original_payment_commission": el[3],
                    "greatest": el[4]
                }
            )
        return response


class ExportExcelPaymentDifferences(XLSXFileMixin, ReadOnlyModelViewSet, PaymentDifferences):
    permission_classes = [HasExportExcelPaymentDifferencesPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = OriginalPaymentDifferencesSerializer
    xlsx_use_labels = True
    filename = "payment_differences.xlsx"
    xlsx_ignore_headers = ["system_payment", "original_payment_commission"]

    def list(self, request: APIViewRequest):
        results = self.get_entries(request)
        results = self.map_results_extended(results)
        serializer = self.get_serializer(
            results, many=True)
        return Response(serializer.data)


class ExportPdfPaymentDifferences(PDFCommons, PaymentDifferences):
    permission_classes = [HasExportPDFPaymentDifferencesPermission]

    def get(self, request):
        results = self.get_entries(request)
        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))

        data = [
            [i + 1, r[0] if r[0] else "" + " " + r[1] if r[1] else "", r[4]]
            for i, r in enumerate(results)
        ]
        if month:
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
        else:
            month_name = ""
        headers = [
            "Indx",
            "Agent Name",
            'Commission',
        ]
        return self.pdf_create_table(headers, data, letter, f'Payments for {insured[0].names if insured else "Insurances"}. {month_name}', True)


class DataForPaymentDifferences(APIView, AgencyManagement):
    permission_classes = [
        HasPaymentDifferencesPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "insurances"))
