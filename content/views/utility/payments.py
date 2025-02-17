from ..imports import *
from content.business.logging.db_logging_service import log_empty_payment


class ImportAgentPayments(APIView, PaymentCommons):
    permission_classes = [HasImportPaymentCSVPermission]

    def post(self, request: APIViewRequest):
        with transaction.atomic():
            insured = request.data.get("insured")  #
            param_date = request.data.get("date")  #

            divided_date = param_date.split("-")
            year = str(divided_date[0])
            month = str(divided_date[1])
            month = month if len(month) == 2 else "0" + month

            ignore_payment_global_ids = self.__get_ignored_payment_globals(
                insured, year, month
            )
            self.__add_to_payment_global(
                request, insured, year, month, divided_date, param_date
            )
            self._add_to_payments(year, month, insured,
                                  ignore_payment_global_ids)
            self._pay_repayments(insured, month, year)
            self._pay_future_payments(insured, month, year)
            self.__save_excel_file(request, month, year, insured)
        return Response(status=status.HTTP_202_ACCEPTED)

    def __save_excel_file(self, request, month, year, insured):
        data = {
            "insured": insured,
            "month": month,
            "year": year,
            "file": request.data.get('file')
        }
        serializer = PaymentExcelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return
        else:
            return None

    def __get_ignored_payment_globals(self, insured, year, month):
        pg_query = f"""SELECT pg.id FROM payments_global pg where
                pg.pyear={year} and pg.month='{month}' and pg.id_insured={insured}"""
        results = self.sql_select_all(pg_query)
        ids = [r[0] for r in results]
        return ids

    def __add_to_payment_global(
        self, request, insured, year, month, divided_date, param_date
    ):
        file = request.data.get("file")
        decoded_file = file.read().decode()
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        payment_global = []

        first_check = 1
        for pos, row in enumerate(reader):
            if first_check:
                first_check = 0
                continue
            effective_date = self.date_from_text(
                self.__aux_get_value(
                    request, row, "effective_date", "1000-01-01"),
                multiple_formats=["%m/%d/%Y", "%Y-%m-%d"],
            )
            client_name = self.__aux_get_value(request, row, "client_name", "").replace(
                ",", " "
            )
            if self.check_none(request.data.get('client_lastname'), None):
                client_name = client_name + " " + \
                    self.__aux_get_value(request, row, "client_lastname", "")
            info_month_str = self.__aux_get_value(request, row, "month", None)
            info_month = self.date_from_text(
                info_month_str, multiple_formats=["%m/%d/%Y", "%Y-%m-%d"]
            )
            if not info_month:
                raise ValidationException(
                    f"Info Month in row {pos+1} must be a string field with format YYYY/mm/dd/ or mm/dd/YYYY, not {info_month_str}"
                )

            data = PaymentsGlobal(
                id_insured=insured,
                fecha=param_date,
                a_number=self.__aux_get_agent_number(request, row),
                agent_name=self.__aux_get_value(
                    request, row, "agent_name", ""),
                c_name=client_name,
                p_state=self.__aux_get_state(request, row, pos),
                p_number=self.__aux_get_p_number(request, row, insured, pos),
                e_date=effective_date,
                month=month,
                n_member=self.__aux_get_num_members(request, row, pos),
                rate=self.__aux_get_value(request, row, "rate", integer=True),
                description=self.__aux_get_value(
                    request, row, "description", ""),
                commission=self.__aux_get_value(
                    request, row, "commision", 0.0, floated=True
                ),
                new_ren=self.__aux_get_value(request, row, "new_ren", ""),
                pyear=year,
                procedado=1,
                info_month=f"{info_month.month}/{info_month.day}/{info_month.year}",
            )
            payment_global.append(data)
            if len(payment_global) > 5000:
                PaymentsGlobal.objects.bulk_create(payment_global)
                payment_global.clear()

        if payment_global:
            PaymentsGlobal.objects.bulk_create(payment_global)

    def __aux_get_value(
        self, request, row, param, default=0, integer=False, floated=False
    ):
        element = request.data.get(param)
        if element == None:
            return default
        try:
            value = row[int(element)].replace('$', '')
            if floated:
                value = float(value)
            elif integer:
                value = int(value)
        except:
            value = default
        return value

    def __aux_get_agent_number(self, request, row):
        value = self.__aux_get_value(request, row, "agent_number")

        if str(value).strip().lower() in ["", "n/a"]:
            return 0

        try:
            value = int(value)
        except:
            value = 0

        return value

    def __aux_get_p_number(self, request, row, insured, pos):
        value = self.__aux_get_value(request, row, "policy_number", None)
        aetna_mode = 1 if int(insured) == 17 else 0
        molina_mode = 1 if int(insured) == 1 else 0

        if value == None:
            raise ValidationException(
                f"Suscriber Id in row {pos+1} must be a valid string"
            )

        if aetna_mode:
            value = value[4:-7]
        elif molina_mode:
            value = value[3:]

        return value

    def __aux_get_num_members(self, request, row, pos):
        value = self.__aux_get_value(
            request, row, "num_member", integer=True, default=None
        )
        if value == None:
            raise ValidationException(
                f"Members # in row {pos+1} must be a valid decimal number"
            )
        return abs(value)

    def __aux_get_state(self, request, row, pos):
        value = self.__aux_get_value(request, row, "state", None)
        if value == None:
            raise ValidationException(
                f"State in row {pos+1} must be a valid text")
        return value

    def _make_payment_log(
        self,
        row,
        client,
        agent,
        insured_id,
        commission,
        payment,
        year,
        month,
        payment_id,
        summary="",
    ):
        log_insurance = Insured.objects.filter(id=insured_id).first()
        log_state = State.objects.filter(sigla__icontains=row[3]).first()
        log_empty_payment(
            dict(
                suscriberid=row[1] if row[1] else None,
                bob_id=row[5] if row[5] else None,
                client_id=client.pk if client and client.pk else None,
                client_name=f"{client.names} {client.lastname}" if client and client.names else None,
                member_number=row[0],
                info_month=row[4] if row[4] else None,
                agent_id=agent.pk if agent and agent.pk else None,
                agent_npn=agent.npn if agent and agent.npn else None,
                agent_name=f"{agent.agent_name} {agent.agent_lastname}" if agent and agent.agent_name else None,
                agent_year_comm=commission if commission else None,
                insured_id=log_insurance.pk if log_insurance else None if row[1] else None,
                insured_name=log_insurance.names if log_insurance else None,
                state_id=log_state.pk if log_state else None,
                state_sigla=row[2] if row[2] else None,
                payment_type=row[3] if row[3] else None,
                payment_total=payment if payment else None,
                summary=summary if summary else None,
                payment_year=year if year else None,
                payment_month=month if month else None,
                repayment=False,
                payment_id=payment_id if payment_id else None,
            )
        )

    def _add_to_payments(self, year, month, insured, ignore_payment_global_ids):
        pg_ids_str = (
            ",".join(set(str(i) for i in ignore_payment_global_ids))
            if len(ignore_payment_global_ids)
            else None
        )
        pg_ids_query_clause = f"and pg.id not in ({pg_ids_str})" if pg_ids_str else ""
        pg_query = f"""SELECT pg.n_member, pg.p_number,
                pg.p_state,pg.new_ren,pg.info_month,pg.id, pg.commission, pg.c_name, pg.agent_name, pg.a_number, pg.rate, pg.e_date, pg.description 
                FROM `payments_global` pg where
                pg.pyear={year} and pg.month='{month}' and pg.id_insured={insured}
                {pg_ids_query_clause}"""

        pg_entries = self.sql_select_all(pg_query)

        agent_payments = []
        try:
            insured_obj = Insured.objects.get(id=insured)
        except:
            raise ValidationException(
                f"There is not such insured with id {insured}"
            )
        for row in pg_entries:
            comm_date = self.date_from_text(row[4])
            clients = Client.objects.filter(
                suscriberid=row[1],
                id_insured=insured,
                aplication_date__year=comm_date.year,
            ).exclude(borrado=1)

            if clients.count() != 1:
                self._make_payment_log(
                    row,
                    None,
                    None,
                    insured,
                    None,
                    None,
                    year,
                    month,
                    None,
                    "Client count != 1"
                )
                self.__add_to_unassigned_payments(
                    insured,
                    row[7],
                    row[8],
                    row[2],
                    row[1],
                    month,
                    row[4],
                    year,
                    row[3],
                    row[9],
                    row[0],
                    row[10],
                    row[6],
                    row[11],
                    row[12]
                )
                continue
            client = clients.get()

            agents = Agent.objects.filter(id=client.id_agent)
            if agents.count() != 1:
                self._make_payment_log(
                    row,
                    client,
                    None,
                    insured,
                    None,
                    None,
                    year,
                    month,
                    None,
                    "Agent count != 1"
                )
                self.__add_to_unassigned_payments(
                    insured,
                    row[7],
                    row[8],
                    row[2],
                    row[1],
                    month,
                    row[4],
                    year,
                    row[3],
                    row[9],
                    row[0],
                    row[10],
                    row[6],
                    row[11],
                    row[12]
                )
                continue
            agent = agents.get()

            if not comm_date:
                agent_year_comm = 0
                total_commission = 0
            else:
                has_assistant = True if hasattr(
                    agent, 'commission_group') and agent.commission_group and agent.commission_group.pk == 1 else False
                agent_year_comm = self.pay_get_agent_year_commission(
                    agent.pk, insured, comm_date.year, row[2], row[3], month, year, has_assistant
                )
                total_commission = abs(
                    float(agent_year_comm)) * abs(int(row[0]))
                if float(row[6]) == 0:
                    total_commission = 0
                elif float(row[6]) < 0:
                    total_commission = -total_commission
            if agent_year_comm == 0:
                self._make_payment_log(
                    row,
                    client,
                    agent,
                    insured,
                    agent_year_comm,
                    total_commission,
                    year,
                    month,
                    None,
                )

            if self.check_future_month(row[4], month, year):

                data = FuturePayments(
                    id_agent=agent.id,
                    id_client=client.id,
                    id_insured=insured_obj.id,
                    id_state=client.id_state,
                    # Strings
                    year=year,
                    month=self.inverse_map_month(self.map_month(int(month))),
                    info_month=row[4],
                    payment_type=row[3],
                    agent_name=f"{agent.agent_name} {agent.agent_lastname}",
                    client_name=row[7],
                    insured_name=insured_obj.names,
                    suscriberid=client.suscriberid,
                    description=row[12],
                    # Numbers
                    members_number=row[0],
                    payment_index=3,
                    commission=total_commission
                )
                data.save()
            else:
                data = AgentPayments(
                    id_agent=agent.id,
                    id_client=client.id,
                    id_insured=insured_obj.id,
                    id_state=client.id_state,
                    # Strings
                    year=year,
                    month=month,
                    info_month=row[4],
                    payment_type=row[3],
                    agent_name=f"{agent.agent_name} {agent.agent_lastname}",
                    client_name=row[7],
                    insured_name=insured_obj.names,
                    suscriberid=client.suscriberid,
                    description=row[12],
                    # Numbers
                    members_number=row[0],
                    payment_index=1,
                    commission=total_commission
                )
                agent_payments.append(data)
                self.__put_reference_for_old_payment_if_needed(
                    row[4], client, agent, insured_obj, row[7], row[0], row[3], month, year, row[12])

                # agency = Agency.objects.filter(id=agent.id_agency).get()
                # if agency.self_managed:
                #     self.__add_self_managed_agency_payment_entry(
                #         agent, client, year, month, row[4], row[3], row[0], row[6], row[7], insured_obj, agency)

                if total_commission == 0:
                    self._make_payment_log(
                        row,
                        client,
                        agent,
                        insured,
                        agent_year_comm,
                        total_commission,
                        year,
                        month,
                        None,
                    )
            if len(agent_payments) > 5000:
                AgentPayments.objects.bulk_create(agent_payments)
                agent_payments.clear()

        if agent_payments:
            AgentPayments.objects.bulk_create(agent_payments)

    # def __add_self_managed_agency_payment_entry(self, agent, client, year, month, info_month, payment_type, members_number, commission, client_name, insured, agency):

    #     data = SelfManagedAgencyPayment(
    #         id_agent=agent.id,
    #         id_client=client.id,
    #         id_insured=client.id_insured,
    #         id_state=client.id_state,
    #         id_agency=agent.id_agency,
    #         year=year,
    #         month=month,
    #         info_month=info_month,
    #         payment_type=payment_type,
    #         agent_name=f"{agent.agent_name} {agent.agent_lastname}",
    #         client_name=client_name,
    #         insured_name=insured.names,
    #         suscriberid=client.suscriberid,
    #         members_number=members_number,
    #         commission=commission,
    #         agency_name=agency.agency_name
    #     )
    #     data.save()

    def __add_to_unassigned_payments(self, id_insured, client_name, agent_name, state_initials, suscriberid, month, info_month, year, new_ren, npn, members, rate, commission, effective_date, description):
        data = UnAssignedPayments(
            id_insured=id_insured,
            client_name=client_name,
            agent_name=agent_name,
            state_initials=state_initials,
            suscriberid=suscriberid,
            month=month,
            info_month=info_month,
            year=year,
            new_ren=new_ren,
            npn=npn,
            members=members,
            rate=rate,
            commission=commission,
            effective_date=effective_date,
            description=description
        )
        data.save()

    def __put_reference_for_old_payment_if_needed(self, info_moth, client, agent, insured_obj, client_name, members_number, payment_type, month, year, description):
        if self.check_past_month(info_moth, month, year):
            payment_date = self.date_from_text(info_moth)
            data = AgentPayments(
                id_agent=agent.id,
                id_client=client.id,
                id_insured=insured_obj.id,
                id_state=client.id_state,
                # Strings
                year=payment_date.year,
                repaid_on=f"{month}/1/{year}",
                month=self.inverse_map_month(
                    self.map_month(payment_date.month)),
                info_month=info_moth,
                payment_type=payment_type,
                agent_name=f"{agent.agent_name} {agent.agent_lastname}",
                client_name=client_name,
                insured_name=insured_obj.names,
                suscriberid=client.suscriberid,
                description=description,
                # Numbers
                members_number=members_number,
                payment_index=1,
                commission=0
            )
            data.save()

    def check_future_month(self, info_moth, actual_month, year):
        full_date = self.date_from_text(info_moth)
        month = int(full_date.month)
        if month > int(actual_month):
            if int(full_date.year) < int(year):
                return False
            return True
        else:
            if int(full_date.year) > int(year):
                return True
            else:
                return False

    def check_past_month(self, info_moth, actual_month, actual_year):
        full_date = self.date_from_text(info_moth)
        month = int(full_date.month)
        if int(actual_year) > int(full_date.year):
            return True
        elif int(actual_year) < int(full_date.year):
            return False
        else:
            if month < int(actual_month):
                return True
            else:
                return False

    def _pay_repayments(self, insured, month, year):
        repayments = Repayments.objects.filter(id_insured=insured)
        future_payments = []
        for repayment in repayments:
            if self.check_future_month(repayment.info_month, month, year):
                future_payments.append(repayment.id)
                continue
            else:
                ap_data = AgentPayments(
                    id_agent=repayment.id_agent,
                    id_client=repayment.id_client,
                    id_insured=insured,
                    id_state=repayment.id_state,
                    # Strings
                    year=year,
                    month=self.inverse_map_month(self.map_month(month)),
                    info_month=repayment.info_month,
                    payment_type=repayment.payment_type,
                    agent_name=repayment.agent_name,
                    client_name=repayment.client_name,
                    insured_name=repayment.insured_name,
                    suscriberid=repayment.suscriberid,
                    description=repayment.description,
                    # Numbers
                    members_number=repayment.members_number,
                    payment_index=2,
                    commission=repayment.commission
                )
                ap_data.save()
                agent = Agent.objects.filter(id=repayment.id_agent).get()
                # agency = Agency.objects.filter(id=agent.id_agency).get()
                # if agency.self_managed:
                #     client = Client.objects.filter(
                #         id=repayment.id_client).get()
                #     insured_obj = Insured.objects.filter(
                #         id=repayment.id_insured).get()
                #     self.__add_self_managed_agency_payment_entry(agent, client, year, month, repayment.info_month, repayment.payment_type,
                #                                                  repayment.members_number, repayment.original_commission, repayment.client_name, insured_obj, agency)

        repayments = repayments.exclude(id__in=future_payments)
        repayments.delete()

    def _pay_future_payments(self, insured, month, year):
        future_payments = FuturePayments.objects.filter(id_insured=insured)
        other_month_future_payments = []
        for future_payment in future_payments:
            if self.check_future_month(future_payment.info_month, month, year):
                other_month_future_payments.append(future_payment.id)
                continue
            else:
                ap_data = AgentPayments(
                    id_agent=future_payment.id_agent,
                    id_client=future_payment.id_client,
                    id_insured=insured,
                    id_state=future_payment.id_state,
                    # Strings
                    year=year,
                    month=self.inverse_map_month(self.map_month(month)),
                    info_month=future_payment.info_month,
                    payment_type=future_payment.payment_type,
                    agent_name=future_payment.agent_name,
                    client_name=future_payment.client_name,
                    insured_name=future_payment.insured_name,
                    suscriberid=future_payment.suscriberid,
                    description=future_payment.description,
                    # Numbers
                    members_number=future_payment.members_number,
                    payment_index=3,
                    commission=future_payment.commission
                )
                ap_data.save()
                agent = Agent.objects.filter(id=future_payment.id_agent).get()
                # agency = Agency.objects.filter(id=agent.id_agency).get()
                # if agency.self_managed:
                #     client = Client.objects.filter(
                #         id=future_payment.id_client).get()
                #     insured_obj = Insured.objects.filter(
                #         id=future_payment.id_insured).get()
                # self.__add_self_managed_agency_payment_entry(agent, client, year, month, future_payment.info_month, future_payment.payment_type, future_payment.members_number, future_payment.original_commission, future_payment.client_name, insured_obj, agency)

        future_payments = future_payments.exclude(
            id__in=other_month_future_payments)
        future_payments.delete()
