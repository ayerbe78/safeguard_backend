from ..imports import *
import re


class PaymentGlobalAssistantPerClient(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasPaymentOverrideAssistantPermission]

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
            return ["client", "assistant"] + self.get_month_list()
        else:
            return [
                "client",
                "assistant",
                "year",
                "telephone",
                "effective_date",
                "paid_date",
                "cancel",
                "suscriberid",
                "members_number",
                month,
            ]

    def _create_sql(self, request: HttpRequest) -> str:
        month = self.map_month(request.GET.get("month"))
        payment = self.check_none(request.GET.get("payment"))
        if month and (payment == '2'):
            query = self.__get_no_payment_query(request)
        else:
            query = (
                self.__get_basic_query(request)
                + self.__get_subquery(request)
                + self.apply_filters(request)
                + self.__apply_search(request)
                + " group by fsq.id_assistant, fsq.id_client "
                + self.__apply_ordering(request)
            )
        return query

    def __get_no_payment_query(self, request: HttpRequest) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        insured = self.check_none(request.GET.get("insured"))
        search = self.check_none(request.GET.get("search"), "")
        insured_filter = f"and c.id_insured={insured}" if insured else ""
        mapped_month = self.map_month(request.GET.get("month"))
        user = request.user
        assistant = self.select_assistant(
            request.GET.get("assistant"), user.pk)
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)

        if assistant:
            clients = self.get_assistant_clients(
                assistant.pk, include_deleted=True)
        else:
            clients = self.get_related_clients(
                user.pk, True, ["id", "id_agent"], True)

        if agent:
            agents = agents.filter(pk=agent.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        clients = clients.filter(id_agent__in=self.queryset_to_list(agents))

        client_filter = f" AND c.id in ({self.queryset_to_list(clients, to_string=True)})" if not (
            user.is_admin and not (agent or assistant or agency)) else ""
        inner_client_filter = f" AND pga.id_client in ({self.queryset_to_list(clients, to_string=True)})" if not (
            user.is_admin and not (agent or assistant or agency)) else ""

        sql = f"""
            SELECT
                CONCAT(c.names, " ", c.lastname) AS client,
                CONCAT(
                    a.assistant_name,
                    " ",
                    a.assistant_lastname
                ) AS assistant,
                SUBSTRING(c.aplication_date, 1, 4) AS year,
                c.telephone,
                bob.effective_date,
                bob.paid_date,
                IF(bob.term_date <= {year}, 1, 0) AS cancel,
                c.suscriberid,
                fsq.members_number,
                CASE WHEN fsq.total_commission IS NOT NULL THEN fsq.total_commission ELSE 0.0 END AS {mapped_month}
                
            FROM 
                client c
                LEFT JOIN(
                    SELECT *
                    FROM
                        payments_global_assistant pga
                    WHERE
                        1 AND pga.id_insured = 1 AND pga.month = '{mapped_month}' AND pga.year = '{year}' {inner_client_filter}
                    GROUP BY
                        pga.id_client
                ) fsq ON (c.id=fsq.id_client) 
                
                LEFT JOIN assistant a ON fsq.id_assistant = a.id
                
                LEFT JOIN(
                    SELECT
                        *
                    FROM
                        bob_global
                    WHERE
                        id IN(
                        SELECT
                            MAX(b.id)
                        FROM
                            bob_global b
                        GROUP BY
                            b.suscriberid
                    )
                ) bob ON c.suscriberid = bob.suscriberid
                
            WHERE
                c.borrado <> 1 {client_filter} AND SUBSTRING(c.aplication_date, 1, 4) = '{year}' 
                    AND(fsq.id IS NULL OR fsq.total_commission = 0) 
                    {insured_filter} AND(c.tipoclient = 1 OR c.tipoclient = 3) AND(
                    LOWER(
                        CONCAT(
                            a.assistant_name,
                            ' ',
                            a.assistant_lastname
                        )
                    ) LIKE '%{search.lower()}%' OR LOWER(CONCAT(c.names, ' ', c.lastname)) LIKE '%{search.lower()}%' OR LOWER(c.suscriberid) LIKE '%{search.lower()}%'
                )
            ORDER BY
                {mapped_month},
                client_name
        """
        return sql

    def __get_basic_query(self, request: HttpRequest) -> str:
        basic_query = f"""select concat(c.names," ", c.lastname) as client, 
                        concat(a.assistant_name," ", a.assistant_lastname) as assistant"""
        month = self.map_month(request.GET.get("month"))

        user_id = request.user.pk
        assistants = self.get_related_assistants(user_id, True)
        assistant = self.select_assistant(
            request.GET.get("assistant"), user_id)
        if assistant:
            assistants = assistants.filter(id=assistant.pk)

        if month:
            basic_query += f""",year, sq1.telephone, sq1.effective_date,
                                sq1.paid_date, sq1.cancel, sq1.suscriberid,
                                {month}.members,
                                case when {month}.com is not null then {month}.com else 0.0 end as {month}"""
            assistant_filter = f"""select * from payments_global_assistant pga where pga.month='{month}' and pga.id_assistant in
                            ({self.queryset_to_list(assistants, to_string=True)})"""
        else:
            for month in self.get_month_list():
                basic_query += f", case when sum({month}.com) is not null then sum({month}.com) else 0.0 end as {month}"
                assistant_filter = f"""select * from payments_global_assistant pga where pga.id_assistant in
                            ({self.queryset_to_list(assistants, to_string=True)})"""

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            insured_filter = f"and c.id_insured = {self.sql_curate_query(str(insured))}"
        else:
            insured_filter = ""
        basic_query += f""" from ({assistant_filter}) fsq join client c on (c.id=fsq.id_client {insured_filter}) join assistant a
                        on  a.id=fsq.id_assistant"""
        return basic_query

    def __get_subquery(self, request) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        sq_filters = self.__get_sq_filters(request)

        def basic_sq(y, m, f):
            return f""" left join (select p.id id, sum(p.total_commission) com, sum(p.members_number) members
            from payments_global_assistant p where p.year = {y} and p.month='{m}' {f}
            GROUP BY p.id_client
            ) {m}
            on fsq.id = {m}.id """

        all_sq = ""
        month = self.map_month(request.GET.get("month"))
        if month:
            month = self.sql_curate_query(month)
            all_sq += basic_sq(year, month, sq_filters)
            m_sq_1, m_sq_2 = self.__get_monthly_subqueries(year, month)
            all_sq += f""" join ({m_sq_1}) sq1 on sq1.client=c.id"""
        else:
            for month in self.get_month_list():
                all_sq += basic_sq(year, month, sq_filters)
        return all_sq

    def __get_sq_filters(self, request: HttpRequest) -> str:
        filters = ""
        agent = self.check_none(request.GET.get("agent"))
        insured = self.check_none(request.GET.get("insured"))
        state = self.check_none(request.GET.get("state"))
        if agent:
            filters += f"and p.id_agent = {self.sql_curate_query(str(agent))} "
        if insured:
            filters += f"and p.id_insured = {self.sql_curate_query(str(insured))} "
        if state:
            filters += f"and p.id_state = {self.sql_curate_query(str(state))} "
        return filters

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "client"
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

    def __apply_search(self, request: HttpRequest) -> str:
        filters = ""
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += f""" and (concat(c.names," ", c.lastname) like '%{search}%' 
                        or concat(a.assistant_name," ", a.assistant_lastname) like '%{search}%' or c.suscriberid like '%{search}%') """
        return filters

    def __get_monthly_subqueries(self, year: str, month: str):
        sq1 = f"""Select c.telephone,bob.effective_date,bob.paid_date,IF(bob.term_date<= {year},1,0)
                    as cancel,c.suscriberid,c.id as client FROM client c join (select p.id_assistant,
                    p.id_client from payments_global_assistant p)p on p.id_client=c.id left join bob_global bob on
                    c.suscriberid=bob.suscriberid"""
        sq2 = f"""SELECT pc.index_payment, pc.id_payment as payment FROM payments_control pc WHERE
                    (pc.month={month} or pc.month=0{month}) group by pc.id_payment"""
        return sq1, sq2

    def apply_filters(self, request: HttpRequest):
        year = request.GET.get("year")
        filters = f" WHERE c.borrado <> 1 and SUBSTRING(c.aplication_date,1,4)='{year}' "
        month = self.map_month(request.GET.get("month"))
        if month:
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" and {month}.com<>0 "
            elif payment and int(payment) == 2:
                filters += f" and {month}.com=0 "
        return filters


class PaymentGlobalAssistantPerClientSummary(APIView, AgencyManagement, DirectSql):
    permission_classes = [HasPaymentOverrideAssistantPermission]

    def get(self, request: HttpRequest):
        sql = "select "
        month_sql = ""
        for month in self.get_month_list():
            month_sql += f", sum({month}.com)"
        sql = sql + month_sql[1:]  # To remove first comma (,)
        user_id = request.user.pk
        assistants = self.get_related_assistants(user_id, True)
        assistant = self.select_assistant(
            request.GET.get("assistant"), user_id)
        if assistant:
            assistants = assistants.filter(id=assistant.pk)
        assistant_filter = f"""select * from payments_global_assistant pga where pga.id_assistant in
                            ({self.queryset_to_list(assistants, to_string=True)})"""
        sql += f""" from ({assistant_filter}) fsq join client c on c.id=fsq.id_client join assistant a
                        on  a.id=fsq.id_assistant """
        sql += f""" {self.__get_subquery(request)} {self.__apply_search(request)}"""
        results = self.sql_select_first(sql)
        results = self.sql_map_results(self.get_month_list(), [results])
        return Response(results)

    def __get_subquery(self, request) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        sq_filters = self.__get_sq_filters(request)

        def basic_sq(y, m, f):
            return f""" left join (select p.id id,p.total_commission com
            from payments_global_assistant p where p.year = {y} and p.month='{m}' {f}) {m}
            on fsq.id = {m}.id """

        all_sq = ""
        for month in self.get_month_list():
            all_sq += basic_sq(year, month, sq_filters)
        return all_sq

    def __get_sq_filters(self, request: HttpRequest) -> str:
        filters = ""
        agent = self.check_none(request.GET.get("agent"))
        insured = self.check_none(request.GET.get("insured"))
        state = self.check_none(request.GET.get("state"))
        if agent:
            filters += f"and p.id_agent = {self.sql_curate_query(str(agent))} "
        if insured:
            filters += f"and p.id_insured = {self.sql_curate_query(str(insured))} "
        if state:
            filters += f"and p.id_state = {self.sql_curate_query(str(state))} "
        return filters

    def __apply_search(self, request: HttpRequest) -> str:
        filters = " where c.borrado<>1 "
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += f"""  and concat(c.names," ", c.lastname) like '%{search}%' 
                        or concat(a.assistant_name," ", a.assistant_lastname) like '%{search}%'"""
        return filters


class PaymentAssistantPerClientExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalAssistantPerClient
):
    permission_classes = [HasExportExcelPaymentAssistantPerClientPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentAssistantPerClientExcelSerializer
    xlsx_use_labels = True
    filename = "payment_assistant_client.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        month = self.map_month(request.GET.get("month"))
        if month:
            self.serializer_class = PaymentAssistantPerClientExcelSerializerExtended

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class PaymentAssistantPerClientExportPdf(PaymentGlobalAssistantPerClient, PDFCommons):
    permission_classes = [HasExportPDFPaymentAssistantPerClientPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)

        month = self.map_month(request.GET.get("month"))
        data = [
            [
                indx + 1,
                re.sub(r"\s+", "\n", r[0].strip()),
                r[1].strip().replace(" ", "\n", 1),
            ]
            + list(r[2:])
            for indx, r in enumerate(results)
        ]
        if month:
            month_name = month.replace(
                "dicember", "december").capitalize()
            headers = [
                "Index",
                "Client",
                "Assistant",
                "Year",
                "Telephone",
                "Effective Date",
                "Paid Date",
                "Cancel",
                "Suscriberid",
                "Members Count",
                month_name,
            ]
            return self.pdf_create_table(headers, data, A2, f'Assistant Report / {month_name}', True)
        else:
            headers = [
                "Index",
                "Client",
                "Assistant",
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
                "Dicember",
            ]
            return self.pdf_create_table(headers, data, A2, 'Assistant Report')


class MakeAssistantRepayment(APIView, AgencyManagement):
    permission_classes = [HasPaymentAssistantPermission]

    def post(self, request: HttpRequest):
        with transaction.atomic():
            try:
                entries = self.__new_get_related_payments(request)
            except ValueError as e:
                raise FailedToGenerateReportException(str(e))

            objs = PaymentsGlobalAssistant.objects.bulk_create(
                list(map(lambda e: PaymentsGlobalAssistant(**e), entries))
            )

            return Response({"count": len(objs)}, status=status.HTTP_201_CREATED)

    def __get_related_payments(self, request: HttpRequest):
        user: CustomUser = request.user

        assistant = self.check_none(request.data.get("assistant"))
        insured = self.check_none(request.data.get("insured"))
        month = self.check_none(request.data.get("month"))
        year = self.check_none(request.data.get("year"))
        if not (assistant and insured and month and year):
            raise ValueError(
                "All four: assistant, insured, month, year params are required"
            )

        month = self.map_month(month)
        if month is None:
            raise ValueError("Month Value is wrong")

        assistant = self.select_assistant(assistant, user.pk)
        if not assistant:
            raise ValidationException(f"No such assistant with id {assistant}")

        clients = self.get_assistant_clients(assistant.pk)

        commission = self.check_none(assistant.comition, 0.0)

        old_ones = PaymentsGlobalAssistant.objects.filter(
            id_assistant=int(request.data.get("assistant")),
            id_insured=int(request.data.get("insured")),
            month=self.map_month(int(request.data.get("month"))),
            year=request.data.get("year"),
        ).exclude(total_commission=0).values('id_client', 'indx')
        if old_ones.exists():
            existing_payments = self.queryset_to_list(old_ones, 'id_client')
            max_index = old_ones.latest('indx').get('indx')
            max_index = int(max_index)+1 if max_index else 1
        else:
            existing_payments = []
            max_index = 1
        payments = Payments.objects.filter(
            id_client__in=self.queryset_to_list(clients), fecha=year
        ).exclude(id_client__in=existing_payments).values("id_agent", "id_client", month)
        response = []
        for p in payments:
            if p[month] == 0 or p[month] == '0':
                continue
            client = clients.filter(
                id_agent=p["id_agent"], id=p["id_client"], id_insured=insured
            ).exclude(borrado=1).only("id_insured", "family_menber", "id_state")
            client = client.get() if client.exists() else None
            if not client or client.family_menber == 0 or client.family_menber == '0':
                continue
            old_payment = PaymentsGlobalAssistant.objects.filter(
                id_assistant=int(request.data.get("assistant")), id_client=client.id, month=month, year=year)
            if old_payment:
                old_payment.delete()

            entry = {
                "id_agent": p["id_agent"],
                "id_client": client.pk,
                "id_state": client.id_state,
                "id_insured": client.id_insured,
                "id_assistant": assistant.pk,
                "month": month,
                "year": year,
                "members_number": client.family_menber,
                "indx": max_index,
                "total_commission": client.family_menber * commission
                if client.family_menber and p[month]
                else 0,
            }
            response.append(entry)
        return response

    def __new_get_related_payments(self, request: HttpRequest):
        user: CustomUser = request.user

        assistant = self.check_none(request.data.get("assistant"))
        insured = self.check_none(request.data.get("insured"))
        month = self.check_none(request.data.get("month"))
        year = self.check_none(request.data.get("year"))
        if not (assistant and insured and month and year):
            raise ValueError(
                "All four: assistant, insured, month, year params are required"
            )

        month = self.map_month(month)
        if month is None:
            raise ValueError("Month Value is wrong")

        assistant = self.select_assistant(assistant, user.pk)
        if not assistant:
            raise ValidationException(f"No such assistant with id {assistant}")

        clients = self.get_assistant_clients(assistant.pk)

        commission = self.check_none(assistant.comition, 0.0)

        old_ones = PaymentsGlobalAssistant.objects.filter(
            id_assistant=int(request.data.get("assistant")),
            id_insured=int(request.data.get("insured")),
            month=self.map_month(int(request.data.get("month"))),
            year=request.data.get("year"),
        ).exclude(total_commission=0).values('id_client', 'indx')

        if old_ones.exists():
            existing_payments = self.queryset_to_list(old_ones, 'id_client')
            max_index = old_ones.latest('indx').get('indx')
            max_index = int(max_index)+1 if max_index else 1
        else:
            existing_payments = []
            max_index = 1

        payments = AgentPayments.objects.filter(
            id_client__in=self.queryset_to_list(clients), year=year, month=self.inverse_map_month(month), id_insured=insured
        ).exclude(id_client__in=existing_payments)
        response = []
        for p in payments:
            if p.commission == 0 or p.commission == '0' or p.members_number == 0 or p.members_number == '0':
                continue
            old_payment = PaymentsGlobalAssistant.objects.filter(
                id_assistant=int(request.data.get("assistant")), id_client=p.id_client, month=month, year=year)
            if old_payment:
                old_payment.delete()

            entry = {
                "id_agent": p.id_agent,
                "id_client": p.id_client,
                "id_state": p.id_state,
                "id_insured": p.id_insured,
                "id_assistant": assistant.pk,
                "month": month,
                "year": year,
                "members_number": p.members_number,
                "indx": max_index,
                "total_commission": p.members_number * commission
                if p.members_number and p.commission
                else 0,
            }
            response.append(entry)
        return response
