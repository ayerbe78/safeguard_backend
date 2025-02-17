from calendar import month
from pyexpat import model
from ..imports import *


class PaymentAssistantCommons:
    def apply_filters(self, request: HttpRequest):
        user: CustomUser = request.user
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            result = PaymentsGlobalAssistant.objects.filter(id_insured=insured)
        else:
            result = PaymentsGlobalAssistant.objects.all()
        assistant = self.select_assistant(
            request.GET.get("assistant"), user.pk)
        if assistant:
            result = result.filter(id_assistant=assistant.pk)
        month = self.check_none(request.GET.get("month"))
        if month:
            try:
                result = result.filter(month=self.get_month(month))
            except:
                pass
        year = self.check_none(request.GET.get("year"))
        if year:
            result = result.filter(year=year)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        if agent:
            result = result.filter(id_agent=agent.pk)

        return result

    def apply_search(self, list_dict, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            results = list(
                filter(lambda e: search.lower()
                       in e["client"].names.lower(), list_dict)
            )
        else:
            results = list_dict
        return results


class PaymentsGlobalAssistantViewSet(
    APIView, AgencyManagement, SorterPagination, PaymentAssistantCommons
):
    permission_classes = [HasPaymentAssistantPermission]

    def get(self, request: HttpRequest):

        result = self.apply_filters(request)
        response = result.values()
        clients = Client.objects.filter(
            id__in=self.queryset_to_list(result, "id_client")
        ).only("names", "lastname")
        assistants = Assistant.objects.filter(
            id__in=self.queryset_to_list(result, "id_assistant")
        ).only("assistant_name", "assistant_lastname")
        for r in response:
            try:
                client = clients.get(id=r["id_client"])
                assistant = assistants.get(id=r["id_assistant"])
            except:
                continue
            r["client"] = f"{client.names} {client.lastname}"
            r[
                "assistant"
            ] = f"{assistant.assistant_name} {assistant.assistant_lastname}"

        response = self.apply_search(response, request)
        page = self.order_paginate_list(response, request, "client")
        if page is not None:
            return self.get_paginated_response(page)

        return Response(response)

    def post(self, request: HttpRequest):
        user: CustomUser = request.user

        with transaction.atomic():
            try:
                if self.check_new_payment(request.data.get('month'), request.data.get('year')):
                    entries = self.__new_get_related_payments(request)
                else:
                    entries = self.__get_related_payments(request)

            except ValueError as e:
                raise FailedToGenerateReportException(str(e))

            old_ones = PaymentsGlobalAssistant.objects.filter(
                id_assistant=int(request.data.get("assistant")),
                id_insured=int(request.data.get("insured")),
                month=self.map_month(int(request.data.get("month"))),
                year=request.data.get("year"),
            )
            if old_ones.exists():
                old_ones.delete()

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

        payments = Payments.objects.filter(
            id_client__in=self.queryset_to_list(clients), fecha=year
        ).values("id_agent", "id_client", month)
        response = []
        for p in payments:
            client = clients.filter(
                id_agent=p["id_agent"], id=p["id_client"], id_insured=insured
            ).exclude(borrado=1).only("id_insured", "family_menber", "id_state")
            client = client.get() if client.exists() else None
            if not client:
                continue
                raise ValidationException(
                    f"No such client with id:{p['id_client']} and agent id: {p['id_agent']} in insured with id {insured}"
                )
            entry = {
                "id_agent": p["id_agent"],
                "id_client": client.pk,
                "id_state": client.id_state,
                "id_insured": client.id_insured,
                "id_assistant": assistant.pk,
                "month": month,
                "year": year,
                "members_number": client.family_menber,
                "indx": 1,
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

        payments = AgentPayments.objects.filter(
            id_client__in=self.queryset_to_list(clients), year=year, month=self.inverse_map_month(month), id_insured=insured
        )
        response = []
        for p in payments:
            entry = {
                "id_agent": p.id_agent,
                "id_client": p.id_client,
                "id_state": p.id_state,
                "id_insured": p.id_insured,
                "id_assistant": assistant.pk,
                "month": month,
                "year": year,
                "members_number": p.members_number,
                "indx": 1,
                "total_commission": p.members_number * commission
                if p.members_number and p.commission != 0
                else 0,
            }
            response.append(entry)
        return response


class PaymentGlobalAssistantYearly(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasPaymentAssistantPermission]

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
            return ["id", "assistant"] + self.get_month_list()
        else:
            return [
                "id",
                "assistant",
                "policies",
                "cancel",
                "no_elegible",
                "nosub",
                "payment",
                "no_payment",
                "total_members",
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
        basic_query = f"""select a.id,concat(a.assistant_name," ", a.assistant_lastname)as assistant"""
        month = self.map_month(request.GET.get("month"))
        if month:
            basic_query += f""",case when sq1.policies is not null then sq1.policies else 0 end,
                case when sq3.cancel is not null then sq3.cancel else 0 end,
                case when sq2.no_elegible is not null then sq2.no_elegible else 0 end,
                case when sq1.nosub is not null then sq1.nosub else 0 end,
                case when sq1.payment is not null then sq1.payment else 0 end,
                case when sq1.no_payment is not null then sq1.no_payment else 0 end,
                case when sq1.total_members is not null then sq1.total_members else 0 end,
                case when {month}.paid_members is not null then {month}.paid_members else 0 end as paid_members,
                case when {month}.com is not null then {month}.com else 0 end as {month}
                """
        else:
            for month in self.get_month_list():
                basic_query += f", case when {month}.com is not null then {month}.com else 0 end as {month}"
        basic_query += self.get_assistant_filter(request)
        return basic_query

    def get_assistant_filter(self, request: HttpRequest):
        user_id = request.user.pk
        assistants = self.get_related_assistants(user_id, True)
        assistant = self.select_assistant(
            request.GET.get("assistant"), user_id)
        if assistant:
            assistants = assistants.filter(id=assistant.pk)
        assistant_filter = f"select * from assistant a where a.id in ({self.queryset_to_list(assistants, to_string=True)})"
        search = self.check_none(request.GET.get("search"))
        if search:
            assistant_filter += f""" and concat(a.assistant_name," ", a.assistant_lastname) like '%{search}%'"""
        assistant_filter = f" from ({assistant_filter}) a "
        return assistant_filter

    def __get_subquery(self, request) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )

        sq_filters = self.get_sq_filters(request)

        def basic_sq(y, m, f):
            return f""" left join (select p.id_assistant id,sum(p.total_commission) com,
            SUM(CASE WHEN p.total_commission <> 0 THEN p.members_number end) as paid_members
            from payments_global_assistant p join client c on p.id_client = c.id where c.borrado<>1 and  p.year = {y} and p.month='{m}' {f}
            group by p.id_assistant) {m} on a.id = {m}.id """

        all_sq = ""

        month = self.map_month(request.GET.get("month"))
        insured = self.check_none(request.GET.get("insured"))
        if month:
            month = self.sql_curate_query(month)
            all_sq += basic_sq(year, month, sq_filters)
            m_sq_1, m_sq_2, m_sq_3 = self.__get_monthly_subqueries(
                year, month, insured)
            all_sq += f""" left join ({m_sq_1}) sq1 on sq1.assistant=a.id
                            left join ({m_sq_2}) sq2 on sq2.assistant=a.id
                            left join ({m_sq_3}) sq3 on sq3.assistant=a.id"""
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
            filters += f"and p.id_agent = {self.sql_curate_query(str(agent))} "
        if insured:
            filters += f"and p.id_insured = {self.sql_curate_query(str(insured))} "
        if state:
            filters += f"and p.id_state = {self.sql_curate_query(str(state))} "
        return filters

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "assistant"
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
        sc1 = f"""Select COUNT(c.id) as policies, COUNT(CASE WHEN  c.suscriberid =null or trim(c.suscriberid) = ''
            or c.suscriberid = 'N/A' THEN c.suscriberid END)as nosub,
            count(CASE when p.month='{month}' and p.total_commission<>0 then p.id end) as payment,
            count(CASE when p.month='{month}' and p.total_commission=0 then p.id end) as no_payment,
            p.id_assistant as assistant,
            sum(p.members_number) as total_members FROM client c inner join payments_global_assistant p on c.id=p.id_client WHERE
            p.year={year} AND p.month='{month}' AND c.borrado <> 1 {insured_filter} group by p.id_assistant"""

        sc2 = f"""SELECT COUNT(bob_global.id) as no_elegible, p.id_assistant as assistant
            FROM bob_global INNER JOIN client c ON c.suscriberid = bob_global.suscriberid join
            (select p.id_assistant, p.id_client from payments_global_assistant p) p on p.id_client = c.id
            WHERE c.borrado <> 1 AND bob_global.eleg_commision = 'No'
            AND SUBSTRING(aplication_date,1,4) = {year} {insured_filter} group by assistant"""

        sc3 = f"""SELECT COUNT(bob_global.id) as cancel, p.id_assistant as assistant
            FROM bob_global INNER JOIN  client c ON c.suscriberid = bob_global.suscriberid join
            (select p.id_client, p.id_assistant from payments_global_assistant p) p
            on p.id_client=c.id WHERE c.borrado <> 1 AND bob_global.term_date <= CURDATE()
            AND SUBSTRING(aplication_date,1,4) = {year} {insured_filter} group by assistant"""

        return sc1, sc2, sc3

    def apply_filters(self, request: HttpRequest):
        filters = ""
        month = self.map_month(request.GET.get("month"))
        if month:
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" where {month}.com<>0 "
            elif payment and int(payment) == 2:
                filters += f" where ({month}.com is null or {month}.com=0)"
        return filters


class PaymentGlobalAssistantSummary(APIView, PaymentCommons):
    def get(self, request: HttpRequest):
        filters = self._apply_filters(request)
        sql = f"""
                SELECT
                    p.indx,
                    COUNT(CASE WHEN p.total_commission <> 0 THEN 1 END),
                    SUM(p.total_commission)
                FROM
                    payments_global_assistant p
                JOIN assistant a on p.id_assistant=a.id
                
                WHERE 1 {filters} 
                GROUP BY
                    p.indx
                """
        response = self.sql_select_all(
            sql, ["indx", "count", "commission"])
        return Response(response)

    def _apply_filters(self, request: HttpRequest):
        user = request.user
        filters = ""
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        filters += f" and p.year={year} "
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            filters += f" AND p.id_insured={insured} "
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        if agent:
            agents = agents.filter(id=agent.pk)
        assistant = self.select_assistant(
            request.GET.get("assistant"), user.pk)
        if assistant:
            agents = agents.filter(id_assistant=assistant.pk)
            filters += f" and p.id_assistant = {assistant.id}"

        if not (user.is_admin and not (agent or assistant)):
            filters += (
                f" AND p.id_agent in ({self.queryset_to_list(agents, to_string=True)})"
            )

        month = self.check_none(request.GET.get("month"))
        if month:
            month = self.map_month(int(month))
            filters += f" and p.month='{month}' "
        payment = self.check_none(request.GET.get("payment"))
        if payment and int(payment) == 1:
            filters += f" AND p.total_commission<>0 "
        elif payment and int(payment) == 2:
            filters += f" AND p.total_commission=0 "
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += (
                f"""
                 and concat(a.assistant_name,' ',a.assistant_lastname) like '%{search}%'
                            
                """
            )

        return filters


class ReportPaymentAssistantSummaryDetails(
    PaymentGlobalAssistantSummary, LimitOffsetPagination
):
    def get(self, request):
        primary_results = self.get_entries(request)
        total_paid = 0
        for p in primary_results:
            try:
                total_paid += float(p["comission"])
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
        query = f"""
            SELECT
                concat(a.agent_name,' ', a.agent_lastname),
                concat(c.names, ' ', c.lastname ),
                i.names,
                a.npn,
                c.suscriberid,
                c.family_menber,
                c.aplication_date,
                p.month,
                p.total_commission as commission
            FROM
                payments_global_assistant p
            JOIN agent a ON
                p.id_agent = a.id 
            JOIN insured i on (p.id_insured=i.id)
            JOIN client c on (p.id_client=c.id)
            WHERE 1 {filters} AND p.indx = {index} and c.borrado <> 1 and SUBSTRING(c.aplication_date,1,4) ='{year}'
        """
        primary_results = self.sql_select_all(
            query, ["agent_name", "client_name", "insured", "npn", "suscriberid", "family_menber", "aplication_date", "month", "comission"])

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


class ExportExcelPaymentAssistantSummaryDetails(
    XLSXFileMixin, ReadOnlyModelViewSet, ReportPaymentAssistantSummaryDetails
):
    permission_classes = [HasExportExcelPaymentGloabalAssistantPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentAssistantSummaryDetailsExcelSerializer
    xlsx_use_labels = True
    filename = "payment_agency_details.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        results = self.get_entries(request)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGloabalAssistantDetails(ReportPaymentAssistantSummaryDetails, PDFCommons):
    permission_classes = [HasExportPDFPaymentGloabalAssistantPermission]

    def get(self, request):
        results = self.get_entries(request)
        data = [
            [
                i + 1,
                r.get("agent_name"),
                r.get("client_name"),
                r.get("insured"),
                r.get("npn"),
                r.get("suscriberid"),
                r.get("family_menber"),
                r.get("aplication_date"),
                r.get("month"),
                r.get("comission")
            ]
            for i, r in enumerate(results)
        ]
        headers = [
            "Indx",
            "Agent",
            "Client",
            "Insurance",
            "NPN",
            "Suscriber ID",
            "Members",
            "Application Date",
            "Month",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A2, 'Assistant Report', True)


class DataForPaymentsGlobalAssistant(APIView, AgencyManagement):
    permission_classes = [HasPaymentAssistantPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "agents", "assistants", "insurances"))


class SingleAssistantMonthPayment(APIView, DashboardCommons):
    permission_classes = [IsAssistantAndAdmin]

    def get(self, request: HttpRequest):
        user_id = self.dash_get_alternative_user(request)
        assistant_id = self.current_is("assistant", user_id)
        result = None
        if assistant_id:
            month = self.map_month(date.today().month)
            year = date.today().year
            result = PaymentsGlobalAssistant.objects.filter(
                id_assistant=assistant_id, year=year, month=month
            ).aggregate(Sum("total_commission"))
            result = result.get("total_commission__sum")
        return Response(data={"result": result if result else 0.0})


class ExportExcelPaymentGloabalAssistatnt(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalAssistantYearly
):
    permission_classes = [HasExportExcelPaymentGloabalAssistantPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentsGlobalAssistantExcelSerializer
    xlsx_use_labels = True
    filename = "payment_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        month = self.map_month(request.GET.get("month"))
        if month:
            self.serializer_class = PaymentsGlobalAssistantExcelSerializerExtended

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGloabalAssistatnt(PaymentGlobalAssistantYearly, PDFCommons):
    permission_classes = [HasExportPDFPaymentGloabalAssistantPermission]

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
                "Assistant",
                "Policies",
                "Cancel",
                "No Elegible",
                "No Sub",
                "Payment",
                "No Payment",
                "Total Members",
                "Paid Members",
                month_name,
            ]
            return self.pdf_create_table(headers, data, A2, f'Assistant Report / {month_name}', True)
        else:
            headers = [
                "Index",
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
            return self.pdf_create_table(headers, data, A3, 'Assistant Report')
