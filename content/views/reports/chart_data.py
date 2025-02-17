from ..imports import *


class DataForTableDashboard(APIView, AgencyManagement, DirectSql, DashboardCommons):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgentSerializer

    def get(self, request: APIViewRequest):
        user_id = self.dash_get_alternative_user(request)
        year = self.check_none(request.query_params.get("year"), date.today().year)
        clients = self.get_related_clients(user_id, True)
        clients_ids = self.queryset_to_list(clients, to_string=True)
        insurances = Insured.objects.all().order_by("names")
        arr = []
        for insurance in insurances:
            sql = f"""Select COUNT(c.id) as policies,SUM(c.family_menber) as members,
                COUNT(CASE WHEN (c.suscriberid = 'n/a' or c.suscriberid = 'N/A' or c.suscriberid = '' or c.suscriberid is null)
                THEN c.suscriberid END) as nosub FROM client c WHERE c.id_insured={insurance.id} 
                AND SUBSTRING(c.aplication_date,1,4)='{year}' AND 
                c.id in ({clients_ids})"""
            response = self.sql_select_first(sql)
            clients_count = response[0]
            members_count = int(response[1]) if response[1] else 0
            noSub = response[2]

            sql = f"""SELECT COUNT(case when (bob_global.term_date <= CURDATE()) then bob_global.id end), 
                COUNT(case when (bob_global.paid_date < CURDATE() and bob_global.paid_date > '1980-01-02')
                then bob_global.id end), count(case when (bob_global.eleg_commision = 'No')
                then bob_global.id end) FROM bob_global INNER JOIN 
                client on client.suscriberid = bob_global.suscriberid where
                bob_global.suscriberid <> '' and bob_global.suscriberid is not null and client.id 
                in ({clients_ids}) and client.id_insured = {insurance.pk} 
                and bob_global.id_insured = {insurance.pk} 
                and SUBSTRING(aplication_date,1,4) = '{year}'
            """
            result = self.sql_select_first(sql)
            cancel = result[0]
            late_pay = result[1]
            no_elegible = result[2]

            arr.append(
                {
                    "insuranceId": insurance.id,
                    "insuranceName": insurance.names,
                    "policies": clients_count,
                    "members": members_count if (members_count != None) else 0,
                    "noSubId": noSub,
                    "cancel": cancel,
                    "latePay": late_pay,
                    "noElig": no_elegible,
                    # "logo": insurance.logo if insurance.logo != None else "",
                }
            )

        arr.append(self.__get_total_row(arr))
        return Response(arr)

    def __get_total_row(self, data):
        row = {
            "insuranceId": 0,
            "insuranceName": "Total",
        }
        p = m = nS = c = l = nE = 0
        for d in data:
            try:
                p += int(d["policies"])
            except:
                pass
            try:
                m += int(d["members"])
            except:
                pass
            try:
                nS += int(d["noSubId"])
            except:
                pass
            try:
                c += int(d["cancel"])
            except:
                pass
            try:
                l += int(d["latePay"])
            except:
                pass
            try:
                nE += int(d["noElig"])
            except:
                pass
        row.update(
            {
                "policies": p,
                "members": m,
                "noSubId": nS,
                "cancel": c,
                "latePay": l,
                "noElig": nE,
            }
        )
        return row


class DataForChartData(APIView, AgencyManagement):
    def get(self, request):
        user = request.user
        result = self.get_selects(user.pk, "insurances")
        return Response(result)
