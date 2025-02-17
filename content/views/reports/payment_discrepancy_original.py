from ..imports import *
import re


class PaymentDiscrepanciesOriginal(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentDiscrepanciesOriginalPermission]

    def get(self, request: HttpRequest):
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)
        results = self.map_results_extended(results)
        serializer = OriginalPaymentDiscrepanciesSerializer(
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
        agent = self.select_agent(request.GET.get("agent"), request.user.pk)
        month = self.check_none(request.GET.get("month"))

        if not insured or not agent or not month:
            raise ValidationException('Missing Filters')

        agency = self.select_agency(request.GET.get("agency"), request.user.pk)
        if agency:
            agency_sql = f"and a.id_agency={agency.id}"
        else:
            agency_sql = ""

        search = self.check_none(request.GET.get("search"))
        if search:
            search_sql = (
                f""" and (concat(a.agent_name,' ',a.agent_lastname) like '%{search}%' 
                or op.client_name like '%{search}%'
                or op.suscriber_id like '%{search}%'
                )"""
            )
        else:
            search_sql = ""

        month = self.inverse_map_month(self.map_month(month))

        new_payments = self.check_new_payment(month, year)
        if new_payments:
            sql = f"""
                Select  CONCAT(
                        a.agent_name,
                        ' ',
                        a.agent_lastname
                    ) AS agent_fullname,
                    op.client_name as client_name,
                    op.suscriber_id,
                    sum(op.member_number) as members,
                    sum(op.commission) AS amount,
                    op.agent,
                    CASE
                        WHEN c.suscriberid IS NULL and ap.suscriberid is NULL THEN 'The policy is not in the system, fix this and make a claim so we can process your payment'
                        WHEN ap.repaid_on IS NOT NULL THEN CONCAT('This policy was/will be paid on: ', ap.repaid_on)
                        WHEN ap.suscriberid is NULL THEN 'This Policy was not paid for some reason, you can make a claim. so we can check what happened'
                        ELSE ''
                    END AS policy_status
                from original_payment op
                left join 
                (Select * from client where borrado<>1 and SUBSTRING(aplication_date,1,4) ='{year}') c
                on (op.suscriber_id=c.suscriberid)
                LEFT JOIN agent a ON
                (op.agent = a.id)
                LEFT JOIN (
                    SELECT * FROM agent_payments WHERE year = {year} AND month = {month} AND id_insured={insured} AND id_agent = {agent.id} 
                    group by suscriberid
                ) ap ON op.suscriber_id = ap.suscriberid
                WHERE
                op.year='{year}' 
                and op.month={month}
                and insured={insured}
                {agency_sql}
                and op.agent={agent.id}
                {search_sql}
                AND (c.suscriberid IS NULL OR ap.suscriberid IS NULL OR ap.repaid_on is not NULL)

                GROUP BY 
                op.suscriber_id 
                {order}

            """
        else:
            sql = f"""
                Select  CONCAT(
                        a.agent_name,
                        ' ',
                        a.agent_lastname
                    ) AS agent_fullname,
                    op.client_name as client_name,
                    op.suscriber_id,
                    sum(op.member_number) as members,
                    sum(op.commission) AS amount,
                    op.agent,
                    CASE
                        WHEN c.suscriberid IS NULL THEN 'The policy is not in the system, fix this and make a claim so we can process your payment'
                        ELSE ''
                    END AS policy_status
                from original_payment op
                left join 
                (Select * from client where borrado<>1 and SUBSTRING(aplication_date,1,4) ='{year}') c
                on (op.suscriber_id=c.suscriberid)
                LEFT JOIN agent a ON
                (op.agent = a.id)
               
                WHERE
                op.year='{year}' 
                and op.month={month}
                and insured={insured}
                {agency_sql}
                and op.agent={agent.id}
                {search_sql}
                AND (c.suscriberid IS NULL)

                GROUP BY 
                op.suscriber_id 
                {order}

            """
        return self.sql_select_all(sql)

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "agent_fullname, client_name"
    ) -> str:
        order = ""
        default = f"order by {default_order}"
        order_field = self.check_none(request.GET.get("order"))
        order_field = "agent_fullname" if order_field == "agent_name" else order_field
        desc = self.check_none(request.GET.get("desc"))
        orderables = [
            "agent_fullname",
            "client_name",
            "suscriber_id",
            "members",
            "amount"
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
                    "agent_name": self.check_none(el[0], ""),
                    "client_name": el[1],
                    "suscriber_id": el[2],
                    "members": el[3],
                    "amount": el[4],
                    "agent": el[5],
                    "policy_status": el[6],
                }
            )
        return response


class ExportExcelPaymentDiscrepanciesOriginal(XLSXFileMixin, ReadOnlyModelViewSet, PaymentDiscrepanciesOriginal):
    permission_classes = [HasExportExcelPaymentDiscrepanciesOriginalPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = OriginalPaymentDiscrepanciesSerializer
    xlsx_use_labels = True
    filename = "orignal_payment_client.xlsx"
    xlsx_ignore_headers = ["agent"]

    def list(self, request: APIViewRequest):
        results = self.get_entries(request)
        results = self.map_results_extended(results)
        serializer = self.get_serializer(
            results, many=True)
        return Response(serializer.data)


class ExportPdfPaymentDiscrepanciesOriginal(PDFCommons, PaymentDiscrepanciesOriginal):
    permission_classes = [HasExportPDFPaymentDiscrepanciesOriginalPermission]

    def get(self, request):
        results = self.get_entries(request)
        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))

        data = [
            [i + 1, r[0], r[1], r[2], r[3], r[4]]
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
            "Client Name",
            "Suscriber ID",
            "Members",
            'Amount',
        ]
        return self.pdf_create_table(headers, data, A3, f'Original Discrepancies for {insured[0].names if insured else "Insurances"}. {month_name}', True)
