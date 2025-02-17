from ..imports import *
import re


class PaymentsAgencyViewSet(APIView, AgencyManagement, LimitOffsetPagination, DirectSql):
    permission_classes = [HasGeneralPaymentPermission]

    def get(self, request: HttpRequest):
        entries = self._get_entries(request)
        total = 0.0
        for r in entries:
            try:
                total += r.total_commission
            except:
                pass
        page = self.paginate_queryset(entries, request, view=self)
        if int(request.GET.get('payment', 0)) == 2:
            response = self.get_paginated_response(page)
        else:
            serilizer = PaymentsAgencySerializer(page, many=True)
            response = self.get_paginated_response(serilizer.data)
        response.data["total"] = total
        return response

    def post(self, request: HttpRequest):
        user: CustomUser = request.user
        if not (user.is_admin or user.has_perm("content.add_generalpayment")):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            entries = self.get_related_payments(request)
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        with transaction.atomic():
            old_ones = PaymentsGlobalAgency.objects.filter(
                agency=int(request.data.get("agency")),
                insured=int(request.data.get("insured")),
                month=self.map_month(int(request.data.get("month"))),
                year=request.data.get("year"),
                sec_pay_from_insured=None
            )
            if old_ones.exists():
                self.backup_repayments_and_delete(old_ones)
            secondary_overrides = SecondaryOverride.objects.filter(
                id_insured=int(request.data.get("insured")), id_children_agency=int(request.data.get("agency")))
            if secondary_overrides.exists():
                for el in secondary_overrides:
                    old_ones = PaymentsGlobalAgency.objects.filter(
                        agency=el.id_parent_agency,
                        insured=int(request.data.get("insured")),
                        month=self.map_month(int(request.data.get("month"))),
                        year=request.data.get("year"),
                        sec_pay_from_insured=request.data.get("agency"),
                        indx=5
                    )
                    if old_ones.exists():
                        old_ones.delete()

            objs = PaymentsGlobalAgency.objects.bulk_create(
                list(map(lambda e: PaymentsGlobalAgency(**e), entries))
            )
            self._pay_repayments(request.data.get("insured"), self.map_month(int(
                request.data.get("month"))), request.data.get("year"), request.data.get("agency"))

        return Response(len(objs))

    def _pay_repayments(self, insured, month, year, agency):
        repayments = AgencyRepayments.objects.filter(
            insured=insured, agency=agency)
        for repayment in repayments:
            ap_data = PaymentsGlobalAgency(
                agent=repayment.agent,
                client=repayment.client,
                insured=repayment.insured,
                agency=repayment.agency,
                sec_pay_from_insured=repayment.sec_pay_from_insured,
                year=year,
                month=month,
                info_month=repayment.info_month,
                members_number=repayment.members_number,
                total_commission=repayment.total_commission,
                indx=2,
            )
            ap_data.save()
        repayments.delete()

    def backup_repayments_and_delete(self, payments):
        repayments = payments.filter(indx=2).exclude(total_commission=0)
        for repayment in repayments:
            data = AgencyRepayments(
                agent=repayment.agent,
                client=repayment.client,
                insured=repayment.insured,
                agency=repayment.agency,
                year=repayment.year,
                month=repayment.month,
                info_month=repayment.info_month,
                sec_pay_from_insured=repayment.sec_pay_from_insured,
                members_number=repayment.members_number,
                total_commission=repayment.total_commission,
                indx=repayment.indx,
            )
            data.save()
        payments.delete()

    def get_related_payments(self, request: HttpRequest):
        user: CustomUser = request.user
        if not user.is_admin:
            return Response(status.HTTP_403_FORBIDDEN)

        agency = self.check_none(request.data.get("agency"))
        insured = self.check_none(request.data.get("insured"))
        month = int(self.check_none(request.data.get("month"), 0))
        year = int(self.check_none(request.data.get("year"), 0))
        if not (agency and insured and month and year):
            raise ValueError(
                "All four: agency, insured, month, year params are required"
            )

        mapped_month = self.map_month(int(month))
        if mapped_month is None:
            raise ValueError("Month Value is wrong")
        agents = self.get_related_agents(user.pk, True)
        agency = self.select_agency(agency, user.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        commission = CommAgency.objects.filter(
            id_agency=agency, id_insured=insured, yearcom=year
        )
        commission = (
            float(commission.values("comm").get()[
                  "comm"]) if commission.exists() else 0
        )
        response = []
        if self.check_new_payment(month, year):
            response = self.__make_new_payments(
                agents, year, self.inverse_map_month(mapped_month), commission, agency, insured)
        else:
            response = self.__make_old_payments(
                agents, year, mapped_month, commission, agency, insured)

        return response

    def __make_new_payments(self, agents, year, month, commission, agency, insured):
        payments = AgentPayments.objects.filter(year=year, month=month, id_agent__in=agents, id_insured=insured).values(
            'id_client', 'id_agent', 'members_number', 'commission', 'info_month')
        response = []
        insured_obj = Insured.objects.get(id=insured)
        for p in payments:
            local_commission = commission
            if p['commission'] == 0 or p['members_number'] == 0:
                continue
            if p['commission'] < 0:
                local_commission = -commission
            agents = Agent.objects.filter(id=p["id_agent"])
            agent = agents.get() if agents.exists() else None
            if not agent:
                continue
            client = Client.objects.filter(
                id_agent=agent.pk, id=p["id_client"], id_insured=insured
            ).exclude(borrado=1).only("names", "lastname", "id_insured", "family_menber")
            client = client.get() if client.exists() else None
            if not client:
                continue
            secondary_overrides = SecondaryOverride.objects.filter(
                id_insured=insured, id_children_agency=agency)
            if secondary_overrides.exists():
                for el in secondary_overrides:
                    if local_commission < 0:
                        amount_per_member = -el.amount_per_member
                    else:
                        amount_per_member = el.amount_per_member
                    entry = {
                        "agent": agent,
                        "client": client,
                        "month": self.map_month(month),
                        "year": year,
                        "agency": el.id_parent_agency,
                        "insured": insured_obj,
                        "members_number": p['members_number'],
                        "info_month": p['info_month'],
                        "indx": 5,
                        "total_commission": p['members_number'] * amount_per_member,
                        "sec_pay_from_insured": agency.pk
                    }
                    response.append(entry)
            entry = {
                "agent": agent,
                "client": client,
                "month": self.map_month(month),
                "year": year,
                "agency": agency,
                "insured": insured_obj,
                "members_number": p['members_number'],
                "info_month": p['info_month'],
                "indx": 1,
                "total_commission": p['members_number'] * local_commission
                if p['members_number'] and p['commission']
                else 0,
            }
            response.append(entry)
        return response

    def __make_old_payments(self, agents, year, month, commission, agency, insured):
        payments = Payments.objects.filter(
            id_agent__in=self.queryset_to_list(agents), fecha=year
        ).values("id_agent", "id_client", month)
        response = []
        for p in payments:
            agents = Agent.objects.filter(id=p["id_agent"])
            agent = agents.get() if agents.exists() else None
            if not agent:
                continue
            client = Client.objects.filter(
                id_agent=agent.pk, id=p["id_client"], id_insured=insured
            ).exclude(borrado=1).only("names", "lastname", "id_insured", "family_menber")
            client = client.get() if client.exists() else None
            if not client:
                continue
            insured_obj = Insured.objects.get(id=client.id_insured)
            entry = {
                "agent": agent,
                "client": client,
                "month": month,
                "year": year,
                "agency": agency,
                "insured": insured_obj,
                "members_number": client.family_menber,
                "indx": 1,
                "total_commission": client.family_menber * commission
                if client.family_menber and p[month]
                else 0,
            }
            response.append(entry)
        return response

    def _get_entries(self, request):
        payment = self.check_none(request.GET.get("payment"))
        if payment and int(payment) == 2:
            entries = self.__get_no_payment_query(request)
        else:
            entries = self.__apply_filters(request)
            entries = self.__apply_search(entries, request)
            entries = self.apply_order_queryset(
                entries, request, "client_name")

        return entries

    def __get_no_payment_query(self, request: HttpRequest) -> str:
        year = self.sql_curate_query(
            str(self.check_none(request.GET.get("year"), date.today().year))
        )
        insured = self.check_none(request.GET.get("insured"))
        if not insured:
            raise ValidationException('Missing Filters')
        search = self.check_none(request.GET.get("search"), "")
        insured_filter = f"and c.id_insured={insured}" if insured else ""
        mapped_month = self.map_month(request.GET.get("month"))
        user = request.user
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        clients = self.get_related_clients(
            user.pk, True, ["id", "id_agent"], True)

        if agent:
            agents = agents.filter(pk=agent.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        clients = clients.filter(id_agent__in=self.queryset_to_list(agents))

        client_filter = f" AND c.id in ({self.queryset_to_list(clients, to_string=True)})" if not (
            user.is_admin and not (agent or agency)) else ""
        inner_client_filter = f" AND pga.id_client in ({self.queryset_to_list(clients, to_string=True)})" if not (
            user.is_admin and not (agent or agency)) else ""

        sql = f"""
            SELECT
                c.id,
                c.id_agent,
                a.id,
                i.id,
                CONCAT(c.names, " ", c.lastname) AS client_name,
                CONCAT(c.agent_name, " ", c.agent_lastname) AS agent_name,
                i.names as insured_name,
                agency_name,
                {year} as year,
                '{mapped_month}' as month,
                c.family_menber,
                fsq.indx,
                CASE WHEN fsq.total_commission IS NOT NULL THEN fsq.total_commission ELSE 0.0 END AS total_commission
                
            FROM 
                (Select c.id, c.id_agent, c.names,c.lastname, c.family_menber, a.agent_name, a.agent_lastname, a.id_agency, c.borrado, c.aplication_date, c.id_insured, c.suscriberid, c.tipoclient from client c left join agent a on c.id_agent = a.id) c
                LEFT JOIN(
                    SELECT *
                    FROM
                        payments_global_agency pga
                    WHERE
                        1 AND pga.id_insured = {insured} AND pga.month = '{mapped_month}' AND pga.year = '{year}' {inner_client_filter}
                    GROUP BY
                        pga.id_client
                ) fsq ON (c.id=fsq.id_client) 
                
                LEFT JOIN agency a ON c.id_agency = a.id
                LEFT JOIN insured i ON c.id_insured = i.id
        
                
            WHERE
                c.borrado <> 1 {client_filter} AND SUBSTRING(c.aplication_date, 1, 4) = '{year}' 
                    AND(fsq.id IS NULL OR fsq.total_commission = 0) 
                    {insured_filter} AND(c.tipoclient = 1 OR c.tipoclient = 3) AND(
                    LOWER(
                        CONCAT(
                           a.agency_name
                        )
                    ) LIKE '%{search.lower()}%' OR LOWER(CONCAT(c.names, ' ', c.lastname)) LIKE '%{search.lower()}%' OR LOWER(c.suscriberid) LIKE '%{search.lower()}%'
                )
            ORDER BY
                client_name,
                agent_name
        """
        results = self.sql_select_all(sql)
        results = self.sql_map_results([
            "client",
            "agent",
            "agency",
            "insured",
            "client_name",
            "agent_name",
            "insured_name",
            "agency_name",
            "year",
            "month",
            "members_number",
            "indx",
            "total_commission"
        ], results)
        return results

    def __apply_filters(self, request):
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            result = PaymentsGlobalAgency.objects.filter(insured=insured)
        else:
            result = PaymentsGlobalAgency.objects.all()

        agency = self.select_agency(request.GET.get("agency"), request.user.pk)
        if agency:
            result = result.filter(agency=agency.pk)
        else:
            result = result.filter(
                agency__in=self.get_related_agencies(request.user.pk, True)
            )

        agent = self.select_agent(request.GET.get("agent"), request.user.pk)
        if agent:
            result = result.filter(agent=agent)

        month = self.check_none(request.GET.get("month"))
        if month:
            try:
                result = result.filter(month=self.map_month(int(month)))
            except:
                pass
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                result = result.exclude(total_commission=0)
            elif payment and int(payment) == 2:
                result = result.filter(total_commission=0)

        year = self.check_none(request.GET.get("year"))
        if year:
            try:
                result = result.filter(year=year)
            except:
                pass

        repayment = self.check_none(request.GET.get("repayment"))
        if repayment == '1':
            result = result.exclude(indx=1)
        elif repayment == '2':
            result = result.filter(indx=1)

        result = result.exclude(client__borrado=1)

        result = result.annotate(
            agent_name=Concat("agent__agent_name", V(" "),
                              "agent__agent_lastname"),
            client_name=Concat("client__names", V(" "), "client__lastname"),
            insured_name=F("insured__names"),
            agency_name=F("agency__agency_name"),
        )

        return result

    def __apply_search(self, queryset, request):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(agent_name__icontains=search) | Q(
                    client_name__icontains=search)
            )
        return queryset


class DataForPaymentsAgency(APIView, AgencyManagement):
    permission_classes = [HasGeneralPaymentPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "agents", "agencies", "insurances"))


class ExportExcelPaymentAgency(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentsAgencyViewSet
):
    permission_classes = [HasExportExcelPaymentAgencyPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentsAgencyExcelSerializer
    xlsx_use_labels = True
    filename = "payment_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request: APIViewRequest):

        results = self._get_entries(request)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentsAgency(PaymentsAgencyViewSet, PDFCommons):
    permission_classes = [HasExportPDFPaymentAgencyPermission]

    def get(self, request):
        results = self._get_entries(request)
        data = [
            [
                i + 1,
                re.sub(r"\s+", "\n", r.client_name.strip()),
                r.agent_name.strip().replace(" ", "\n", 1),
                r.agency_name,
                r.insured_name,
                r.month,
                r.members_number,
                r.total_commission,
            ]
            for i, r in enumerate(results)
        ]
        headers = [
            "Indx",
            "Client Name",
            "Agent Name",
            "Agency",
            "Insurance",
            "Month",
            "Members",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A2, 'Agency Report', True)


class MakeAgencyRepayment(APIView, AgencyManagement):

    def post(self, request: HttpRequest):
        user: CustomUser = request.user
        if not (user.is_admin or user.has_perm("content.add_generalpayment")):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            count = self.get_related_payments(request)
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

        return Response(count)

    def get_related_payments(self, request):
        user: CustomUser = request.user
        agency = self.check_none(request.data.get("agency"))
        insured = self.check_none(request.data.get("insured"))
        month = self.check_none(request.data.get("month"))
        year = self.check_none(request.data.get("year"))

        mapped_month = self.map_month(int(month))
        if month is None:
            raise ValueError("Month Value is wrong")
        agents = self.get_related_agents(user.pk, True)
        agency = self.select_agency(agency, user.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)

        agency_commission = CommAgency.objects.filter(
            id_agency=agency, id_insured=insured, yearcom=year
        )
        agency_commission = (
            float(agency_commission.values("comm").get()[
                  "comm"]) if agency_commission.exists() else 0
        )

        old_ones = PaymentsGlobalAgency.objects.filter(
            agency=int(request.data.get("agency")),
            insured=int(request.data.get("insured")),
            month=self.map_month(int(request.data.get("month"))),
            year=request.data.get("year"),
        ).exclude(total_commission=0).values('client_id', 'indx')

        old_ones_rep = AgencyRepayments.objects.filter(
            agency=int(request.data.get("agency")),
            insured=int(request.data.get("insured")),
            year=request.data.get("year"),
        ).exclude(total_commission=0).values('client_id')

        if old_ones:
            existing_payments = self.queryset_to_list(old_ones, 'client_id')
            max_index = old_ones.latest('indx').get('indx')
            max_index = int(max_index)+1 if max_index else 1
        else:
            existing_payments = []
            max_index = 2

        if old_ones_rep:
            existing_payments += self.queryset_to_list(
                old_ones_rep, 'client_id')
        with transaction.atomic():
            if self.check_new_payment(month, year):
                count = self.__make_new_payments(
                    agents, year, month, agency_commission, agency, insured, existing_payments, max_index)
            else:
                count = self.__make_old_payments(
                    agents, year, mapped_month, agency_commission, agency, insured, existing_payments, max_index)
        return count

    def __make_old_payments(self, agents, year, mapped_month, agency_commission, agency, insured, existing_payments, max_index):
        payments = Payments.objects.filter(
            id_agent__in=self.queryset_to_list(agents), fecha=year
        ).exclude(id_client__in=existing_payments).values("id_agent", "id_client", mapped_month)
        month_will_pay, year_will_pay = self.__get_month_year_will_pay(
            year, insured, self.inverse_map_month(mapped_month), agency)
        count = 0
        for p in payments:
            agents = Agent.objects.filter(id=p["id_agent"])
            agent = agents.get() if agents.exists() else None
            if not agent:
                continue
            client = Client.objects.filter(
                id_agent=agent.pk, id=p["id_client"], id_insured=insured
            ).exclude(borrado=1).only("names", "lastname", "id_insured", "family_menber")
            client = client.get() if client.exists() else None
            if not client:
                continue
            insured_obj = Insured.objects.get(id=client.id_insured)

            if p[mapped_month] == 0 or p[mapped_month] == '0':
                payments_done_count = self.check_paid_client_by_infomonth(
                    agent, client, insured_obj, mapped_month, year, agency_commission, agency, max_index)
                count += payments_done_count
                continue

            if client.family_menber == 0 or client.family_menber == '0':
                continue
            old_payment = PaymentsGlobalAgency.objects.filter(
                agent=agent, client=client, month=mapped_month, year=year, agency=agency, total_commission=0)
            if old_payment:
                old_payment.delete()

            payment_month_entry = PaymentsGlobalAgency(
                agent=agent,
                client=client,
                month=mapped_month,
                info_month=f"{self.inverse_map_month(mapped_month)}/01/{year}",
                year=year,
                agency=agency,
                insured=insured_obj,
                members_number=client.family_menber,
                total_commission=0,
                indx=2,
                repaid_on=f"{month_will_pay}/01/{year_will_pay}"

            )
            payment_month_entry.save()
            entry = AgencyRepayments(

                agent=agent,
                client=client,
                month=mapped_month,
                info_month=f"{self.inverse_map_month(mapped_month)}/01/{year}",
                year=year,
                agency=agency,
                insured=insured_obj,
                members_number=client.family_menber,
                total_commission=client.family_menber * agency_commission
                if client.family_menber and p[mapped_month]
                else 0,
                indx=2
            )
            entry.save()
            count += 1

        return count

    def check_paid_client_by_infomonth(self, agent, client, insured_obj, mapped_month, year, agency_commission, agency, max_index):
        payments = AgentPayments.objects.filter(
            id_agent=agent.id, id_client=client.id, id_insured=insured_obj.id, info_month=f"{self.inverse_map_month(mapped_month)}/1/{year}"
        ).exclude(commission=0)
        month_will_pay, year_will_pay = self.__get_month_year_will_pay(
            year, insured_obj.id, self.inverse_map_month(mapped_month), agency)
        count = 0
        if len(payments) > 0:
            for p in payments:
                payment_month_entry = PaymentsGlobalAgency(
                    agent=agent,
                    client=client,
                    month=mapped_month,
                    info_month=p.info_month,
                    year=year,
                    agency=agency,
                    insured=insured_obj,
                    members_number=p.members_number,
                    total_commission=0,
                    indx=2,
                    repaid_on=f"{month_will_pay}/01/{year_will_pay}"

                )
                payment_month_entry.save()
                entry = AgencyRepayments(

                    agent=agent,
                    client=client,
                    month=mapped_month,
                    info_month=p.info_month,
                    year=year,
                    agency=agency,
                    insured=insured_obj,
                    members_number=p.members_number,
                    total_commission=p.members_number * agency_commission
                    if p.members_number and p.commission
                    else 0,
                    indx=2
                )
                entry.save()
                count += 1
        return count

    def __get_month_year_will_pay(self, year, insured, month, agency):
        result_month = 0
        result_year = 0
        past_month = month-1
        past_month_year = year
        if month-1 == 0:
            past_month = 12
            past_month_year = year-1
        if PaymentsGlobalAgency.objects.filter(
                insured_id=insured, agency_id=agency, month=self.map_month(past_month), year=past_month_year).exclude(total_commission=0).count() == 0:
            result_month = past_month
            result_year = past_month_year
        elif PaymentsGlobalAgency.objects.filter(
                insured_id=insured, agency_id=agency, month=self.map_month(month), year=year).exclude(total_commission=0).count() == 0:
            result_month = month
            result_year = year
        else:
            result_month = month+1 if month+1 != 13 else 1
            result_year = year if month+1 != 13 else year+1
        return self.inverse_map_month(self.map_month(result_month)), result_year

    def __make_new_payments(self, agents, year, month, agency_commission, agency, insured, existing_payments, max_index):
        payments = AgentPayments.objects.filter(
            id_agent__in=self.queryset_to_list(agents), id_insured=insured, month=self.inverse_map_month(self.map_month(month)), year=year
        ).exclude(id_client__in=existing_payments).exclude(commission=0)
        month_will_pay, year_will_pay = self.__get_month_year_will_pay(
            year, insured, int(month), agency)
        count = 0
        insured_obj = Insured.objects.get(id=insured)
        for p in payments:
            local_agency_commission = -agency_commission if p.commission < 0 else agency_commission
            agents = Agent.objects.filter(id=p.id_agent)
            agent = agents.get() if agents.exists() else None
            if not agent:
                continue
            client = Client.objects.filter(id=p.id_client).exclude(borrado=1)
            client = client.get() if client.exists() else None
            if not client:
                continue

            PaymentsGlobalAgency.objects.filter(
                agent=agent, client=client, month=self.map_month(month), year=year, agency=agency, total_commission=0).delete()

            payment_month_entry = PaymentsGlobalAgency(
                agent=agent,
                client=client,
                month=self.map_month(month),
                info_month=p.info_month,
                year=year,
                agency=agency,
                insured=insured_obj,
                members_number=p.members_number,
                total_commission=0,
                indx=2,
                repaid_on=f"{month_will_pay}/01/{year_will_pay}"

            )
            payment_month_entry.save()
            entry = AgencyRepayments(
                agent=agent,
                client=client,
                month=self.map_month(month),
                info_month=p.info_month,
                year=year,
                agency=agency,
                insured=insured_obj,
                members_number=p.members_number,
                total_commission=p.members_number * local_agency_commission
                if p.members_number and p.commission
                else 0,
                indx=2
            )
            entry.save()
            count += 1

            secondary_overrides = SecondaryOverride.objects.filter(
                id_insured=insured, id_children_agency=agency)
            if secondary_overrides.exists():
                for el in secondary_overrides:
                    if local_agency_commission < 0:
                        amount_per_member = -el.amount_per_member
                    else:
                        amount_per_member = el.amount_per_member
                    entry = AgencyRepayments(
                        agent=agent,
                        client=client,
                        month=self.map_month(month),
                        info_month=p.info_month,
                        year=year,
                        agency=el.id_parent_agency,
                        insured=insured_obj,
                        members_number=p.members_number,
                        total_commission=p.members_number * amount_per_member,
                        indx=2,
                        sec_pay_from_insured=agency.pk
                    )
                    entry.save()
        return count
