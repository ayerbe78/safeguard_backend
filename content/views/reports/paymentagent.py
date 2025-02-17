from ..imports import *


class PaymentAgentCommons(AgencyManagement, DirectSql):
    def get_entries(self, request: HttpRequest):
        user: CustomUser = request.user
        filters = self.__apply_filters(request)
        order = self.__apply_ordering(request)
        month = self.map_month(request.GET.get("month"))
        year = self.check_none(request.GET.get(
            "year"), str(date.today().year))
        join_type = "left" if user.is_admin else "inner"
        if not month:
            sql = f"""Select a.agent_name,a.agent_lastname,p.fecha,sum(p.january) january,
            sum(p.february) february, sum(p.march) march, sum(p.april) april, sum(p.may) may,
            sum(p.june) june, sum(p.july) july, sum(p.august) august, sum(p.september) september,
            sum(p.october) october, sum(p.november) november, sum(p.dicember) dicember,
            a.id from payments p {join_type} join agent a on
            p.id_agent=a.id {join_type} JOIN 
            client c ON (p.id_client=c.id)
            where 1 {filters} and c.borrado<>1 and SUBSTRING(c.aplication_date,1,4)='{year}' group by p.id_agent {order}"""

            results = self.sql_select_all(sql)
        else:
            insured = self.check_none(request.GET.get("insured"))

            sc1, sc2, sc3 = self.__get_subqueries(year, month, insured)
            sql = f"""Select a.agent_name,a.agent_lastname,p.fecha,sum(p.january) january,
                sum(p.february) february, sum(p.march) march, sum(p.april) april, sum(p.may) may,
                sum(p.june) june, sum(p.july) july, sum(p.august) august, sum(p.september) september,
                sum(p.october) october, sum(p.november) november, sum(p.dicember) dicember,
                a.id, c.policies, c.nosub, c.payment, c.no_payment, sc2.no_elegible, sc3.cancel, c.members
                from payments p {join_type} join agent a on p.id_agent=a.id
                LEFT JOIN client on (p.id_client=client.id)
                {join_type} JOIN ({sc1}) c ON p.id_agent = c.id 
                left join ({sc2})sc2 on p.id_agent=sc2.agent
                left join ({sc3})sc3 on p.id_agent=sc3.agent
                where 1 and client.borrado<>1 and SUBSTRING(client.aplication_date,1,4)='{year}'
                {filters} group by p.id_agent {order}"""
            results = self.sql_select_all(sql)
        return results

    def __apply_filters(self, request: HttpRequest) -> str:
        user: CustomUser = request.user
        filters = " "

        year = self.check_none(request.GET.get("year"), str(date.today().year))
        filters += f"and p.fecha={year}"

        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        if agent:
            agents = agents.filter(pk=agent.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        if not (user.is_admin and not (agent or agency)):
            filters += (
                f" AND p.id_agent in ({self.queryset_to_list(agents, to_string=True)})"
            )

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            filters += f" AND p.id_client in (Select id from client where id_insured={insured})"

        search = self.check_none(request.GET.get("search"))
        if search:
            filters += (
                f""" and concat(a.agent_name,' ',a.agent_lastname) like '%{search}%'"""
            )

        month = self.map_month(request.GET.get("month"))
        if month:
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" AND p.{month} <>0 "
            elif payment and int(payment) == 2:
                filters += f" AND p.{month}=0 "

        return filters

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "a.agent_name"
    ) -> str:
        order = ""
        default = f"order by {default_order}"
        order_field = self.check_none(request.GET.get("order"))
        month = self.map_month(request.GET.get("month"))
        desc = self.check_none(request.GET.get("desc"))
        orderables = [
            "agent_name",
            "agent_lastname",
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
            "id",
            "policies",
            "nosub",
            "payment",
            "no_payment",
            "no_elegible",
            "cancel",
        ]

        # if order_field and order_field in orderables:
        if order_field and month and order_field in orderables:
            order = f"order by {self.sql_curate_query(order_field)}"
        elif order_field and order_field in orderables[:-6]:
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
                    "agent_name": self.check_none(el[0], "")
                    + " "
                    + self.check_none(el[1], ""),
                    "fecha": el[2],
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
                    "id_agent": el[15],
                }
            )
        return response

    def map_results_extended(self, results: list) -> list:
        response = []
        for el in results:
            response.append(
                {
                    "agent_name": self.check_none(el[0], "")
                    + " "
                    + self.check_none(el[1], ""),
                    "fecha": el[2],
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
                    "id_agent": el[15],
                    "policies": el[16],
                    "nosub": el[17],
                    "payment": el[18],
                    "no_payment": el[19],
                    "no_elegible": el[20],
                    "cancel": el[21],
                    "members": el[22],
                }
            )
        return response

    def __get_subqueries(self, year: str, month: str, insured: str):
        if insured:
            insured_filter = f""" and c.id_insured={insured} """
        else:
            insured_filter = ""
        sc1 = f"""Select COUNT(c.id) as policies, COUNT(CASE WHEN c.suscriberid = 'N/A' THEN c.suscriberid END)
            as nosub,count(CASE when p.{month}<>0 then p.id end) as payment, count(CASE when p.{month}
            =0 then p.id end) as no_payment, c.id_agent as id, SUM(c.family_menber) as members
            FROM client c inner join payments p on c.id=p.id_client WHERE
            SUBSTRING(c.aplication_date,1,4)={year} {insured_filter} AND c.borrado <> 1 AND p.id_agent=c.id_agent
            group by c.id_agent"""

        sc2 = f"""SELECT COUNT(bob_global.id) as no_elegible, c.id_agent as agent
            FROM (select * from bob_global where id in (select max(b.id) from bob_global b group by b.suscriberid)) bob_global
            INNER JOIN  client c ON
            c.suscriberid = bob_global.suscriberid WHERE c.borrado <> 1 AND
            bob_global.eleg_commision = 'No' {insured_filter} AND SUBSTRING(aplication_date,1,4) = {year}
            group by c.id_agent"""

        sc3 = f"""SELECT COUNT(bob_global.id) as cancel, c.id_agent as agent
            FROM (select * from bob_global where id in (select max(b.id) from bob_global b group by b.suscriberid)) bob_global
            INNER JOIN  client c ON
            c.suscriberid = bob_global.suscriberid WHERE c.borrado <> 1 AND
            bob_global.term_date <= CURDATE() {insured_filter} AND SUBSTRING(aplication_date,1,4) = {year}
            group by c.id_agent"""

        return sc1, sc2, sc3


class ReportPaymentAgent(APIView, PaymentAgentCommons, LimitOffsetPagination):
    permission_classes = [HasPaymentAgentPermission]

    def get(self, request: HttpRequest):
        month = self.map_month(request.GET.get("month"))
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)

        if not month:
            results = self.map_results(results)
            serializer = PaymentAgentSerializer(results, many=True)
        else:
            results = self.map_results_extended(results)
            serializer = PaymentAgentMonthSerializer(results, many=True)

        response = self.get_paginated_response(serializer.data)
        return response


class ReportPaymentAgentSummary(APIView, PaymentCommons):
    permission_classes = [HasPaymentAgentPermission]

    def get(self, request: HttpRequest):
        filters = self._apply_filters(request)
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        sql = f"""SELECT p.index_payment,count(p.id),sum(p.commision), created_at FROM payments_control p
                    join agent a on p.id_agent=a.id 
                    LEFT JOIN payments pay on (p.id_payment=pay.id)
                    left join client c on (pay.id_client=c.id)
                    {filters}
                     and c.borrado<>1 and SUBSTRING(c.aplication_date,1,4) ='{year}'
                       GROUP BY p.index_payment"""
        response = self.sql_select_all(
            sql, ["indx", "count", "commission", "created_at"])
        return Response(response)

    def _apply_filters(self, request: HttpRequest):
        user = request.user
        filters = ""
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        filters += f" where p.year_made={self.sql_curate_query(year)} "
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            filters += f" AND p.id_insured={insured} "
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        if agent:
            agents = agents.filter(id=agent.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        if not (user.is_admin and not (agent or agency)):
            filters += (
                f" AND p.id_agent in ({self.queryset_to_list(agents, to_string=True)})"
            )

        month = self.check_none(request.GET.get("month"))
        if month:
            month = self.sql_curate_query(month)
            filters += f" and (p.month='{month}' or p.month='0{month}') "
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" AND p.commision<>0 "
            elif payment and int(payment) == 2:
                filters += f" AND p.commision=0 "
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += (
                f" and concat(a.agent_name,' ',a.agent_lastname) like '%{search}%' "
            )

        return filters


class ReportPaymentGlobalAgentSummary(APIView, PaymentCommons):
    permission_classes = [HasPaymentAgentPermission]

    def get(self, request: HttpRequest):
        filters = self._apply_filters(request)
        self_managed = self.check_none(request.GET.get("self_managed"))
        self_managed_filter = "and ag.self_managed = 1" if self_managed == '1' else "and (ag.self_managed <> 1 or ag.self_managed is null)"
        sql = f"""
                SELECT
                    ap.payment_index,
                    COUNT(DISTINCT ap.id_client),
                    SUM(ap.commission),
                    created_at
                FROM
                    agent_payments ap
                JOIN agent a ON
                    ap.id_agent = a.id
                JOIN agency ag ON (a.id_agency=ag.id)
                WHERE
                    1 {filters} {self_managed_filter}
                GROUP BY  ap.payment_index"""
        response = self.sql_select_all(
            sql, ["indx", "count", "commission", "created_at"])
        return Response(response)

    def _apply_filters(self, request: HttpRequest):
        user = request.user
        filters = ""
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        filters += f" AND ap.year={self.sql_curate_query(year)} "
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            filters += f" AND ap.id_insured={insured} "
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        if agent:
            agents = agents.filter(id=agent.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        if not (user.is_admin and not (agent or agency)):
            filters += (
                f" AND ap.id_agent in ({self.queryset_to_list(agents, to_string=True)})"
            )

        month = self.check_none(request.GET.get("month"))
        if month:
            month = self.sql_curate_query(month)
            filters += f" and (ap.month='{month}' or ap.month='0{month}') "
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" AND ap.repaid_on is NULL "
            elif payment and int(payment) == 2:
                filters += f" AND ap.commission is NULL "
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += (
                f" and LOWER(ap.agent_name) like '%{search.lower()}%' "
            )

        return filters


class ReportPaymentAgentSummaryDetails(
    ReportPaymentAgentSummary, LimitOffsetPagination
):
    def get(self, request):
        payment_ids, data, t_commission = self.get_entries(request)
        total_paid = 0
        for p in payment_ids:
            try:
                total_paid += float(p["comm"])
            except:
                pass
        data = self.__apply_order(data, request)
        results = self.paginate_queryset(data, request, view=self)
        response = self.get_paginated_response(results)
        response.data["total_paid"] = total_paid
        response.data["total_commission"] = t_commission

        return response

    def get_entries(self, request):
        index = self.check_none(request.GET.get("index"), 0)
        index = self.sql_curate_query(index)
        filters = self._apply_filters(request)
        query = f"""SELECT p.id_payment,p.month,p.commision FROM payments_control p
            JOIN payments pa on p.id_payment =  pa.id
            join client c on pa.id_client=c.id
            join agent a on
            p.id_agent=a.id {filters} and p.index_payment = {index} and c.borrado<>1"""
        payment_ids = self.sql_select_all(query, ["id", "month", "comm"])
        months = self.dict_list_to_list(
            payment_ids, param="month", to_string=True)
        payments = self.dict_list_to_list(payment_ids, to_string=True)
        data, t_commission = self.pay_get_actual_payments_for_agent(
            payments, months, index
        )
        return payment_ids, data, t_commission

    def __apply_order(self, data, request):
        order_default = "agent_name"
        order = self.check_none(request.GET.get("order"), order_default)
        desc = self.check_none(request.GET.get("desc"), False)
        desc = 1 if desc else 0

        if order not in ["commission", "num_member"]:
            return self.apply_order_dict_list(data, request, order_default)

        def key_func(x):
            return x[order] if x[order] else -1

        try:
            queryset = sorted(data, key=key_func, reverse=desc)
        except KeyError:
            order = order_default
            queryset = sorted(data, key=key_func, reverse=desc)

        return queryset


class ReportPaymentGlobalAgentSummaryDetails(
    ReportPaymentGlobalAgentSummary, LimitOffsetPagination
):
    def get(self, request):
        primary_results = self.get_entries(request)
        total_paid = 0
        for p in primary_results:
            try:
                total_paid += float(p["commission"])
            except:
                pass
        data = self.__apply_order(primary_results, request)
        results = self.paginate_queryset(data, request, view=self)
        response = self.get_paginated_response(results)
        response.data["total_paid"] = total_paid

        return response

    def get_entries(self, request):
        index = self.check_none(request.GET.get("index"), 0)
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        index = self.sql_curate_query(index)
        filters = self._apply_filters(request)
        self_managed = self.check_none(request.GET.get("self_managed"))
        self_managed_filter = "and ag.self_managed = 1" if self_managed == '1' else "and (ag.self_managed <> 1 or ag.self_managed is null)"
        query = f"""
            SELECT
                ap.agent_name,
                ap.client_name,
                ap.insured_name,
                a.npn,
                ap.suscriberid,
                ap.members_number,
                c.aplication_date,
                ap.payment_type,
                CONCAT(ap.month,'/01/',ap.year),
                ap.info_month,
                ap.commission
            FROM
                agent_payments ap
            JOIN agent a ON
                ap.id_agent = a.id
            JOIN client c ON
                (ap.id_client = c.id)
            JOIN agency ag ON (a.id_agency=ag.id)
            WHERE
                1 {filters} {self_managed_filter}  AND ap.payment_index = {index}
        """
        primary_results = self.sql_select_all(
            query, ["agent_name", "client_name", "insured_name", "npn", "suscriberid", "num_member", "effective_date", "type", "date", "month", "commission"])

        return primary_results

    def __apply_order(self, data, request):
        order_default = "agent_name"
        order = self.check_none(request.GET.get("order"), order_default)
        desc = self.check_none(request.GET.get("desc"), False)
        desc = 1 if desc else 0

        if order not in ["commission", "num_member"]:
            return self.apply_order_dict_list(data, request, order_default)

        def key_func(x):
            return x[order] if x[order] else -1

        try:
            queryset = sorted(data, key=key_func, reverse=desc)
        except KeyError:
            order = order_default
            queryset = sorted(data, key=key_func, reverse=desc)

        return queryset


class ExportExcelPaymentAgentSummaryDetails(
    XLSXFileMixin, ReadOnlyModelViewSet, ReportPaymentAgentSummaryDetails
):
    permission_classes = [HasExportExcelPaymentAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentAgentSummaryDetailsExcelSerializer
    xlsx_use_labels = True
    filename = "payment_agent_details.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        payment_ids, data, t_commission = self.get_entries(request)
        serializer = self.get_serializer(data, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGloabalAgentDetails(ReportPaymentAgentSummaryDetails, PDFCommons):
    permission_classes = [HasExportAgentPaymentPDFPermission]

    def get(self, request):
        payment_ids, data, t_commission = self.get_entries(request)
        data = [
            [
                i + 1,
                r.get("agent_name"),
                r.get("client_name"),
                r.get("date"),
                r.get("effective_date"),
                r.get("insured_name"),
                r.get("month"),
                r.get("npn"),
                r.get("num_member"),
                r.get("state"),
                r.get("suscriberid"),
                r.get("type"),
                r.get("commission"),
            ]
            for i, r in enumerate(data)
        ]
        headers = [
            "Indx",
            "Agent",
            "Client",
            "Date",
            "Application Date",
            "Insurance",
            "Month",
            "NPN",
            "Members",
            "State",
            "Suscriber ID",
            "Type",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A2, 'Agent Report', True)


class ExportExcelPaymentGlobalAgentSummaryDetails(
    XLSXFileMixin, ReadOnlyModelViewSet, ReportPaymentGlobalAgentSummaryDetails
):
    permission_classes = [HasExportExcelPaymentAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentAgentSummaryDetailsExcelSerializer
    xlsx_use_labels = True
    filename = "payment_agent_details.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        results = self.get_entries(request)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGlobalAgentSummaryDetails(ReportPaymentGlobalAgentSummaryDetails, PDFCommons):
    permission_classes = [HasExportAgentPaymentPDFPermission]

    def get(self, request):
        results = self.get_entries(request)
        data = [
            [
                i + 1,
                r.get("agent_name"),
                r.get("client_name"),
                r.get("date"),
                r.get("effective_date"),
                r.get("insured_name"),
                r.get("month"),
                r.get("npn"),
                r.get("num_member"),
                r.get("suscriberid"),
                r.get("type"),
                r.get("commission"),
            ]
            for i, r in enumerate(results)
        ]
        headers = [
            "Indx",
            "Agent",
            "Client",
            "Date",
            "Application Date",
            "Insurance",
            "Month",
            "NPN",
            "Members",
            "Suscriber ID",
            "Type",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A2, 'Payment Global Agent Details Report', True)


class DataForPaymentGlobalAgent(APIView, AgencyManagement):
    permission_classes = [HasPaymentAgentPermission]

    def get(self, request):
        user = request.user
        return Response(self.get_selects(user.pk, "agents", "agencies", "insurances"))


class ExportExcelPaymentAgent(XLSXFileMixin, ReadOnlyModelViewSet, PaymentAgentCommons):
    permission_classes = [HasExportExcelPaymentAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentAgentSerializer
    xlsx_use_labels = True
    filename = "payment_agent.xlsx"
    xlsx_ignore_headers = ["id_agent"]

    def list(self, request: APIViewRequest):
        month = self.map_month(request.GET.get("month"))
        results = self.get_entries(request)

        if not month:
            results = self.map_results(results)
        else:
            self.serializer_class = ExportPaymentAgentMonthSerializer
            context = {"request": request, "month": month}
            results = self.map_results_extended(results)
            serializer = self.get_serializer(
                results, many=True, context=context)
            return Response(serializer.data)

        if request.GET.get('year') == 2023 or request.GET.get('year') == '2023':
            self.serializer_class = JanJunSerializer
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentAgent(APIView, PaymentAgentCommons, PDFCommons):
    permission_classes = [HasExportAgentPaymentPDFPermission]

    def get(self, request):
        results = self.get_entries(request)
        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))
        if not month:
            data = [[i + 1, (r[0] + "\n" if r[0] else "\n") + (r[1] if r[1] else ""), r[2]] + list(r[-13:-1])
                    for i, r in enumerate(results)
                    ]
            headers = [
                "Indx",
                "Agent Name",
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
            if request.GET.get('year') == 2023 or request.GET.get('year') == '2023':
                data = [[i + 1, (r[0] + "\n" if r[0] else "\n") + (r[1] if r[1] else ""), r[2], r[3], r[4], r[5], r[6], r[7], r[8]]
                        for i, r in enumerate(results)
                        ]
                headers = [
                    "Indx",
                    "Agent Name",
                    "Year",
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                ]
                return self.pdf_create_table(headers, data, A2, f'Report for {insured[0].names if insured else "Insurances"}')
            return self.pdf_create_table(headers, data, A1, f'Report for {insured[0].names if insured else "Insurances"}')
        else:
            data = [
                [i + 1, (r[0] + "\n" if r[0] else "\n") + (r[1] if r[1] else ""), r[2]] +
                list(r[-7:]) + [r[2 + int(month)]]
                for i, r in enumerate(results)
            ]
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
            headers = [
                "Indx",
                "Agent Name",
                "Year",
                "Policies",
                "No Sub.",
                "Payment",
                "No Pay.",
                "No Elig.",
                "Cancel",
                "Members",
                month_name,
            ]
            return self.pdf_create_table(headers, data, A3, f'Report for {insured[0].names if insured else "Insurances"} / {month_name}', True)


class PaymentGlobalAgent(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasPaymentAgentPermission]

    def get(self, request: HttpRequest):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)
        results = self.paginate_queryset(results, request, view=self)
        response = self.get_paginated_response(results)
        return response

    def _get_mapping(self, request: HttpRequest):
        month = self.map_month(request.GET.get("month"))
        if not month:
            return ["id", "agent_name", "year"] + self.get_month_list()
        else:
            return [
                "id",
                "agent_name",
                "year",
                "policies",
                "cancel",
                "no_elegible",
                "nosub",
                "payment",
                "no_payment",
                "paid_members",
                month,
            ]

    def _create_sql(self, request: HttpRequest) -> str:
        query = (
            self.__get_basic_query(request)
            + self.__get_subquery(request)
            + self.apply_filters(request)
            + " group by a.id "
            + self.__apply_ordering(request)
        )
        return query

    def __get_basic_query(self, request: HttpRequest) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        basic_query = f"""Select a.id, a.agent_name as agent, {year} as year """
        month = self.map_month(request.GET.get("month"))
        if month:
            basic_query += f"""
            ,CASE WHEN sq1.policies IS NOT NULL THEN sq1.policies ELSE 0 END as policies,
            CASE WHEN sq3.cancel IS NOT NULL THEN sq3.cancel ELSE 0 END as cancel,
            CASE WHEN sq2.no_elegible IS NOT NULL THEN sq2.no_elegible ELSE 0 END as no_elegible,
            CASE WHEN sq1.nosub IS NOT NULL THEN sq1.nosub ELSE 0 END as no_sub,
            CASE WHEN sq1.payment IS NOT NULL THEN sq1.payment ELSE 0 END as payment,
            CASE WHEN sq1.payment IS NOT NULL AND sq1.policies is not null THEN sq1.policies - sq1.payment ELSE 0 END as no_payment,
            CASE WHEN {month}.paid_members IS NOT NULL THEN {month}.paid_members ELSE 0 END AS paid_members,
            CASE WHEN {month}.com IS NOT NULL THEN {month}.com ELSE 0 END AS {month}
                """
        else:
            for month in self.get_month_list():
                basic_query += f", case when {month}.com is not null then {month}.com else 0 end as {month}"
        basic_query += self.get_agent_filter(request)
        return basic_query

    def get_agent_filter(self, request: HttpRequest):
        self_managed = self.check_none(request.GET.get("self_managed"))
        self_managed_filter = "and ag.self_managed = 1" if self_managed == '1' else "and (ag.self_managed <> 1 or ag.self_managed is null)"
        user = request.user
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        if agent:
            agents = agents.filter(pk=agent.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        filters = "WHERE 1 "
        if not (user.is_admin and not (agent or agency)):
            filters += (
                f" AND a.id in ({self.queryset_to_list(agents, to_string=True)})"
            )
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += f""" and concat(a.agent_name,' ',a.agent_lastname) like '%{search}%'"""

        agent_filter = f" FROM (Select a.id, concat(a.agent_name,' ',a.agent_lastname) agent_name FROM agent a JOIN agency ag ON (a.id_agency=ag.id) {filters} {self_managed_filter} ) a "
        return agent_filter

    def __get_subquery(self, request) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )

        sq_filters = self.get_sq_filters(request)

        def basic_sq(y, m, f):
            return f""" LEFT JOIN (Select ap.id_agent, sum(ap.commission) as com,
            SUM(CASE WHEN ap.commission <> 0 THEN ap.members_number end) as paid_members
            from agent_payments ap where ap.year = {y} and ap.month='{self.inverse_map_month(m)}' {f}
            group by ap.id_agent) {m} on a.id = {m}.id_agent """

        all_sq = ""

        month = self.map_month(request.GET.get("month"))
        insured = self.check_none(request.GET.get("insured"))
        if month:
            month = self.sql_curate_query(month)
            all_sq += basic_sq(year, month, sq_filters)
            m_sq_1, m_sq_2, m_sq_3 = self.__get_monthly_subqueries(
                year, month, insured)
            all_sq += f""" left join ({m_sq_1}) sq1 on a.id= sq1.agent 
                            left join ({m_sq_2}) sq2 on a.id= sq2.agent
                            left join ({m_sq_3}) sq3 on a.id= sq3.agent"""
        else:
            for month in self.get_month_list():
                all_sq += basic_sq(year, month, sq_filters)
        return all_sq

    def get_sq_filters(self, request: HttpRequest) -> str:
        filters = ""
        agent = self.check_none(request.GET.get("agent"))
        insured = self.check_none(request.GET.get("insured"))
        state = self.check_none(request.GET.get("state"))
        if agent:
            filters += f"and ap.id_agent = {self.sql_curate_query(str(agent))} "
        if insured:
            filters += f"and ap.id_insured = {self.sql_curate_query(str(insured))} "
        if state:
            filters += f"and ap.id_state = {self.sql_curate_query(str(state))} "
        return filters

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "agent"
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

    def __get_monthly_subqueries(self, year: str, month: str, insured):
        insured_filter = f" and c.id_insured = {insured}" if insured else ""
        sc1 = f"""
            SELECT
                COUNT(DISTINCT c.id) AS policies,
                COUNT(CASE WHEN c.suscriberid = NULL OR TRIM(c.suscriberid) = '' OR c.suscriberid = 'N/A' THEN c.suscriberid END) AS nosub,
                COUNT(DISTINCT CASE WHEN ap.month = '{self.inverse_map_month(month)}' AND ap.repaid_on is NULL AND ap.id_client IS NOT NULL THEN ap.id_client END) AS payment,
                c.id_agent AS agent
            FROM client
                c
            LEFT JOIN agent_payments ap ON
                c.id = ap.id_client
            WHERE
                SUBSTRING(c.aplication_date, 1, 4) = {year}  {insured_filter} and c.borrado<>1
            GROUP BY
                c.id_agent
        """

        sc2 = f"""
            SELECT
                COUNT(bob_global.id) AS no_elegible,
                c.id_agent AS agent
            FROM
                bob_global
            INNER JOIN client c ON
                c.suscriberid = bob_global.suscriberid
            LEFT JOIN(
                SELECT
                    ap.id_agent,
                    ap.id_client
                FROM
                    agent_payments ap
            ) ap ON c.id= ap.id_client  
            
            WHERE
                bob_global.eleg_commision = 'No' AND SUBSTRING(aplication_date, 1, 4) = {year}  {insured_filter} and c.borrado<>1
            GROUP BY
                agent
        
        """

        sc3 = f"""
            SELECT
                COUNT(bob_global.id) AS cancel,
               	c.id_agent AS agent
            FROM
                bob_global
            INNER JOIN client c ON
                c.suscriberid = bob_global.suscriberid
            LEFT JOIN(
                SELECT
                    ap.id_client,
                    ap.id_agent
                FROM
                    agent_payments ap
            ) ap
            ON
                c.id = ap.id_client
            WHERE
                bob_global.term_date <= CURDATE() AND SUBSTRING(aplication_date, 1, 4) = {year} {insured_filter} and c.borrado<>1
            GROUP BY agent
        """
        return sc1, sc2, sc3

    def apply_filters(self, request: HttpRequest):
        filters = ""
        month = self.map_month(request.GET.get("month"))
        if month:
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" where {month}.com<>0 "
            elif payment and int(payment) == 2:
                filters += f" where {month}.com is NULL or {month}.com=0 "
        return filters


class ExportExcelPaymentGlobalAgent(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalAgent
):
    permission_classes = [HasExportExcelPaymentAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentGlobalAgentSerializer
    xlsx_use_labels = True
    filename = "payment_global_agent.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        month = self.map_month(request.GET.get("month"))
        if month:
            self.serializer_class = ExportPaymentGlobalAgentMonthSerializer
        elif (request.GET.get('year') == 2023 or request.GET.get('year') == '2023'):
            self.serializer_class = JulDecSerializer

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGlobalAgent(PaymentGlobalAgent, PDFCommons):
    permission_classes = [HasExportAgentPaymentPDFPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)

        month = self.map_month(request.GET.get("month"))
        data = [[indx + 1] + list(r[1:]) for indx, r in enumerate(results)]
        if month:
            month_name = month.replace(
                "dicember", "december").capitalize()

            headers = [
                "Index",
                "Agent",
                "Year",
                "Policies",
                "Cancel",
                "No Elegible",
                "No Sub",
                "Payment",
                "No Payment",
                "Paid Members",
                month_name,
            ]
            return self.pdf_create_table(headers, data, A2, f'Payment Global Agent Report / {month_name}', True)
        else:
            headers = [
                "Indx",
                "Agent",
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
            if request.GET.get('year') == 2023 or request.GET.get('year') == '2023':
                data = [[i + 1,  r[1], r[9], r[10], r[11], r[12], r[13], r[14]]
                        for i, r in enumerate(results)
                        ]
                headers = [
                    "Indx",
                    "Agent Name",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
                return self.pdf_create_table(headers, data, A3, 'Payment Global Agent Report')
            return self.pdf_create_table(headers, data, A1, 'Payment Global Agent Report')


class AgentPaymentsDetailsByInsurance(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentAgentPermission]

    def get(self, request: HttpRequest):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(self._get_mapping(request), results)
        return Response(results)

    def _create_sql(self, request):
        month = self.map_month(request.GET.get("month"))
        id_agent = request.GET.get("agent")
        year = self.check_none(request.GET.get(
            "year"), str(date.today().year))

        sql = f"""
            Select 
                ap.id_insured,
                ap.insured_name,
                sum(ap.commission)
            FROM
                agent_payments ap
            WHERE 
                ap.id_agent={id_agent}
                and month='{self.inverse_map_month(month)}'
                and year='{year}'
            GROUP BY 
                ap.id_insured
            ORDER BY 
                ap.commission DESC
        """
        return sql

    def _get_mapping(self, request):
        return ['id_insured', 'insured_name', 'commission']


class ExportExcelAgentPaymentsDetailsByInsurancet(
    XLSXFileMixin, ReadOnlyModelViewSet, AgentPaymentsDetailsByInsurance
):
    permission_classes = [HasExportExcelPaymentAgentPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AgentPaymentsDetailsByInsuranceSerializer
    xlsx_use_labels = True
    filename = "payment_global_agent.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfAgentPaymentsDetailsByInsurance(AgentPaymentsDetailsByInsurance, PDFCommons):
    permission_classes = [HasExportAgentPaymentPDFPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)
        agent = self.select_agent(request.GET.get('agent'), request.user.pk)
        month = self.map_month(request.GET.get("month"))
        data = [[indx + 1] + list(r[1:]) for indx, r in enumerate(results)]
        if month:
            month_name = month.replace(
                "dicember", "december").capitalize()
            headers = [
                "Index",
                "Insurance",
                "Commission"
            ]
            return self.pdf_create_table(headers, data, A4, f"{agent.agent_name} {agent.agent_lastname} / {month_name}", True)
