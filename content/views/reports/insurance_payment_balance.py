from ..imports import *


class Insurance_Payment_Balance(APIView, AgencyManagement, DirectSql, DashboardCommons):
    def get(self, request: APIViewRequest):
        year = self.check_none(
            request.query_params.get("year"), date.today().year)
        insured = self.check_none(request.query_params.get("insurance_id"), 1)
        user_id = self.dash_get_alternative_user(request)
        combine_payments = request.GET.get('combine_payments', None)
        if combine_payments == True or combine_payments == 'true':
            old_payments = self.__old_get_payment_data(user_id, year, insured)
            new_payments = self.__get_payment_data(user_id, year, insured)
            payments = old_payments[:6] + new_payments[-6:]
        else:
            payments = self.__get_payment_data(user_id, year, insured)
        payments_global = self.__get_payment_global_data(
            user_id, year, insured)

        data = []
        for i in range(12):
            data.append(
                {
                    "payments": self.check_none(payments[i], 0),
                    "globalPayment": self.check_none(payments_global[i], 0),
                }
            )
        return Response(data)

    def __old_get_payments_for_agent_query(self, year, insured, user_id):
        agent = self.current_is("agent", user_id)
        sql = f"""select sum(p.january), sum(p.february), sum(p.march),
            sum(p.april), sum(p.may), sum(p.june), sum(p.july), sum(p.august),
            sum(p.september), sum(p.october), sum(p.november), sum(p.dicember)
            from payments p where p.fecha = {year} and p.id_agent = {agent}
            and p.id_client in (select c.id from client c WHERE c.borrado<>1 and c.id_insured
            = {insured})"""

        return sql

    def __get_payments_for_agent_query(self, year, insured, user_id):
        agent = self.current_is("agent", user_id)
        sql = "Select "
        for mon in self.get_month_list():
            sql += f" {mon}.com as {mon},"
        sql = sql[:-1]
        sql += " FROM "
        for mon in self.get_month_list():
            sql += f" (Select sum(ap.commission) as com FROM agent_payments ap WHERE ap.year='{year}' and ap.id_agent={agent} and ap.id_insured={insured} and ap.month='{self.inverse_map_month(mon)}') {mon},"
        sql = sql[:-1]
        return sql

    def __get_payments_for_assistant_query(self, year, insured, user_id):
        assistant = self.current_is("assistant", user_id)
        basic_query = "select "
        for month in self.get_month_list():
            basic_query += f"{month}.com as {month},"
        basic_query = basic_query[:-1] + f" from (select {assistant} as id) a "

        def basic_sq(y, m, f):
            return f""" left join (select p.id_assistant id,sum(p.total_commission) com
            from payments_global_assistant p where p.year = {y} and p.month='{m}' {f}
            group by p.id_assistant) {m} on a.id = {m}.id """

        for month in self.get_month_list():
            basic_query += basic_sq(year, month, f"and p.id_insured={insured}")
        return basic_query

    def __get_payments_for_agency_admin_query(self, year, insured, user_id):
        agencies = self.get_related_agencies(user_id, True)
        agencies_str = self.queryset_to_list(agencies, to_string=True)
        basic_query = "select "
        for month in self.get_month_list():
            basic_query += f"{month}.com,"
        basic_query = basic_query[:-1] + f" from (select {insured} as id) i "

        def basic_sq(y, m, f):
            return f""" left join (select p.id_insured id,sum(p.total_commission) com
                from payments_global_agency p where p.year = {y} and p.month='{m}' {f})
                {m} on i.id = {m}.id """

        for month in self.get_month_list():
            basic_query += basic_sq(
                year,
                month,
                f"and p.id_insured={insured} and p.id_agency in ({agencies_str})",
            )

        return basic_query

    def __old_get_payments_for_admin_query(self, year, insured, user_id):
        query = f"""select sum(p.january), sum(p.february), sum(p.march),
	        sum(p.april), sum(p.may), sum(p.june),sum(p.july), sum(p.august),
            sum(p.september),sum(p.october), sum(p.november), sum(p.dicember)
            from payments p where p.fecha = {year} and p.id_client in 
            (select c.id from client c WHERE c.borrado<>1 and c.id_insured = {insured})"""
        return query

    def __get_payments_for_admin_query(self, year, insured, user_id):
        sql = "Select "
        for mon in self.get_month_list():
            sql += f" {mon}.com as {mon},"
        sql = sql[:-1]
        sql += " FROM "
        for mon in self.get_month_list():
            sql += f" (Select sum(ap.commission) as com FROM agent_payments ap WHERE ap.year='{year}' and ap.id_insured={insured} and ap.month='{self.inverse_map_month(mon)}') {mon},"
        query = sql[:-1]
        return query

    def __old_get_payment_data(self, user_id, year, insured):
        year, insured = self.__curate_params(year, insured)
        if self.current_is("agent", user_id):
            query_function = self.__old_get_payments_for_agent_query
        elif self.current_is("assistant", user_id):
            query_function = self.__get_payments_for_assistant_query
        elif self.current_is("agency_admin", user_id):
            query_function = self.__get_payments_for_agency_admin_query
        elif self.current_is("admin", user_id):
            query_function = self.__old_get_payments_for_admin_query
        else:
            return [0.0] * 12

        query = query_function(year, insured, user_id)
        payments = self.sql_select_first(query)
        return list(payments)

    def __get_payment_data(self, user_id, year, insured):
        year, insured = self.__curate_params(year, insured)
        if self.current_is("agent", user_id):
            query_function = self.__get_payments_for_agent_query
        elif self.current_is("assistant", user_id):
            query_function = self.__get_payments_for_assistant_query
        elif self.current_is("agency_admin", user_id):
            query_function = self.__get_payments_for_agency_admin_query
        elif self.current_is("admin", user_id):
            query_function = self.__get_payments_for_admin_query
        else:
            return [0.0] * 12

        query = query_function(year, insured, user_id)
        payments = self.sql_select_first(query)
        return list(payments)

    def __get_payment_global_data(self, user_id, year, insured):
        payment_global = [0] * 12
        if not self.current_is("admin", user_id):
            return payment_global
        query = f"""SELECT p.month, sum(p.commission)c FROM payments_global p 
            where p.id_insured = {insured} and p.pyear = {year} group by p.month;"""
        result = self.sql_select_all(query)
        for m in result:
            payment_global_month = int(m[0]) - 1
            payment_global[payment_global_month] = float(m[1])
        return payment_global

    def __curate_params(self, year, insured):
        year = self.sql_curate_query(year)
        insured = self.sql_curate_query(insured)
        return year, insured
