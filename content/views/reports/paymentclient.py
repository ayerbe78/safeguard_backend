from ..imports import *


class PaymentGlobalCommons(AgencyManagement, DirectSql):
    def get_entries(self, request: HttpRequest):
        user: CustomUser = request.user
        filters = self.apply_filters(request)
        order = self.__apply_ordering(request)
        month = self.check_none(request.GET.get("month"))
        year = self.check_none(request.GET.get("year"))
        if not month:
            sql = f"""Select a.agent_name,a.agent_lastname,c.names,c.lastname, p.fecha,
                p.january,p.february,p.march,p.april,p.may,p.june,
                p.july,p.august,p.september,p.october,p.november,p.dicember,p.id_client,p.id_agent, p.id
                from payments p {'left' if user.is_admin else 'inner'} join agent a on p.id_agent=a.id
                {'left' if user.is_admin else 'inner'} join client c on (p.id_client=c.id
                {'' if user.is_admin else 'and c.borrado<>1'}) where 1 {filters}
                group by p.id_agent, p.id_client {order}"""
            results = self.sql_select_all(sql)
        else:
            sc1, sc2 = self._get_subqueries(
                year, month, user.is_admin, request)
            if (year == '2023' or year == 2023):
                sql = f"""Select a.agent_name,a.agent_lastname,c.names,c.lastname, p.fecha,
                    sc2.comm as january,sc2.comm as february,sc2.comm as march,sc2.comm as april,
                    sc2.comm as may,sc2.comm as june, sc2.comm as july,sc2.comm as august, sc2.comm as
                    september, sc2.comm as october,sc2.comm as november,sc2.comm as dicember,
                    p.id_client,p.id_agent, p.id, c.telephone,c.effective_date,c.paid_date,c.cancel,
                    c.suscriberid,sc2.index_payment, members
                    from payments p {'left' if user.is_admin else 'inner'} join agent a on p.id_agent=a.id
                    {'left' if user.is_admin else 'inner'} join ({sc1}) c on 
                    (p.id_client=c.id)
                    left join ({sc2})sc2 on p.id=sc2.payment
                    where 1 {filters} group by p.id_agent,p.id_client {order}"""
            else:
                sql = f"""Select a.agent_name,a.agent_lastname,c.names,c.lastname, p.fecha,
                    p.january,p.february,p.march,p.april,
                    p.may,p.june, p.july,p.august, p.september, p.october,p.november,p.dicember,
                    p.id_client,p.id_agent, p.id, c.telephone,c.effective_date,c.paid_date,c.cancel,
                    c.suscriberid, 1 as index_payment, members
                    from payments p {'left' if user.is_admin else 'inner'} join agent a on p.id_agent=a.id
                    {'left' if user.is_admin else 'inner'} join ({sc1}) c on 
                    (p.id_client=c.id)
                    
                    where 1 {filters} group by p.id_agent,p.id_client {order}"""
            results = self.sql_select_all(sql)
        return results

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "c.names"
    ) -> str:
        pass
        order = ""
        default = f"order by {default_order}, c.lastname"
        order_field = self.check_none(request.GET.get("order"))
        desc = self.check_none(request.GET.get("desc"))
        if order_field:
            if order_field == "agent":
                order += f"order by a.agent_name"
            elif order_field == "client_name":
                order += f"order by c.names"
            else:
                order += f"order by {self.sql_curate_query(order_field)}"
            if desc:
                order += f" desc"
            order += " ,c.names"
        else:
            order = default

        return order

    def _get_subqueries(self, year: str, month: str, is_admin: bool, request):
        sq1 = f"""Select c.names,c.lastname,c.telephone,bob.effective_date,bob.paid_date,IF(bob.term_date<= {year},1,0)
                    as cancel,c.suscriberid,c.id, c.family_menber as members FROM client c left join 

                    ( SELECT
                            b1.*
                        FROM
                            bob_global b1
                        JOIN (
                            SELECT
                                suscriberid,
                                MAX(term_date) AS max_term_date
                            FROM
                                bob_global
                            GROUP BY
                                suscriberid
                        ) b2 ON b1.suscriberid = b2.suscriberid AND b1.term_date = b2.max_term_date
                    ) 
                    bob on
                    c.suscriberid=bob.suscriberid 
                    
                    where SUBSTRING(c.aplication_date,1,4)='{year}' and c.borrado<>1
                    {'' if is_admin else 'and c.borrado<>1'} group by c.id"""
        repayment = self.check_none(request.GET.get("repayment"), 0)
        if int(repayment) == 1:
            filter = f" and pc.index_payment > 1 "
        elif int(repayment) == 2:
            filter = f" and pc.index_payment = 1 "
        else:
            filter = ""
        sq2 = f"""SELECT max(pc.index_payment) index_payment, pc.id_payment payment,
                    sum(pc.commision) comm FROM payments_control pc WHERE pc.month={month}
                    and pc.year_made = {year} {filter} group by pc.id_payment"""
        return sq1, sq2

    def map_results(self, results: list) -> list:
        response = []
        for el in results:
            response.append(
                {
                    "agent_name": self.check_none(el[0], "")
                    + " "
                    + self.check_none(el[1], ""),
                    "client_name": self.check_none(el[2], "")
                    + " "
                    + self.check_none(el[3], ""),
                    "fecha": el[4],
                    "january": el[5],
                    "february": el[6],
                    "march": el[7],
                    "april": el[8],
                    "may": el[9],
                    "june": el[10],
                    "july": el[11],
                    "august": el[12],
                    "september": el[13],
                    "october": el[14],
                    "november": el[15],
                    "dicember": el[16],
                    "id_client": el[17],
                    "id_agent": el[18],
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
                    "client_name": self.check_none(el[2], "")
                    + " "
                    + self.check_none(el[3], ""),
                    "fecha": el[4],
                    "january": el[5],
                    "february": el[6],
                    "march": el[7],
                    "april": el[8],
                    "may": el[6],
                    "june": el[10],
                    "july": el[11],
                    "august": el[12],
                    "september": el[13],
                    "october": el[14],
                    "november": el[15],
                    "dicember": el[16],
                    "id_client": el[17],
                    "id_agent": el[18],
                    "telephone": el[20],
                    "effective_date": el[21],
                    "paid_date": el[22],
                    "cancel": el[23],
                    "suscriberid": el[24],
                    "indx_payment": el[25] if el[25] else 1,
                    "members": el[26],
                }
            )
        return response

    def apply_filters(self, request: HttpRequest) -> str:
        user: CustomUser = request.user
        filters = " "

        year = self.check_none(request.GET.get("year"), str(date.today().year))
        filters += f"and p.fecha={year}"

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

        if not (user.is_admin and not (agent or assistant or agency)):
            filters += f" AND p.id_client in ({self.queryset_to_list(clients, to_string=True)})"

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            filters += f""" AND p.id_client in (Select id from client where borrado<>1 
            and SUBSTRING(aplication_date,1,4)='{year}' and id_insured={insured})"""

        month = self.map_month(request.GET.get("month"))
        if month:
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                filters += f" AND p.{month}<>0 "
            elif payment and int(payment) == 2:
                filters += f" AND p.{month}=0 "
            repayment = self.check_none(request.GET.get("repayment"), 0)
            if int(repayment) == 1:
                filters += f" AND sc2.index_payment > 1 "
            elif int(repayment) == 2:
                filters += f" AND sc2.index_payment = 1 "

        search = self.check_none(request.GET.get("search"))
        if search:
            filters += f""" and (concat(a.agent_name,' ',a.agent_lastname) like '%{search}%'
                            or concat(c.names,' ',c.lastname) like '%{search}%' 
                            OR c.suscriberid like '%{search}%'
                            )"""

        return filters


class ReportPaymentGlobal(
    APIView, PaymentGlobalCommons, LimitOffsetPagination, DirectSql
):
    permission_classes = [HasPaymentClientPermission]

    def get(self, request: HttpRequest):
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)

        month = self.check_none(request.GET.get("month"))
        if not month:
            results = self.map_results(results)
            serializer = PaymentClientSerializerExtended(results, many=True)
        else:
            results = self.map_results_extended(results)
            serializer = PaymentClientMonthSerializerExtended(
                results, many=True)

        response = self.get_paginated_response(serializer.data)
        return response


class PaymentGlobalClient(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasPaymentClientPermission]

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
            return ["agent_name", "client_name", "id_client", "id_agent", "year"] + self.get_month_list()
        else:
            return [
                "agent_name",
                "client_name",
                "id_client",
                "id_agent",
                "year",
                "members_number",
                "telephone",
                "effective_date",
                "paid_date",
                "cancel",
                "suscriberid",
                "payment_index",
                "repaid_on",
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
                + " group by c.id_agent, c.id, c.id_insured"
                + self.__apply_ordering(request)
            )
        return query

    def __get_no_payment_query(self, request: HttpRequest) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        insured = self.check_none(request.GET.get("insured"))
        month = self.check_none(request.GET.get("month"))
        search = self.check_none(request.GET.get("search"), "")
        insured_filter = f"and c.id_insured={insured}" if insured else ""
        filters = self._get_sq_filters(request)
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

        query = (f"""
                Select
                    concat(a.agent_name,' ',a.agent_lastname) as agent_name,
                    concat(c.names,' ', c.lastname) as client_name,
                    c.id,
                    c.id_agent,
                    SUBSTRING(c.aplication_date,1,4) as year,
                    ap.members_number,
                    c.telephone,
                    bob.effective_date,
                    bob.paid_date,
                    IF(bob.term_date <= {year}, 1, 0) AS cancel,
                    c.suscriberid,
                    ap.payment_index,
                    ap.repaid_on,
                    case when ap.commission is not null then ap.commission else 0.0 end as {mapped_month}
                FROM 
                    client c 
                    left join 
                    (
                        Select * from agent_payments ap where 1 {filters} 
                            AND CAST(SUBSTRING_INDEX(ap.info_month, '/', 1) AS UNSIGNED) = {month}
                            AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(ap.info_month, '/', -1), ' ', 1) AS UNSIGNED) = {year}
                        group by ap.id_client
                    ) ap  on c.id=ap.id_client
                    join agent a on c.id_agent=a.id
                    JOIN(
                         SELECT 
                            b1.*
                        FROM
                            bob_global b1
                        JOIN (
                            SELECT
                                suscriberid,
                                MAX(term_date) AS max_term_date
                            FROM
                                bob_global
                            GROUP BY
                                suscriberid
                        ) b2 ON b1.suscriberid = b2.suscriberid AND b1.term_date = b2.max_term_date
                    ) bob ON  c.suscriberid = bob.suscriberid
                WHERE
                    c.borrado<>1 and SUBSTRING(c.aplication_date,1,4)={year} and c.aplication_date<='{year}-{month}-01' and (ap.id is NULL or ap.repaid_on is not null) {client_filter}
                    {insured_filter} and (tipoclient=1 or tipoclient=3) 
                    and (LOWER(concat(a.agent_name,' ',a.agent_lastname)) like '%{search.lower()}%'
                                            or LOWER(concat(c.names,' ',c.lastname)) like '%{search.lower()}%' OR LOWER(c.suscriberid) LIKE '%{search.lower()}%')
        """) + self.__apply_ordering(request)
        return query

    def __get_basic_query(self, request: HttpRequest) -> str:
        basic_query = f"""SELECT
                            c.agent_name as agent,
                            c.client_name as client,
                            c.id,
                            c.id_agent,
                            c.year
                           
                        """
        month = self.map_month(request.GET.get("month"))

        if month:
            basic_query += f"""  
                                ,
                                {month}.members_number,
                                sq1.telephone,
                                sq1.effective_date,
                                sq1.paid_date,
                                sq1.cancel,
                                sq1.suscriberid,
                                c.payment_index,
                                c.repaid_on,
                                case when {month}.com is not null then {month}.com else 0.0 end as {month}"""
        else:
            for month in self.get_month_list():
                basic_query += f", case when sum({month}.com) is not null then sum({month}.com) else 0.0 end as {month}"

        return basic_query

    def __get_subquery(self, request) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        sq_filters = self._get_sq_filters(request)
        self_managed = self.check_none(request.GET.get("self_managed"))
        self_managed_filter = "and ag.self_managed = 1" if self_managed == '1' else "and (ag.self_managed <> 1 or ag.self_managed is null)"

        def basic_sq(y, m, f):
            return f""" 
                LEFT JOIN(
                    SELECT
                        ap.id_client as client,
                        ap.id_agent as agent,
                        ap.id_insured as insured,
                        sum(ap.members_number) as members_number,
                        sum(ap.commission) com
                    FROM
                        agent_payments ap
                    WHERE
                        ap.year = {y} AND ap.month = '{self.inverse_map_month(month)}' {f}
                    GROUP BY
                        ap.id_client,
                        ap.id_agent,
                        ap.id_insured
                ) {m} 
                ON c.id = {m}.client and c.id_agent={m}.agent and c.id_insured={m}.insured
            """

        all_sq = ""
        month = self.map_month(request.GET.get("month"))
        if month:
            all_sq += f"""
            FROM
                (
                    Select 
                        ap.id_client as id, ap.id_agent,ap.id_insured, ap.agent_name, cl.client_name, ap.year, ap.suscriberid, ap.members_number, max(ap.payment_index) as payment_index, ap.repaid_on
                    FROM 
                        agent_payments ap left join (Select id, concat(names,' ',lastname) as client_name from  client) cl on (ap.id_client=cl.id) JOIN agent a ON (ap.id_agent = a.id) JOIN agency ag ON (a.id_agency=ag.id)
                    WHERE  ap.year = {year} and ap.repaid_on is NULL AND ap.month = {self.inverse_map_month(month)} {sq_filters}  
                    {self_managed_filter}  {self.__apply_search(request)}
                    GROUP by ap.id_client,ap.id_agent, ap.id_insured
                ) c
            """
            month = self.sql_curate_query(month)
            all_sq += basic_sq(year, month, sq_filters)
            m_sq_1 = self.__get_monthly_subqueries(year, month)
            all_sq += f"""left join ({m_sq_1}) sq1 on c.id=sq1.id"""
        else:
            all_sq += f"""
            FROM
                (
                    Select 
                        ap.id_client as id, ap.id_agent,ap.id_insured, ap.agent_name, cl.client_name, ap.year, ap.suscriberid, ap.members_number
                    FROM 
                        agent_payments ap left join (Select id, concat(names,' ',lastname) as client_name from  client) cl on (ap.id_client=cl.id)
                        JOIN agent a ON (ap.id_agent = a.id) JOIN agency ag ON (a.id_agency=ag.id)
                    WHERE  ap.year = {year} and ap.repaid_on is NULL  {sq_filters}  {self_managed_filter}  {self.__apply_search(request)}
                    GROUP by ap.id_client,ap.id_agent, ap.id_insured
                ) c
            """
            for month in self.get_month_list():
                all_sq += basic_sq(year, month, sq_filters)
        return all_sq

    def _get_sq_filters(self, request: HttpRequest) -> str:
        user = request.user
        filters = ""
        insured = self.check_none(request.GET.get("insured"))
        state = self.check_none(request.GET.get("state"))

        repayment = self.check_none(request.GET.get("repayment"))

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

        if not (user.is_admin and not (agent or assistant or agency)):
            filters += f" AND ap.id_client in ({self.queryset_to_list(clients, to_string=True)})"
        if insured:
            filters += f"and ap.id_insured = {self.sql_curate_query(str(insured))} "
        if state:
            filters += f"and ap.id_state = {self.sql_curate_query(str(state))} "

        if repayment and request.GET.get("payment") != '2':
            if repayment == 1 or repayment == '1':
                filters += f"and ap.payment_index<>1  "
            if repayment == 2 or repayment == '2':
                filters += f"and ap.payment_index = 1  "
            filters+" and ap.repaid_on is null "
        return filters

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "client_name"
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
            filters += f""" and (LOWER(ap.agent_name) like '%{search.lower()}%'
                        or LOWER(ap.client_name) like '%{search.lower()}%' or LOWER(ap.suscriberid) like '%{search.lower()}%') """
        return filters

    def __get_monthly_subqueries(self, year: str, month: str):
        sq1 = f"""
                SELECT
                    c.telephone,
                    bob.effective_date,
                    bob.paid_date,
                    IF(bob.term_date <= {year}, 1, 0) AS cancel,
                    c.suscriberid,
                    c.id
                FROM 
                    client c
                    LEFT JOIN(
                       SELECT
                            b1.*
                        FROM
                            bob_global b1
                        JOIN (
                            SELECT
                                suscriberid,
                                MAX(term_date) AS max_term_date
                            FROM
                                bob_global
                            GROUP BY
                                suscriberid
                        ) b2 ON b1.suscriberid = b2.suscriberid AND b1.term_date = b2.max_term_date
                    )bob ON  c.suscriberid = bob.suscriberid
                GROUP BY
                    c.id
        """
        return sq1


class PaymentGlobalSummary(APIView, PaymentGlobalCommons):
    permission_classes = [HasPaymentClientPermission]

    def get(self, request: HttpRequest):
        user = request.user
        filters = self.apply_filters(request)
        month = self.check_none(request.GET.get("month"))
        if month:
            year = self.check_none(request.GET.get("year"))
            _, sc2 = self._get_subqueries(year, month, user.is_admin, request)
            sql = f"""Select sum(sc2.comm),sum(sc2.comm),sum(sc2.comm),sum(sc2.comm),sum(sc2.comm),sum(sc2.comm),sum(sc2.comm)
                    ,sum(sc2.comm),sum(sc2.comm),sum(sc2.comm),sum(sc2.comm),sum(sc2.comm)
                    from payments p {'left' if user.is_admin else 'inner'} join agent a on 
                    p.id_agent=a.id {'left' if user.is_admin else 'inner'} join client c on
                    (p.id_client=c.id {'' if user.is_admin else 'and c.borrado<>1'})
                    left join ({sc2})sc2 on p.id=sc2.payment
                    where 1 {filters}"""
        else:
            sql = f"""Select sum(p.january),sum(p.february),sum(p.march),sum(p.april),sum(p.may),
                    sum(p.june),sum(p.july),sum(p.august),sum(p.september),sum(p.october),
                    sum(p.november),sum(p.dicember) from payments p {'left' if user.is_admin else 'inner'} join agent a on 
                    p.id_agent=a.id {'left' if user.is_admin else 'inner'} join client c on
                    (p.id_client=c.id {'' if user.is_admin else 'and c.borrado<>1'}) where 1 {filters}"""
        response = self.sql_select_first(sql)
        response = self.sql_map_results(self.get_month_list(), [response])
        if month:
            str_month = self.map_month(month)
            response = [{str_month: e.get(str_month)} for e in response]
        return Response(response)


class PaymentGlobalClientSummary(PaymentGlobalClient):
    permission_classes = [HasPaymentClientPermission]

    def get(self, request: HttpRequest):
        filters = self._get_sq_filters(request)
        month = self.check_none(request.GET.get("month"))
        year = self.check_none(request.GET.get("year"))
        self_managed = self.check_none(request.GET.get("self_managed"))
        self_managed_filter = "and ag.self_managed = 1" if self_managed == '1' else "and (ag.self_managed <> 1 or ag.self_managed is null)"
        if month:
            string_month = self.map_month(month)
            sql = f"""
            SELECT
                SUM(ap.members_number) as members , SUM(ap.commission) AS {string_month}
            FROM
                agent_payments ap
                JOIN agent a ON (ap.id_agent = a.id) JOIN agency ag ON (a.id_agency=ag.id)
            WHERE
                ap.year = '{year}' and ap.commission<>0 AND ap.month = '{self.inverse_map_month(string_month)}' {filters} {self_managed_filter}
            """
            response = self.sql_select_first(sql)
            payment = self.check_none(request.GET.get("payment"), 0)
            response = [{
                'Paid Members': response[0] if payment != '2' and payment != 2 else 0,
                'Commission': response[1] if payment != '2' and payment != 2 else 0
            }]
        else:
            sql = "Select "
            for mon in self.get_month_list():
                sql += f" {mon}.com as {mon},"
            sql = sql[:-1]
            sql += " FROM "
            for mon in self.get_month_list():
                sql += f" (Select sum(ap.commission) as com FROM agent_payments ap WHERE ap.year='{year}' {filters} and ap.month='{self.inverse_map_month(mon)}') {mon},"
            sql = sql[:-1]
            response = self.sql_select_first(sql)
            response = self.sql_map_results(self.get_month_list(), [response])
        return Response(response)


class DataForPaymentGlobalClient(APIView, AgencyManagement):
    permission_classes = [HasPaymentClientPermission]

    def get(self, request):
        user = request.user
        return Response(
            self.get_selects(user.pk, "agents", "assistants",
                             "insurances", "agencies")
        )


class ExportExcelPaymentGlobal(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalCommons
):
    permission_classes = [HasExportExcelPaymentClientPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentClientSerializerExtended
    xlsx_use_labels = True
    filename = "payment_agent.xlsx"
    xlsx_ignore_headers = ["id_client", "id_agent", "indx_payment"]

    def list(self, request):
        results = self.get_entries(request)

        month = self.check_none(request.GET.get("month"))
        if not month:
            results = self.map_results(results)
        else:
            self.serializer_class = ExportPaymentClientMonthSerializerExtended
            month = self.map_month(request.GET.get("month"))
            context = {"request": request, "month": month}
            results = self.map_results_extended(results)
            serializer = self.get_serializer(
                results, many=True, context=context)
            return Response(serializer.data)

        if request.GET.get('year') == 2023 or request.GET.get('year') == '2023':
            self.serializer_class = JanJunClientSerializer
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGlobal(APIView, PaymentGlobalCommons, PDFCommons):
    permission_classes = [HasExportClientPaymentPDFPermission]

    def get(self, request):
        results = self.get_entries(request)
        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))

        if not month:
            data = [
                [i + 1, (r[0] + "\n" if r[0] else "\n") + (r[1] if r[1]
                                                           else ""), r[2] + "\n" + r[3]] + list(r[4:-3])
                for i, r in enumerate(results)
            ]
            headers = [
                "Indx",
                "Agent Name",
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
            if (request.GET.get('year') == 2023 or request.GET.get('year') == '2023'):
                data = [[i + 1, (r[0] + "\n" if r[0] else "\n") + (r[1] if r[1] else ""), r[2] + "\n" + r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]]
                        for i, r in enumerate(results)
                        ]
                headers = [
                    "Indx",
                    "Agent Name",
                    "Client Name",
                    "Year",
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                ]
                return self.pdf_create_table(headers, data, A3, f'Report for {insured[0].names if insured else "Insurances"}')
            return self.pdf_create_table(headers, data, A1, f'Report for {insured[0].names if insured else "Insurances"}')
        else:
            data = [
                [i + 1, (r[0] + "\n" if r[0] else "\n") +
                 (r[1] if r[1] else ""), (r[2] if r[2] else "") + "\n" + (r[3] if r[3] else ""), r[4]]
                + list(r[-7:-1])
                + [r[4 + int(month)]]
                for i, r in enumerate(results)
            ]
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
            headers = [
                "Indx",
                "Agent Name",
                "Client Name",
                "Year",
                "Telephone",
                "Eff. Date",
                "Paydate",
                "Cancel",
                "Suscriber ID",
                "Members",
                month_name,
            ]
            return self.pdf_create_table(headers, data, A2, f'Report for {insured[0].names if insured else "Insurances"} / {month_name}', True)


class ExportExcelPaymentGlobalClient(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalClient
):
    permission_classes = [HasExportExcelPaymentClientPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentGlobalClientSerializer
    xlsx_use_labels = True
    filename = "payment_global_client.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        sql = self._create_sql(request)
        map_list = self._get_mapping(request)
        results = self.sql_select_all(sql)
        results = self.sql_map_results(map_list, results)

        month = self.map_month(request.GET.get("month"))
        if month:
            self.serializer_class = ExportPaymentGlobalClientMonthSerializer
        elif (request.GET.get('year') == 2023 or request.GET.get('year') == '2023'):
            self.serializer_class = JulDecClientSerializer
        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGlobalClient(PaymentGlobalClient, PDFCommons):
    permission_classes = [HasExportClientPaymentPDFPermission]

    def get(self, request):
        sql = self._create_sql(request)
        results = self.sql_select_all(sql)

        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))
        if month:
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
            headers = [
                "Index",
                "Agent",
                "Client",
                "Paid Members",
                "Telephone",
                "Effective Date",
                "Paid Date",
                "Cancel",
                "Subscriber ID",
                month_name,
            ]
            data = [
                [i + 1, (truncate_string(r[0], 20) if r[0] else ""),
                 (truncate_string(r[1], 20) if r[1] else ""), r[5], r[6], r[7], r[8], r[9], r[10], r[13]]
                for i, r in enumerate(results)
            ]
            return self.pdf_create_table(headers, data, A2, f'Report for {insured[0].names if insured else "Insurances"} / {month_name}', True)
        else:
            headers = [
                "Indx",
                "Agent",
                "Client",
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
            data = [
                [i + 1, (truncate_string(r[0], 20) if r[0] else ""),
                 (truncate_string(r[1], 20) if r[1] else ""), r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16]]
                for i, r in enumerate(results)
            ]
            if (request.GET.get('year') == 2023 or request.GET.get('year') == '2023'):
                data = [[i + 1, (truncate_string(r[0], 20) if r[0] else ""),
                         (truncate_string(r[1], 20) if r[1] else ""), r[11], r[12], r[13], r[14], r[15], r[16]]
                        for i, r in enumerate(results)]
                headers = [
                    "Indx",
                    "Agent",
                    "Client",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
                return self.pdf_create_table(headers, data, A2, f'Report for {insured[0].names if insured else "Insurances"}')
            return self.pdf_create_table(headers, data, A1, f'Report for {insured[0].names if insured else "Insurances"}')


def truncate_string(string, max_length=10):
    if len(string) > max_length:
        return string[:max_length] + "..."
    else:
        return string
