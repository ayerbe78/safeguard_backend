from ..imports import *
import re


class PaymentClientOriginal(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentClientOriginalPermission]

    def get(self, request: HttpRequest):
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)
        month = self.check_none(request.GET.get('month'))
        if not month:
            results = self.map_results(results)
            serializer = OriginalPaymentClientSerializer(results, many=True)
        else:
            results = self.map_results_extended(results)
            serializer = OriginalPaymentClientMonthSerializer(
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
        if insured:
            insured_sql = f"and insured= {insured}"
        else:
            insured_sql = ""

        agency = self.select_agency(request.GET.get("agency"), request.user.pk)
        if agency:
            agency_sql = f"and a.id_agency={agency.id}"
        else:
            agency_sql = ""

        agent = self.select_agent(request.GET.get("agent"), request.user.pk)

        agent_sql = ""
        if agent:
            agent_sql = f"and op.agent={agent.id}"

        agents = self.get_related_agents(request.user.pk, True)
        if not (request.user.is_admin and not (agent or agency)):
            agent_sql += (
                f" AND op.agent in ({self.queryset_to_list(agents, to_string=True)})"
            )

        search = self.check_none(request.GET.get("search"))
        if search:
            search_sql = (
                f""" and (concat(a.agent_name,' ',a.agent_lastname) like '%{search}%' or op.suscriber_id like '%{search}%' or op.client_name like '%{search}%')"""
            )
        else:
            search_sql = ""

        month = self.check_none(request.GET.get("month"))
        if not month:
            sql = f"""
            SELECT
                main.agent_fullname as agent_fullname,
                main.client_name as client_name,
                main.suscriber_id,
                jan.commission as january, 
                feb.commission as february,
                mar.commission as march,
                apr.commission as april, 
                may.commission as may, 
                jun.commission as june, 
                jul.commission as july, 
                ag.commission as august, 
                sep.commission as september, 
                oct.commission as october,
                nov.commission as november,
                dece.commission as dicember,
                main.agent_id as agent_id
            FROM
                (
                SELECT
                    op.suscriber_id,
                    op.client_name,
                    CONCAT(
                        a.agent_name,
                        ' ',
                        a.agent_lastname
                    ) AS agent_fullname,
                    op.agent as agent_id,
                    a.id_agency
                FROM
                    original_payment op
                LEFT JOIN agent a ON
                    (op.agent = a.id)
                WHERE
                    year = '{year}' {agency_sql} {agent_sql} {search_sql}
                GROUP BY
                    op.suscriber_id,
                    op.client_name
            ) main
            LEFT JOIN(
                SELECT agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '01'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) jan
            ON
                (
                    main.suscriber_id = jan.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '02'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) feb
            ON
                (
                    main.suscriber_id = feb.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '03'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) mar
            ON
                (
                    main.suscriber_id = mar.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '04'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) apr
            ON
                (
                    main.suscriber_id = apr.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '05'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) may
            ON
                (
                    main.suscriber_id = may.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '06'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) jun
            ON
                (
                    main.suscriber_id = jun.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '07'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) jul
            ON
                (
                    main.suscriber_id = jul.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '08'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) ag
            ON
                (
                    main.suscriber_id = ag.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '09'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) sep
            ON
                (
                    main.suscriber_id = sep.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '10'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) oct
            ON
                (
                    main.suscriber_id = oct.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '11'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) nov
            ON
                (
                    main.suscriber_id = nov.suscriber_id
                )
            LEFT JOIN(
                SELECT
                    agent,
                    suscriber_id,
                    client_name,
                    SUM(commission) AS commission
                FROM
                    original_payment
                WHERE
                    year = '{year}' AND month = '12'
                    {insured_sql}
                GROUP BY
                    suscriber_id,
                    client_name,
                    agent
            ) dece
            ON
                (
                    main.suscriber_id = dece.suscriber_id
                )
            {order}
            """
        else:
            sql = f"""
            SELECT
                CONCAT(
                    a.agent_name,
                    ' ',
                    a.agent_lastname
                ) AS agent_fullname,
                op.client_name as client_name,
                op.suscriber_id,
                op.member_number as members,
                op.commission AS amount,
                op.agent,
                op.info_month
            FROM
                original_payment op
            LEFT JOIN agent a ON
                (op.agent = a.id)
            WHERE
                year = '{year}' AND (month = '{month}' OR month='0{month}') {insured_sql} {agency_sql} {agent_sql} {search_sql}
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
        month = request.GET.get("month", None)
        desc = self.check_none(request.GET.get("desc"))
        orderables = [
            "agent_fullname",
            "client_name",
            "suscriber_id",
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
        ]
        month_orderables = [
            "agent_fullname",
            "client_name",
            "suscriber_id",
            "members",
            "amount"
        ]

        # if order_field and order_field in orderables:
        if order_field and month and order_field in month_orderables:
            order = f"order by {self.sql_curate_query(order_field)}"
        elif order_field and month == "0" and order_field in orderables:
            order = f"order by {self.sql_curate_query(order_field)}"
        else:
            order = default
        if desc:
            order += " desc"

        return order

    def map_results(self, results: list) -> list:
        response = []
        for el in results:
            response.append(
                {
                    "agent_name": self.check_none(el[0], ""),
                    "client_name": el[1],
                    "suscriber_id": el[2],
                    "january": el[3],
                    "february": el[4],
                    "march": el[5],
                    "april": el[6],
                    "may": el[7],
                    "june": el[8],
                    "july": el[9],
                    "august": el[10],
                    "september": el[11],
                    "october": el[12],
                    "november": el[13],
                    "dicember": el[14],
                    "agent": el[15]
                }
            )
        return response

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
                    "info_month": el[6],
                }
            )
        return response


class ExportExcelPaymentClientOriginal(XLSXFileMixin, ReadOnlyModelViewSet, PaymentClientOriginal):
    permission_classes = [HasExportExcelPaymentClientOriginalPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = OriginalPaymentClientSerializer
    xlsx_use_labels = True
    filename = "orignal_payment_client.xlsx"
    xlsx_ignore_headers = ["agent"]

    def list(self, request: APIViewRequest):
        month = self.map_month(request.GET.get("month"))
        results = self.get_entries(request)

        if not month:
            results = self.map_results(results)
        else:
            self.serializer_class = OriginalPaymentClientMonthSerializer
            results = self.map_results_extended(results)
            serializer = self.get_serializer(
                results, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentClientOriginal(PDFCommons, PaymentClientOriginal):
    permission_classes = [HasExportPDFPaymentClientOriginalPermission]

    def get(self, request):
        results = self.get_entries(request)
        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))
        if not month:
            data = [[i + 1, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14]]
                    for i, r in enumerate(results)
                    ]
            headers = [
                "Indx",
                "Agent Name",
                "Client Name",
                "Suscriber ID",
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
            return self.pdf_create_table(headers, data, A1, f'Original Report for {insured[0].names if insured else "Insurances"}')
        else:
            data = [
                [i + 1, r[0], r[1], r[2], r[6], r[3], r[4]]
                for i, r in enumerate(results)
            ]
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
            headers = [
                "Indx",
                "Agent Name",
                "Client Name",
                "Suscriber ID",
                "Paid Month",
                "Members",
                'Amount',
            ]
            return self.pdf_create_table(headers, data, A3, f'Original Report for {insured[0].names if insured else "Insurances"} / {month_name}', True)
