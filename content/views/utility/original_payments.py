from ..imports import *
from ..mailing.service.email_service import EmailService
from safeguard import settings


class GenerateOriginalPayments(APIView, PaymentCommons):
    permission_classes = [HasGenerateOriginalPaymentPermission]

    def post(self, request: APIViewRequest):
        insured = request.data.get('insured')
        month = request.data.get('month')
        year = request.data.get('year')
        if not insured or not month or not year:
            raise ValidationException("Missing filters")

        payment_globals = PaymentsGlobal.objects.filter(pyear=year,
                                                        id_insured=insured).filter(Q(month=month) | Q(month="0" + month))
        if self.check_existing_original_payment(insured, month, year):
            raise ValidationException(
                "This month's original payment was already paid")

        if len(payment_globals) == 0:
            raise NotFoundException(
                "No payment globals founded with this params")

        with transaction.atomic():
            for payment_global in payment_globals:
                agent = Agent.objects.filter(
                    npn=payment_global.a_number).exclude(borrado=1)

                if len(agent) == 0:
                    raise ValidationException(
                        f"This NPN ('{payment_global.a_number}') doesn't match any Agent, this is the rest of the information in that row: payment_global_id: '{payment_global.id}', suscriber_id: '{payment_global.p_number}'")
                elif len(agent) > 1:
                    raise ValidationException(
                        f"There are more than 1 agent with this NPN ('{payment_global.a_number}')")
                else:
                    agent = agent.get()
                comm_date = self.date_from_text(payment_global.info_month)
                if not comm_date:
                    agent_commission = 0
                    final_commission = 0
                else:
                    agent_commission = self.pay_get_agent_year_commission(
                        agent.id, insured,  comm_date.year, payment_global.p_state, payment_global.new_ren, None, None)
                    final_commission = self.pay_get_agent_payment_using_commission(
                        payment_global.commission, agent_commission, payment_global.n_member)

                original_payment = OriginalPayment.objects.create(
                    insured=insured,
                    agent=agent.id,
                    client_name=payment_global.c_name,
                    suscriber_id=payment_global.p_number,
                    state=payment_global.p_state,
                    npn=payment_global.a_number,
                    member_number=payment_global.n_member,
                    effective_date=payment_global.e_date,
                    info_month=payment_global.info_month,
                    commission=final_commission,
                    new_ren=payment_global.new_ren,
                    month=payment_global.month,
                    year=payment_global.pyear,
                )
        return Response(status=status.HTTP_201_CREATED)

    def check_existing_original_payment(self, insured, month, year):
        return OriginalPayment.objects.filter(insured=insured, month=self.inverse_map_month(self.map_month(month)), year=year).count() != 0


class SendOriginalDiscrepancies(APIView, PaymentCommons):
    permission_classes = [HasGenerateOriginalPaymentPermission]

    def post(self, request: APIViewRequest):
        insured = request.data.get('insured')
        month = request.data.get('month')
        year = request.data.get('year')
        if not insured or not month or not year:
            raise ValidationException("Missing filters")

        agents = Agent.objects.filter(
            send_discrepancies=True).exclude(borrado=1)

        for agent in agents:
            discrepancies = self.__get_entries(year, month, insured, agent.id)
            if len(discrepancies) > 0:
                self.__send_discrepancies_email(
                    agent, insured, month, discrepancies)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def __send_discrepancies_email(self, agent: Agent, insured, month, discrepancies):
        service = EmailService(user_name="Safeguard & Associates",
                               email=settings.EMAIL_HOST_USER, passw=settings.EMAIL_SAFEGUARD_PASSWORD)
        insured = Insured.objects.filter(id=insured).get()
        text = f"""
Dear {agent.agent_name} {agent.agent_lastname},
    The following policies came in the payment file from {insured.names}, in the month of {self.map_month(month).capitalize()}, but we couldn't process the payment in the system. Please check each one of them so we can process your payment.

<table border="1" cellspacing="0" cellpadding="5">
<tr>
    <th>Client Name</th>
    <th>Subscriber ID</th>
    <th>Members</th>
    <th>Commission</th>
    <th>Policy Status</th>
</tr>
"""

        for discrepancie in discrepancies:
            text += f"""
<tr>
    <td>{discrepancie['client_name']}</td>
    <td>{discrepancie['suscriber_id']}</td>
    <td>{discrepancie['members']}</td>
    <td>{discrepancie['amount']}</td>
    <td>{discrepancie['policy_status']}</td>
</tr>
"""

        text += """
</table>
<p>Sincerely,<br>
Safeguard & Associates</p>
"""
        service.send_message(
            agent.email, "Missing Policies in System", False, None, None, None, text)

    def __get_entries(self, year, month, insured, agent):
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
                WHEN ap.repaid_on IS NOT NULL AND ap.commission = 0 THEN CONCAT('This policy was/will be paid on: ', ap.repaid_on)
                WHEN ap.commission = 0 or ap.suscriberid is NULL THEN 'This Policy was not paid for some reason, you can make a claim. so we can check what happened'
                ELSE ''
            END AS policy_status
        from original_payment op
        left join 
        (Select * from client where borrado<>1 and SUBSTRING(aplication_date,1,4) ='{year}') c
        on (op.suscriber_id=c.suscriberid)
        LEFT JOIN agent a ON
        (op.agent = a.id)
        LEFT JOIN (
            SELECT * FROM agent_payments WHERE year = {year} AND month = {month} AND id_insured={insured} AND id_agent = {agent} 
            group by suscriberid
        ) ap ON op.suscriber_id = ap.suscriberid
        WHERE
        op.year='{year}' 
        and (op.month='{month}' or op.month='0{month}')
        and insured= {insured}
        and op.agent={agent}
        AND (c.suscriberid IS NULL OR ap.suscriberid IS NULL OR ap.commission = 0)


        GROUP BY 
        op.suscriber_id 

        Order By agent_fullname, client_name
        """
        results = self.sql_select_all(sql)
        results = self.sql_map_results([
            "agent_fullname",
            "client_name",
            "suscriber_id",
            "members",
            "amount",
            "agent",
            "policy_status"
        ], results)
        return results
