from ..imports import *
import re


class PaymentGlobalOriginal(APIView, AgencyManagement, DirectSql, LimitOffsetPagination):
    permission_classes = [HasPaymentGlobalOriginalPermission]

    def get(self, request: HttpRequest):
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)
        month = self.check_none(request.GET.get('month'))
        if not month:
            results = self.map_results(results)
            serializer = OriginalPaymentGlobalSerializer(results, many=True)
        else:
            results = self.map_results_extended(results)
            serializer = OriginalPaymentGlobalMonthSerializer(
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
            agency_sql = f"and agents.id_agency={agency.id}"
        else:
            agency_sql = ""

        agent = self.select_agent(request.GET.get("agent"), request.user.pk)

        agent_sql = ""
        if agent:
            agent_sql = f"and id={agent.id}"

        agents = self.get_related_agents(request.user.pk, True)
        if not (request.user.is_admin and not (agent or agency)):
            agent_sql += (
                f" AND id in ({self.queryset_to_list(agents, to_string=True)})"
            )

        search = self.check_none(request.GET.get("search"))
        if search:
            search_sql = (
                f""" and concat(agent_name,' ',agent_lastname) like '%{search}%'"""
            )
        else:
            search_sql = ""

        month = self.check_none(request.GET.get("month"))
        if not month:
            sql = f"""
            Select 
            concat(agents.agent_name," ", agents.agent_lastname) as agent_fullname,
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
            agents.id
            from
            (Select * from agent where borrado <> 1 {agent_sql} {search_sql}) agents left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='01'
            {insured_sql}
            Group By agent) jan on (agents.id= jan.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='02'
            {insured_sql}
            Group By agent) feb on (agents.id= feb.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='03'
            {insured_sql}
            Group By agent) mar on (agents.id= mar.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='04'
            {insured_sql}
            Group By agent) apr on (agents.id= apr.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='05'
            {insured_sql}
            Group By agent) may on (agents.id= may.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='06'
            {insured_sql}
            Group By agent) jun on (agents.id= jun.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='07'
            {insured_sql}
            Group By agent) jul on (agents.id= jul.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='08'
            {insured_sql}
            Group By agent) ag on (agents.id= ag.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='09'
            {insured_sql}
            Group By agent) sep on (agents.id= sep.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='10'
            {insured_sql}
            Group By agent) oct on (agents.id= oct.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='11'
            {insured_sql}
            Group by agent) nov on (agents.id= nov.agent) left join 
            (SELECT agent,sum(commission) commission
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and month='12'
            {insured_sql}
            Group by agent) dece on (agents.id= dece.agent) 
            WHERE 1 {agency_sql}
            {order}
            """
        else:
            sql = f"""
            Select 
            concat(agents.agent_name," ", agents.agent_lastname) as agent_fullname,
            month.members as members,
            month.commission as amount,
            agents.id
            FROM
            (Select * from agent where borrado <> 1 {agent_sql} {search_sql}) agents left join 
            (SELECT agent,sum(commission) commission, sum(member_number) members
            FROM `original_payment`  
            WHERE 
            year = '{year}'
            and (month='{month}' or month='0{month}')
            {insured_sql}
            Group by agent) month on (agents.id= month.agent) 
            WHERE 1 {agency_sql}
            {order}
            """
        return self.sql_select_all(sql)

    def __apply_ordering(
        self, request: HttpRequest, default_order: str = "agent_fullname"
    ) -> str:
        order = ""
        default = f"order by {default_order}"
        order_field = self.check_none(request.GET.get("order"))
        month = request.GET.get("month", None)
        desc = self.check_none(request.GET.get("desc"))
        orderables = [
            "agent_fullname",
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
            "dicember"
        ]
        month_orderables = [
            "agent_fullname",
            "members",
            "amount",
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
                    "january": el[1],
                    "february": el[2],
                    "march": el[3],
                    "april": el[4],
                    "may": el[5],
                    "june": el[6],
                    "july": el[7],
                    "august": el[8],
                    "september": el[9],
                    "october": el[10],
                    "november": el[11],
                    "dicember": el[12],
                    "agent": el[13],
                }
            )
        return response

    def map_results_extended(self, results: list) -> list:
        response = []
        for el in results:
            response.append(
                {
                    "agent_name": self.check_none(el[0], ""),
                    "members": el[1],
                    "amount": el[2],
                    "agent": el[3],
                }
            )
        return response


class ExportExcelPaymentGlobalOriginal(XLSXFileMixin, ReadOnlyModelViewSet, PaymentGlobalOriginal):
    permission_classes = [HasExportExcelPaymentGlobalOriginalPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = OriginalPaymentGlobalSerializer
    xlsx_use_labels = True
    filename = "orignal_payment_global.xlsx"
    xlsx_ignore_headers = ["agent"]

    def list(self, request: APIViewRequest):
        month = self.map_month(request.GET.get("month"))
        results = self.get_entries(request)

        if not month:
            results = self.map_results(results)
        else:
            self.serializer_class = OriginalPaymentGlobalMonthSerializer
            results = self.map_results_extended(results)
            serializer = self.get_serializer(
                results, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentGlobalOriginal(PDFCommons, PaymentGlobalOriginal):
    permission_classes = [HasExportPDFPaymentGlobalOriginalPermission]

    def get(self, request):
        results = self.get_entries(request)
        month = self.check_none(request.GET.get("month"))
        insured = self.get_insured_by_id(
            self.check_none(request.GET.get('insured')))
        if not month:
            data = [[i + 1, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12]]
                    for i, r in enumerate(results)
                    ]
            headers = [
                "Indx",
                "Agent Name",
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
            return self.pdf_create_table(headers, data, A2, f'Original Report for {insured[0].names if insured else "Insurances"}')
        else:
            data = [
                [i + 1, r[0], r[1], r[2]]
                for i, r in enumerate(results)
            ]
            month_name = self.map_month(month).replace(
                "dicember", "december").capitalize()
            headers = [
                "Indx",
                "Agent Name",
                "Members",
                'Amount',
            ]
            return self.pdf_create_table(headers, data, A4, f'Original Report for {insured[0].names if insured else "Insurances"} / {month_name}', True)


class DataForOriginalPayment(APIView, AgencyManagement):
    permission_classes = [
        HasPaymentGlobalOriginalPermission or HasPaymentGlobalAgencyPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "agents", "agencies", "insurances"))
