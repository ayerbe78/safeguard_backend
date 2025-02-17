from ..imports import *
from .__common import ClientAppUtils
from content.views.sms.views import SmsCommons
import random
from django.db.models import CharField
from django.db.models.functions import Concat, Replace, ExtractYear, Cast


class ClientViewSet(viewsets.ModelViewSet, ClientAppUtils, DirectSql):
    permission_classes = [HasClientPermission]
    serializer_class = ClientSerializer
    queryset = Client.objects.filter(
        Q(tipoclient=0) | Q(tipoclient=1) | Q(tipoclient=3)
    ).exclude(borrado=1)

    def create(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        dependants = self.check_none(request.data.get("dependants"))
        pendingdocs = self.check_none(request.data.get("pendingdocs"))
        spouse_data = {
            k.replace("spouse_", ""): v
            for k, v in request.data.items()
            if "spouse_" in k
        }
        with transaction.atomic():
            response: Response = super().create(request)
            new_client: Client = Client(**response.data)
            new_client.tipoclient = 1
            new_client.save()
            self.check_existing_client(new_client)
            if dependants and isinstance(dependants, list):
                self.add_to_dependants(dependants, new_client.pk)
            if len(spouse_data.keys()):
                self.add_spouse(spouse_data, new_client.pk)
            if pendingdocs and isinstance(pendingdocs, list):
                self.add_to_pending_docs(pendingdocs, new_client.pk)
            self.add_to_payment(response.data)
            self.log_client_insert(user, new_client.pk)
            self.add_first_note(new_client, request)
            return response

    def update(self, request, *args, **kwargs):
        user = request.user
        with transaction.atomic():
            client = self.get_object()
            spouse_data = {
                k.replace("spouse_", ""): v
                for k, v in request.data.items()
                if "spouse_" in k
            }
            if len(spouse_data.keys()):
                self.add_spouse(spouse_data, client.pk)
            response = super().update(request, *args, **kwargs)
            new_client = Client(**response.data)
            self.check_existing_client(new_client)
            self.add_to_payment(response.data)
            self.log_client_update(user, new_client.pk, new_client)
            return self.retrieve(request)

    def retrieve(self, request, *args, **kwargs):
        client: Client = self.get_object()
        response = self.retrieve_client_app_response(client)
        return Response(response)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        client = self.get_object()
        client.borrado = 1
        client.save()
        self.log_client_delete(user, client.pk)
        return Response(client.pk)

    def list(self, request, *args, **kwargs):
        x = date.today()
        a = date(x.year, 1, 1)
        b = date(x.year, 12, 31)
        if request == None:
            queryset = (
                Client.objects.filter(aplication_date__range=[a, b])
                .exclude(borrado=1)
                .exclude(tipoclient=2)
                .exclude(tipoclient=4)
                .order_by("names")
            )
        else:
            if request.GET.get("order") == "true":
                queryset = (
                    Client.objects.filter(aplication_date__range=[a, b])
                    .exclude(borrado=1)
                    .exclude(tipoclient=2)
                    .exclude(tipoclient=4)
                    .order_by("names")
                )
            else:
                queryset = (
                    Client.objects.filter(aplication_date__range=[a, b])
                    .exclude(borrado=1)
                    .exclude(tipoclient=2)
                    .exclude(tipoclient=4)
                    .order_by("-names")
                )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["post"], detail=True, url_path="transfer", url_name="transfer_to_app"
    )
    def transfer_to_app(self, request: HttpRequest, pk=None):
        client: Client = self.get_object()
        next_year = (date.today().year) + 1
        if self.check_existing_application(client, next_year):
            raise ValidationException(
                'This Client was already transfered to Application')

        old_client_id = client.pk
        dependants = ClientParient.objects.filter(id_client=client.pk)
        notes = History.objects.filter(id_client=client.pk)
        documents = ClientDocument.objects.filter(id_client=client.pk)
        client.tipoclient = 4
        client.not_visible = 1
        client.plansupp = client.new_plan
        client.new_plan = None
        with transaction.atomic():
            new_date = f"{next_year}-1-1"
            client.aplication_date = new_date
            client.pk = None
            if not client.paymentday:
                client.paymentday = date.today().strftime("%Y-%m-%d")
            if not client.cardexp:
                client.cardexp = date.today().strftime("%Y-%m-%d")
            client.save()
            self.check_existing_client(client)
            self.migrate_dependants(dependants, client.pk)
            self.migrate_notes(notes, client.pk)
            self.migrate_documents(documents, client.pk)
            self.migrate_client_consent_log(old_client_id, client.pk)
            self.log_app_transfer(
                request.user, old_client_id, f"Client transfered to application {client.pk}")
            self.log_app_transfer(
                request.user, client.pk, f"Application transfered from client {old_client_id}")
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["post"], detail=True, url_path="migrate")
    def migrate_next_year(self, request: HttpRequest, pk=None):
        user = request.user
        pendingdocs = self.check_none(request.data.get("pendingdocs"))
        with transaction.atomic():
            instance: Client = self.get_object()
            dependants = ClientParient.objects.filter(id_client=instance.pk)
            notes = History.objects.filter(id_client=instance.pk)
            documents = ClientDocument.objects.filter(id_client=instance.pk)

            duplicated = Client(**model_to_dict(instance))
            duplicated.pk = None
            if not duplicated.paymentday:
                duplicated.paymentday = date.today().strftime("%Y-%m-%d")
            if not duplicated.cardexp:
                duplicated.cardexp = date.today().strftime("%Y-%m-%d")
            duplicated.save()
            serializer = self.get_serializer(
                duplicated, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            duplicated.plansupp = duplicated.new_plan
            duplicated.new_plan = None
            duplicated.save()

            client = Client(**serializer.data)

            self.migrate_dependants(dependants, client.pk)
            self.migrate_notes(notes, client.pk)
            self.migrate_documents(documents, client.pk)

            self.check_existing_client(client)
            if pendingdocs and isinstance(pendingdocs, list):
                self.add_to_pending_docs(pendingdocs, client.pk)
            self.add_to_payment(serializer.data)

            # Mark as renewed the old client
            instance.renewed = 1
            instance.save()

            self.migrate_client_consent_log(instance.pk, client.pk)
            self.log_client_migrate(
                user, instance.pk, "Migrated to Client with ID: "+str(client.pk))

            self.log_client_migrate(
                user, client.pk, "Migrated from Client with ID: "+str(instance.pk))
            return Response(serializer.data)

    def get_policy_status_filter(self, request):
        policy_status = self.check_none(request.GET.get("policy_status"))
        sql = ""
        if policy_status == 4 or policy_status == '4':
            sql = f"and (b.suscriberid IS NULL)"
        elif policy_status == 1 or policy_status == '1':
            sql = f"and (b.suscriberid IS NOT NULL and b.term_date IS NULL or b.term_date < CURDATE()  or b.policy_status = 'Terminated')"
        elif policy_status == 2 or policy_status == '2':
            sql = f"and ((b.suscriberid IS NOT NULL and b.term_date IS NOT NULL and b.term_date >= CURDATE()  and b.policy_status <> 'Terminated') and (b.paid_date IS NULL or b.paid_date < CURDATE()))"
        elif policy_status == 3 or policy_status == '3':
            sql = f"and ( b.suscriberid IS NOT NULL and b.term_date IS NOT NULL and b.term_date >= CURDATE()  and b.policy_status <> 'Terminated' and  b.paid_date IS NOT NULL and b.paid_date >= CURDATE() )"
        return sql

    @action(methods=["get"], detail=False, url_path="filter")
    def filter(self, request: HttpRequest):
        filters = self.apply_filters(request)
        ordering = self.apply_ordering(request)
        alternate_joins = self.apply_alternate_joins(request)
        sql = f"""Select c.pending,c.id,c.names,c.lastname,c.suscriberid,c.aplication_date,
                c.id_insured,c.date_birth,c.id_agent,c.id_state,c.family_menber,
                CASE WHEN b.suscriberid is NULL THEN 'black' WHEN b.term_date is NULL THEN 'red'
                WHEN b.term_date < CURDATE() THEN 'red' WHEN b.policy_status = 'Terminated' THEN 'red'
                WHEN b.paid_date is NULL THEN 'yellow' WHEN b.paid_date < CURDATE() THEN 'yellow'
                else 'normal' END as status_bob, c.renewed from client c left join
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
                   )b
                on c.suscriberid=b.suscriberid {alternate_joins} where c.borrado <>1 and c.tipoclient <> 2
                and c.tipoclient <> 4 {filters} {self.get_policy_status_filter(request)} group by c.id {ordering}"""

        all = self.sql_select_all(sql)

        clients = self.sql_map_results(
            [
                "pending",
                "id",
                "names",
                "lastname",
                "suscriberid",
                "aplication_date",
                "id_insured",
                "date_birth",
                "id_agent",
                "id_state",
                "family_menber",
                "status_bob",
                "renewed",
            ],
            all,
        )
        total_members = 0
        for c in clients:
            try:
                total_members += int(c["family_menber"])
            except:
                total_members += 0
        results = self.paginate_queryset(clients)
        serializer = ListClientSerializer(results, many=True)
        data = self.get_paginated_response(serializer.data).data
        data["members"] = total_members
        return Response(data)

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_client(self, request: HttpRequest):
        user: CustomUser = request.user
        if not (user.is_admin or user.has_perm("content.view_client")):
            return Response(status=status.HTTP_403_FORBIDDEN)

        agents = (
            self.get_related_agents(user.pk, True)
            .values("id", "agent_name", "agent_lastname", "id_agency", "id_assistant")
            .order_by("agent_name", "agent_lastname")
        )
        agency = (
            self.get_related_agencies(user.pk, True)
            .values("id", "agency_name")
            .order_by("agency_name")
        )
        assistant = (
            Assistant.objects.all()
            .values("id", "assistant_name", "assistant_lastname")
            .order_by("assistant_name", "assistant_lastname")
        )
        insurances = (
            Insured.objects.all()
            .order_by("names")
            .values("id", "names")
            .order_by("names")
        )
        state = (
            State.objects.all()
            .order_by("names")
            .values("id", "names")
            .order_by("names")
        )
        status_obj = (
            Status.objects.all()
            .order_by("names")
            .values("id", "names")
            .order_by("names")
        )
        policy = (
            Poliza.objects.all()
            .order_by("names")
            .values("id", "names")
            .order_by("names")
        )
        event = (
            Event.objects.all()
            .order_by("names")
            .values("id", "names")
            .order_by("names")
        )

        agent_serializer = AgentOnlyNameSerializer(agents, many=True)
        insurance_serializer = InsuredOnlyNameSerializer(insurances, many=True)
        agency_serializer = AgencyOnlyNameSerializer(agency, many=True)
        state_serializer = StateOnlyNameSerializer(state, many=True)
        assistant_serializer = AssistantOnlyNameSerializer(
            assistant, many=True)

        event_serializer = StateOnlyNameSerializer(event, many=True)
        status_obj_serializer = StateOnlyNameSerializer(status_obj, many=True)
        policy_serializer = StateOnlyNameSerializer(policy, many=True)
        new_selects = self.get_selects(
            user.pk, "agents", "assistants", "insurances", "agencies", "states"
        )
        response = {
            "agents": agent_serializer.data,
            "insurances": insurance_serializer.data,
            "agency": agency_serializer.data,
            "state": state_serializer.data,
            "policy": policy_serializer.data,
            "event": event_serializer.data,
            "status": status_obj_serializer.data,
            "assistant": assistant_serializer.data,
        }
        response.update(new_selects)
        return Response(
            response,
            status=status.HTTP_200_OK,
        )

    @action(methods=["put"], detail=True, url_path="pending/toggle")
    def toggle_pending(self, request: HttpRequest, pk):
        clients = Client.objects.filter(id=pk)

        if not clients.exists():
            raise NotFoundException("Not such client")

        client = clients.get()
        client.pending = 0 if client.pending else 1
        client.save()

        sql = f"""select CASE WHEN b.suscriberid is NULL THEN 'red' WHEN b.term_date is NULL THEN 'red'
                WHEN b.term_date < CURDATE() THEN 'red' WHEN b.policy_status = 'Terminated' THEN 'red'
                WHEN b.paid_date is NULL THEN 'yellow' WHEN b.paid_date < CURDATE() THEN 'yellow'
                else 'normal' END as status_bob from client c join bob_global b
                on c.suscriberid=b.suscriberid where c.id = {client.pk}"""
        result = self.sql_select_first(sql)
        status_bob = result[0] if result and len(result) else "red"

        client_dict = model_to_dict(client)
        client_dict["status_bob"] = status_bob

        serializer = ListClientSerializer(client_dict)
        self.log_client_check_toggle(request.user, client.pk)
        return Response(serializer.data)

    @action(methods=["put"], detail=True, url_path="set_renewed")
    def set_renewed(self, request: HttpRequest, pk):
        clients = Client.objects.filter(id=pk)

        if not clients.exists():
            raise NotFoundException("Not such client")

        client = clients.get()
        client.renewed = 1
        client.save()

        sql = f"""select CASE WHEN b.suscriberid is NULL THEN 'red' WHEN b.term_date is NULL THEN 'red'
                WHEN b.term_date < CURDATE() THEN 'red' WHEN b.policy_status = 'Terminated' THEN 'red'
                WHEN b.paid_date is NULL THEN 'yellow' WHEN b.paid_date < CURDATE() THEN 'yellow'
                else 'normal' END as status_bob from client c join bob_global b
                on c.suscriberid=b.suscriberid where c.id = {client.pk}"""
        result = self.sql_select_first(sql)
        status_bob = result[0] if result and len(result) else "red"

        client_dict = model_to_dict(client)
        client_dict["status_bob"] = status_bob

        serializer = ListClientSerializer(client_dict)
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="import")
    def import_clients(self, request: APIViewRequest):
        user = request.user
        agent_id = self.check_none(request.data.get("agent"))
        agent = self.select_agent(agent_id, user.pk)
        file = request.data.get("file")

        if not file or not agent:
            raise ValidationException(
                "Agent and import file must be provided!")

        decoded_file = file.read().decode()
        io_string = io.StringIO(decoded_file)
        # reader = csv.reader(io_string)
        reader = csv.reader(io_string)

        first = True
        count = 0
        with transaction.atomic():
            for row in reader:
                if first:
                    first = False
                    continue

                data = dict(
                    lastname=self.__aux_get_value(row, 1),
                    names=self.__aux_get_value(row, 0),
                    telephone=self.__aux_get_value(row, 2),
                    suscriberid=self.__aux_get_value(row, 3),
                    date_birth=self.date_from_text(
                        self.__aux_get_value(row, 4),
                        multiple_formats=["%Y-%m-%d", "%m/%d/%Y"],
                    ),
                    id_insured=self.__aux_get_insurance(row, 5),
                    application_id=self.__aux_get_value(row, 6),
                    id_state=self.__aux_get_state(row, 7),
                    social_security=self.__aux_get_value(row, 8),
                    family_menber=self.__aux_get_value(row, 9, 0, True),
                    sexo=self.__aux_get_gender(row, 10),
                    email=self.__aux_get_value(row, 11),
                    aplication_date=self.date_from_text(
                        self.__aux_get_value(row, 12),
                        multiple_formats=["%Y-%m-%d", "%m/%d/%Y"],
                    ),
                    id_agent=agent.pk,
                    tipoclient=1,
                )
                new_client: Client = Client.objects.create(**data)
                try:
                    self.check_existing_client(new_client)
                    self.add_to_payment(model_to_dict(new_client))
                except Exception as e:
                    new_client.delete()
                    continue
                    # raise ValidationException(
                    #     f"Client {new_client.names} {new_client.lastname} could not be imported. Exceptio was: {e}"
                    # )
                spouse = self.__aux_get_value(row, 13)
                if spouse:
                    spouse_name = spouse
                    spouse_lastname = self.__aux_get_value(row, 14)
                    client_spouse = ClientParient(
                        id_client=new_client.pk,
                        names=spouse_name,
                        lastnames=spouse_lastname,
                        pos=0,
                    )
                    client_spouse.save()
                count += 1
                self.log_client_insert(user, new_client.pk)

        return Response(count)

    def __aux_get_value(self, row, pos, default=None, integer=False, floated=False):
        na_values = ["n/a", "na", ""]
        try:
            value = row[int(pos)]
            if str(value).lower() in na_values:
                return default
            if floated:
                value = float(value)
            elif integer:
                value = int(value)
        except:
            value = default
        return value

    def __aux_get_gender(self, row, pos):
        gender = self.__aux_get_value(row, pos, 0)
        gender = (
            1
            if gender and str(gender).lower() == "m"
            else 2
            if gender and str(gender).lower() == "f"
            else 0
        )
        return gender

    def __aux_get_state(self, row, pos):
        state = State.objects.filter(
            sigla__icontains=self.__aux_get_value(row, pos, "")
        )
        state_id = state[0].pk if state.exists() else 0
        return state_id

    def __aux_get_insurance(self, row, pos):
        insured = Insured.objects.filter(
            names__icontains=self.__aux_get_value(row, pos, "")
        )
        insured_id = insured[0].pk if insured.exists() else 0
        return insured_id

    @action(methods=["get"], detail=False, url_path="lite")
    def get_clients_lite(self, request: HttpRequest):
        user: CustomUser = request.user
        search = self.sql_curate_query(
            self.check_none(request.GET.get('search'), '')).replace(" ", "")
        clients = self.get_related_clients(user.pk, include_self=True, year=date.today().year, only=['id', 'names', 'lastname']) | self.get_related_clients(
            user.pk, include_self=True, year=date.today().year+1, only=['id', 'names', 'lastname'])

        clients = clients.annotate(
            year=Cast(ExtractYear("aplication_date"),
                      output_field=CharField()),
            full_name=Concat("names", V(" "), "lastname",
                             V(" ("), "year", V(")")),
            full_name_no_spaces=Replace(
                Replace(
                    Replace(Concat("names", V(" "), "lastname"), V(" "), V("")),
                    V("\t"), V(""),
                ),
                V("\n"), V(""),
            )
        ).filter(full_name_no_spaces__icontains=search)[:50]
        results = self.paginate_queryset(clients)
        serializer = ClientSerializerLite(results, many=True)
        return self.get_paginated_response(serializer.data)


class ClientDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasClientDocumentPermission]
    serializer_class = ClientDocumentSerializer
    queryset = ClientDocument.objects.all()


class ClientParientViewSet(viewsets.ModelViewSet):
    permission_classes = [HasDependantPermission]
    serializer_class = ClientParientSerializer
    queryset = ClientParient.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        id_client = data.get("id_client")
        pos = self.get_queryset().filter(id_client=id_client).aggregate(Max("pos"))
        data["pos"] = pos["pos__max"] + 1 if pos["pos__max"] is not None else 1
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance: ClientParient = self.get_object()
                pos, client = instance.pos, instance.id_client
                # if pos == 0:
                #     instance.
                others = ClientParient.objects.filter(
                    id_client=client, pos__gt=pos)
                for d in others:
                    d.pos = d.pos - 1
                    d.save()
                return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))


class ClientYearDeatails(APIView):
    permission_classes = [HasClientYearDetailsPermission]

    def get(self, request):
        user = request.user
        if not (user.is_admin or user.has_perm("content.view_client")):
            return Response(status=status.HTTP_403_FORBIDDEN)
        agent = request.GET.get("agent")
        client = request.GET.get("client")
        year = request.GET.get("year")
        if not (agent and client):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = Payments.objects.filter(
            id_agent=agent,
            id_client=client,
            fecha=(year if year else date.today().year),
        )
        serializer = PaymentsSerializer
        # x = Payment
        serializer = serializer(data, many=True)
        return Response(serializer.data[0] if data.exists() else None)


class NewClientYearDetails(APIView, AgencyManagement, DirectSql):
    permission_classes = [HasClientYearDetailsPermission]

    def get(self, request):
        user = request.user
        if not (user.is_admin or user.has_perm("content.view_client")):
            return Response(status=status.HTTP_403_FORBIDDEN)
        agent = request.GET.get("agent")
        suscriberid = request.GET.get("suscriberid")
        year = request.GET.get("year")
        if not (agent and suscriberid):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        sql = f"Select {agent} as id_agent, '{suscriberid}' as suscriberid, {year} as fecha,"
        for mon in self.get_month_list():
            sql += f" case when {mon}.com is not null then {mon}.com else 0 end as {mon},"
        sql = sql[:-1]
        sql += " FROM "
        for mon in self.get_month_list():
            sql += f" (Select sum(ap.commission) as com FROM agent_payments ap WHERE ap.id_agent={agent} and ap.suscriberid='{suscriberid}' and ap.year='{year}' and ap.month='{self.inverse_map_month(mon)}') {mon},"
        sql = sql[:-1]
        response = self.sql_select_first(sql)
        response = self.sql_map_results(
            ['id_agent', 'suscriberid', 'fecha']+self.get_month_list(), [response])
        return Response(response[0])


class DetailPaymentInPaymentTable(APIView, PaymentCommons):
    permission_classes = [HasDetailPaymentInPaymentTablePermission]

    def get(self, request):
        user = request.user
        year = request.GET.get("year")
        client = request.GET.get("client")
        agent = request.GET.get("agent")
        month = request.GET.get("month")
        if (
            year == None
            or agent == None
            or client == None
            or month == None
            or year == "0"
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data="All year, agent, client and month params must be valid",
            )
        total, payment_id = self.pay_get_made_payments_for_agent(
            year, month, agent, client, withId=True
        )
        total = list(total.values())[0] if total else 0
        payments = self.pay_get_actual_payments_for_agent(
            str(payment_id), f"{month},0{month}"
        )
        payments = payments[0] if payments else []
        return Response({"data": payments, "total": total})


class NewDetailPaymentInPaymentTable(APIView, PaymentCommons):
    permission_classes = [HasDetailPaymentInPaymentTablePermission]

    def get(self, request):
        year = request.GET.get("year")
        client = request.GET.get("client")
        suscriberid = self.check_none(request.GET.get("suscriberid"))
        agent = request.GET.get("agent")
        month = request.GET.get("month")
        repayment = request.GET.get('repayment', None)
        payment = request.GET.get('payment', None)
        repayment_filter, payment_filter = '', ''
        if repayment == '1' or repayment == 1:
            repayment_filter = ' and payment_index<>1'
        elif repayment == '2' or repayment == 2:
            repayment_filter = ' and payment_index=1'
        if payment == '2' or payment == 2:
            payment_filter = ' and ap.commission=0'
        suscriberid_filter = ''
        if suscriberid:
            suscriberid_filter = f" and ap.suscriberid='{suscriberid}'"
        else:
            suscriberid_filter = f'and ap.id_client={client}'
        if (
            year == None
            or agent == None
            or client == None
            or month == None
            or year == "0"
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data="All year, agent, client and month params must be valid",
            )
        sql = f"""
            SELECT
                ap.agent_name,
                ap.client_name,
                ap.insured_name,
                a.npn,
                ap.suscriberid,
                ap.members_number,
                c.aplication_date,
                ap.payment_type,
                concat(ap.month,'/01/',ap.year),
                ap.info_month,
                s.sigla,
                ap.commission,
                ap.description
            FROM
                agent_payments ap 
                left join agent a on ap.id_agent=a.id
                left join client c on ap.id_client=c.id
                left join state s on ap.id_state= s.id
            WHERE
                1 {suscriberid_filter} {repayment_filter} {payment_filter} and repaid_on is null and ap.id_agent={agent} and ap.month='{self.inverse_map_month(self.map_month(month))}' and ap.year='{year}'
        """
        mapper = [
            'agent_name',
            'client_name',
            'insured_name',
            'npn',
            'suscriberid',
            'num_member',
            'effective_date',
            'type',
            'date',
            'month',
            'state',
            'commission',
            'description'
        ]
        payments = self.sql_select_all(sql)
        total = 0
        response = self.sql_map_results(mapper, payments)

        for row in response:
            total += row.get('commission')
        return Response({"data": response, "total": total})


class BobByClient(APIView):
    permission_classes = [HasBobGlobalPermission]
    serializer_class = BobGlobalSerializer

    def get(self, request):
        elements = BobGlobal.objects.filter(
            suscriberid=request.GET.get("suscriberid")
        ).order_by("-term_date")
        if len(elements) > 0:
            serializer = self.serializer_class(elements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ExportsCommons(
    ClientAppUtils,
    DirectSql,
    AgencyManagement,
):
    def get_entries(self, request, extra_fields=False):
        filters = self.apply_filters(request)
        ordering = self.get_exports_order(request)
        joins = self.get_exports_joins()
        extra_fields_sql = ", c.princome, c.conincome, c.email, c.addreess" if extra_fields else ""
        sql = f"""Select concat(c.names,' ',c.lastname)as client_name,c.telephone,c.suscriberid,
                c.date_birth,i.names,c.application_id,s.names,
                concat(ag.agent_name,' ',ag.agent_lastname)as agent_names,c.family_menber,
                c.agent2, concat(a.assistant_name, ' ', a.assistant_lastname) as assistant_names,
                concat(cp.names, ' ', cp.lastnames) {extra_fields_sql}
                 
                   from client c {joins}
                where c.borrado <>1 and c.tipoclient <> 2
                and c.tipoclient <> 4 {filters} group by c.id {ordering}
                """

        values = self.sql_select_all(sql)
        return values

    def get_exports_joins(self):
        sql = """left join insured i on c.id_insured = i.id left join state s 
            on c.id_state = s.id left join agent ag on c.id_agent = ag.id left join
            assistant a on ag.id_assistant = a.id left join client_parient cp on
            (cp.id_client = c.id and cp.pos = 0)
            """
        return sql

    def get_exports_order(self, request):
        order = " "
        default = "order by client_name"
        order_field = self.check_none(request.GET.get("order"))
        desc = self.check_none(request.GET.get("desc"))
        if order_field:
            if order_field == "names":
                order += "order by client_name"
            elif order_field == "agent":
                order += "order by agent_names"
            elif order_field == "insured":
                order += "order by i.names"
            elif order_field == "state":
                order += "order by s.names"
            else:
                try:
                    test = Client.objects.all().only(order_field)[0]
                    order += f"order by {order_field}"
                except:
                    order = default
            if desc:
                order += f" desc"
        else:
            order = default
        return order

    def get_mapings(self):
        return [
            "client_names",
            "telephone",
            "suscriberId",
            "irthdate",
            "nsurance",
            "applicationId",
            "state",
            "agent_names",
            "member_n",
            "agent2",
            "assistant_names",
            "spouse",
            "princome",
            "conincome",
            "email",
            "addreess",
        ]


class ExportExcelClient(XLSXFileMixin, ReadOnlyModelViewSet, ExportsCommons):
    permission_classes = [HasClientPermission]
    serializer_class = ClientExportSerializer
    renderer_classes = (XLSXRenderer,)
    xlsx_use_labels = True
    filename = "clients.xlsx"
    xlsx_ignore_headers = []

    def list(self, request, *args, **kwargs):
        values = self.get_entries(request, True)
        values = self.sql_map_results(self.get_mapings(), values)
        serializer = self.get_serializer(values, many=True)
        return Response(serializer.data)


class ExportPdfClient(APIView, ExportsCommons, PDFCommons):
    permission_classes = [HasClientPermission]

    def truncate_string(self, string, max_length=10):
        if len(string) > max_length:
            return string[:max_length] + "..."
        else:
            return string

    def get(self, request):
        values = self.get_entries(request)

        data = [
            [i + 1, self.truncate_string(r[0],
                                         30).replace(" ", "\n", 1) if r[0] else ""]
            + list(r[1:-5])
            + [r[-1].replace(" ", "\n", 1) if r[-1] else ""]
            + [r[-5].replace(" ", "\n", 1) if r[-5] else "", r[-4]]
            for i, r in enumerate(values)
        ]
        headers = [
            "Indx",
            "Client Name",
            "Telephone",
            "Suscriber",
            "Birthdate",
            "Insurance",
            "Application",
            "State",
            "Spouse",
            "Agent Name",
            "Ins. #",
        ]
        return self.pdf_create_table(headers, data, A2)


class ImportSMSExcel(APIView, SmsCommons):
    def post(self, request: APIViewRequest):
        service = self.sms_get_service()
        user: CustomUser = request.user
        if user.company_phone_number:
            company_number = user.company_phone_number
        else:
            company_number = random.choice(
                self.get_company_numbers_for_mass_sending())
        body = request.data.get('body', None)
        telephone_pos = int(request.data.get('telephone', '-1'))
        if not body or telephone_pos == -1:
            raise ValidationException('Missing Fields')
        else:
            try:
                file = request.data.get("file")
                decoded_file = file.read().decode()
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)

                first_check = 1
                for pos, row in enumerate(reader):
                    if first_check:
                        first_check = 0
                        continue
                    telephone = row[telephone_pos]
                    message = service.send_custom_sms(
                        from_=company_number, to=telephone, sms=body)

                return Response('Sended',
                                status=status.HTTP_200_OK,
                                )
            except:
                raise ValidationException('Error')
