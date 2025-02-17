from ..imports import *


class VideoViewSet(viewsets.ModelViewSet, Common):
    permission_classes = [HasVideoPermission]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.get_queryset()
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "-fecha")

        page = self.paginate_queryset(entries)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(names__icontains=search)
        return queryset


# class PayFlorida(APIView, AgencyManagement):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request):
#         commission_group = CommissionsGroup.objects.filter(id=2).get()
#         agents = commission_group.agents.exclude(borrado=1).values('id')
#         agents = self.queryset_to_list(agents)
#         payments = AgentPayments.objects.filter(
#             id_insured=3, month='01', year=2024, id_agent__in=agents, payment_index=1, info_month__icontains='2024')
#         new_payments = []
#         for payment in payments:
#             commission = payment.members_number*3
#             if payment.commission == 0:
#                 commission = 0
#             elif payment.commission < 0:
#                 commission = -commission
#             ap_data = AgentPayments(
#                 id_agent=payment.id_agent,
#                 id_client=payment.id_client,
#                 id_insured=3,
#                 id_state=payment.id_state,
#                 # Strings
#                 year='2024',
#                 month='01',
#                 info_month=payment.info_month,
#                 payment_type=payment.payment_type,
#                 agent_name=payment.agent_name,
#                 client_name=payment.client_name,
#                 insured_name=payment.insured_name,
#                 suscriberid=payment.suscriberid,
#                 # Numbers
#                 members_number=payment.members_number,
#                 payment_index=98,
#                 commission=commission
#             )
#             new_payments.append(ap_data)

#         if new_payments:
#             AgentPayments.objects.bulk_create(new_payments)
#         return Response(len(new_payments))


# class PayUnited(APIView, PaymentCommons):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request):
#         sql = f""" Select
# n_member, p_number,
#                 p_state,new_ren,info_month,id, commission, c_name FROM payments_global where info_month='1/1/2024' and pyear=2023 and month='11' and id_insured=18
# and p_number not in (
# Select suscriberid from client where borrado<>1 and YEAR(aplication_date)=2023 and id_insured=18
# )
# and p_number not in (
# Select suscriberid from agent_payments where info_month='1/1/2024' and id_insured=18
# )
# and p_number in (
# Select suscriberid from client where borrado<>1 and YEAR(aplication_date)=2024 and id_insured=18 and (tipoclient=1 or tipoclient=3)
# )
# """
#         pg_entries = self.sql_select_all(sql)
#         index_payment = 99
#         count = 0
#         for row in pg_entries:
#             comm_date = self.date_from_text(row[4])
#             clients = Client.objects.filter(
#                 suscriberid=row[1],
#                 id_insured=18,
#                 aplication_date__year=2024,
#             ).exclude(borrado=1)

#             client = clients.get()

#             agents = Agent.objects.filter(id=client.id_agent)

#             agent = agents.get()

#             if not comm_date:
#                 agent_year_comm = 0
#                 total_commission = 0
#             else:
#                 agent_year_comm = self.pay_get_agent_year_commission(
#                     agent.pk, 18, comm_date.year, row[2], row[3], '11', 2023
#                 )
#                 total_commission = abs(
#                     float(agent_year_comm)) * abs(int(row[0]))
#                 if float(row[6]) == 0:
#                     total_commission = 0
#                 elif float(row[6]) < 0:
#                     total_commission = -total_commission

#             data = Repayments(
#                 id_agent=agent.id,
#                 id_client=client.id,
#                 id_insured=18,
#                 id_state=client.id_state,
#                 # Strings
#                 year=2024,
#                 month='03',
#                 info_month=row[4],
#                 payment_type=row[3],
#                 agent_name=f"{agent.agent_name} {agent.agent_lastname}",
#                 client_name=row[7],
#                 insured_name=18,
#                 suscriberid=client.suscriberid,
#                 # Numbers
#                 members_number=row[0],
#                 payment_index=index_payment,
#                 commission=total_commission
#             )
#             data.save()
#             ap_data = AgentPayments(
#                 id_agent=agent.id,
#                 id_client=client.id,
#                 id_insured=18,
#                 id_state=client.id_state,
#                 # Strings
#                 year=2023,
#                 month='11',
#                 info_month=row[4],
#                 repaid_on="03/01/2024",
#                 payment_type=row[3],
#                 agent_name=f"{agent.agent_name} {agent.agent_lastname}",
#                 client_name=row[7],
#                 insured_name=18,
#                 suscriberid=client.suscriberid,
#                 # Numbers
#                 members_number=row[0],
#                 payment_index=2,
#                 commission=0
#             )
#             ap_data.save()
#             count += 1
#         return Response(count)


# class FixWrongYearForPayments(APIView, PaymentCommons):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request):
#         sql = f""" Select
# ap.id, ap.suscriberid, ap.id_insured
# FROM
# agent_payments ap
#   join client c on ap.id_client = c.id
# where year='2024' and info_month like '%2024%' and year(c.aplication_date)=2023  AND ap.repaid_on IS NULL  AND borrado<>1 AND (tipoclient=1 OR tipoclient=3)
# AND ap.suscriberid IN (
# SELECT suscriberid FROM client WHERE year(aplication_date)=2024
# )
# """
#         pg_entries = self.sql_select_all(sql)
#         count = 0
#         for row in pg_entries:
#             ap_id = row[0]
#             client = Client.objects.filter(
#                 suscriberid=row[1],
#                 id_insured=row[2],
#                 aplication_date__year=2024,
#             ).exclude(borrado=1)
#             if client.exists():
#                 client2024 = client.get()
#                 ap = AgentPayments.objects.filter(
#                     id=ap_id).update(id_client=client2024.pk)
#                 count += 1
#         return Response(count)


# class FixWrongRepaidOn(APIView, PaymentCommons):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request):

#         sql = f""" SELECT repaid_on, suscriberid, info_month, id FROM agent_payments WHERE repaid_on IS NOT NULL AND repaid_on LIKE '%2024'  AND suscriberid NOT IN (SELECT suscriberid FROM repayments)"""
#         pg_entries = self.sql_select_all(sql)
#         count = 0
#         with transaction.atomic():
#             for row in pg_entries:
#                 repaid_on = self.date_from_text(row[0])
#                 str_month = self.inverse_map_month(
#                     self.map_month(repaid_on.month))
#                 payment = AgentPayments.objects.filter(
#                     suscriberid=row[1],
#                     info_month=row[2],
#                     year=2024,
#                     month=str_month
#                 )
#                 if not payment.exists():
#                     payment_id = row[3]
#                     AgentPayments.objects.filter(
#                         id=payment_id).update(repaid_on=f"{self.inverse_map_month(self.map_month(repaid_on.month+1))}/01/2024")
#                     count += 1
#         return Response(count)


# class FixWrongRepaidOn(APIView, PaymentCommons):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request):

#         sql = f""" SELECT repaid_on, suscriberid, info_month, id FROM agent_payments WHERE repaid_on IS NOT NULL AND repaid_on LIKE '%2024'  AND suscriberid NOT IN (SELECT suscriberid FROM repayments)"""
#         pg_entries = self.sql_select_all(sql)
#         count = 0
#         with transaction.atomic():
#             for row in pg_entries:
#                 repaid_on = self.date_from_text(row[0])
#                 str_month = self.inverse_map_month(
#                     self.map_month(repaid_on.month))
#                 payment = AgentPayments.objects.filter(
#                     suscriberid=row[1],
#                     info_month=row[2],
#                     year=2024,
#                     month=str_month,
#                     repaid_on=None
#                 )
#                 if not payment.exists():
#                     payment_id = row[3]
#                     AgentPayments.objects.filter(
#                         id=payment_id).update(repaid_on=f"{self.inverse_map_month(self.map_month(repaid_on.month+1))}/01/2024")
#                     count += 1
#         return Response(count)


# class FixWrongRepaidOnRepayments(APIView, PaymentCommons):
#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request):

#         sql = f""" SELECT repaid_on, suscriberid, info_month, id, id_insured FROM agent_payments WHERE repaid_on IS NOT NULL AND repaid_on LIKE '%2024'  AND suscriberid IN (SELECT suscriberid FROM repayments)"""
#         pg_entries = self.sql_select_all(sql)
#         count = 0
#         current_date = datetime.now()
#         current_month = current_date.month
#         current_year = current_date.year
#         with transaction.atomic():
#             for row in pg_entries:
#                 repaid_on = self.date_from_text(row[0])
#                 str_month = self.inverse_map_month(
#                     self.map_month(repaid_on.month))
#                 payment_month, payment_year = self.__get_month_year_will_pay(
#                     current_year, row[4], current_month)
#                 if str_month != payment_month:
#                     payment_id = row[3]
#                     AgentPayments.objects.filter(
#                         id=payment_id).update(repaid_on=f"{payment_month}/01/2024")
#                     count += 1
#         return Response(count)

#     def __get_month_year_will_pay(self, year, insured, month):
#         result_month = 0
#         result_year = 0
#         past_month = month-1
#         past_month_year = year
#         if month-1 == 0:
#             past_month = 12
#             past_month_year = year-1
#         else:
#             past_month = self.inverse_map_month(self.map_month(past_month))
#         if AgentPayments.objects.filter(
#                 id_insured=insured, month=past_month, year=past_month_year).count() == 0:
#             result_month = past_month
#             result_year = past_month_year
#         elif AgentPayments.objects.filter(
#                 id_insured=insured, month=self.inverse_map_month(self.map_month(month)), year=year).count() == 0:
#             result_month = month
#             result_year = year
#         else:
#             result_month = month+1 if month+1 != 13 else 1
#             result_year = year if month+1 != 13 else year+1
#         return self.inverse_map_month(self.map_month(result_month)), result_year
