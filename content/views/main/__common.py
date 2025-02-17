from ..imports import *
from content.business.logging.db_logging_service import ClientLogging


class ClientAppUtils(ClientLogging, AgencyManagement):
    def add_to_payment(self, data: dict):
        new_client = data
        client_id, agent_id, tipoclient = (
            new_client["id"],
            new_client["id_agent"],
            new_client["tipoclient"],
        )
        try:
            year = int(data["aplication_date"][:4])
        except:
            year = int(data["aplication_date"].year)

        if not Payments.objects.filter(
            id_agent=agent_id, id_client=client_id, fecha=year
        ).exists():
            # if ((tipoclient != 2 and tipoclient != 4) and (not Payments.objects.filter(id_agent=agent_id, id_client=client_id, fecha=year).exists())):
            new_payment = Payments(
                None, agent_id, client_id, year, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            new_payment.save()

    def add_to_pending_docs(self, pending_docs: list, client_id: int):
        current_pending_docs = PendingDocuments.objects.filter(
            id_client=client_id)
        for c in current_pending_docs:
            c.delete()
        for i, pd in enumerate(pending_docs):
            if "upload_date" in pd.keys() and pd["upload_date"] == "":
                pd.pop("upload_date")
            if "end_date" in pd.keys() and pd["end_date"] == "":
                pd.pop("end_date")
            pd["id_client"] = client_id
            new_doc = PendingDocumentsSerializer(data=pd)
            new_doc.is_valid(raise_exception=True)
            new_doc.save()

    def add_app_problems(self, problems: list, client_id: int):
        current_problems = ApplicationProblem.objects.filter(
            id_client=client_id)
        for c in current_problems:
            c.delete()
        for i, pd in enumerate(problems):
            new_doc = ApplicationProblem(
                id_client=client_id,
                id_problem=pd
            )
            new_doc.save()

    def add_to_dependants(self, dependants: list, client_id: int):
        current_dependants = ClientParient.objects.filter(id_client=client_id).exclude(
            pos=0
        )
        for d in current_dependants:
            d.delete()
        for i, d in enumerate(dependants):
            d["id_client"] = client_id
            d["pos"] = i + 1
            if "cardexp" in d.keys() and d["cardexp"] == "":
                d.pop("cardexp")
            if "date_brith" in d.keys() and d["date_brith"] == "":
                d.pop("date_brith")
            if "fechaexdition" in d.keys() and d["fechaexdition"] == "":
                d.pop("fechaexdition")
            new_dependant = ClientParientSerializer(data=d)
            new_dependant.is_valid(raise_exception=True)
            new_dependant.save()

    def add_spouse(self, data: dict, client_id):
        current_dependants = ClientParient.objects.filter(
            id_client=client_id, pos=0)
        for d in current_dependants:
            d.delete()
        # if not "spouse" in data.keys() or not data["spouse"]:
        #     return
        data["id_client"] = client_id
        data["pos"] = 0
        new_dependant = ClientParientSerializer(data=data)
        new_dependant.is_valid(raise_exception=True)
        new_dependant.save()

    def check_existing_application(self, client: Client, next_year):
        return Client.objects.filter(suscriberid=client.suscriberid, aplication_date__year=next_year).exclude(tipoclient=1).exclude(tipoclient=3).exclude(borrado=1).exclude(Q(suscriberid="") | Q(suscriberid="n/a") | Q(suscriberid="N/A")).count() != 0

    def check_existing_client(self, client: Client):
        try:
            year = int(client.aplication_date[:4])
        except:
            year = int(client.aplication_date.year)
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        # count = Client.objects.exclude(Q(borrado=1) | Q(id_agent=0)).filter(

        count1 = 0
        count2 = 0
        if client.tipoclient == 1 or client.tipoclient == 3:
            count1 = (
                Client.objects.exclude(Q(borrado=1) | Q(id_agent=0))
                .exclude(Q(suscriberid="") | Q(suscriberid="n/a") | Q(suscriberid="N/A"))
                .filter(
                    tipoclient=1,
                    suscriberid=client.suscriberid,
                    aplication_date__range=[start, end],
                )
                .count()
            )
            count2 = (
                Client.objects.exclude(Q(borrado=1) | Q(id_agent=0))
                .exclude(Q(suscriberid="") | Q(suscriberid="n/a") | Q(suscriberid="N/A"))
                .filter(
                    tipoclient=3,
                    suscriberid=client.suscriberid,
                    aplication_date__range=[start, end],
                )
                .count()
            )
        elif client.tipoclient == 2 or client.tipoclient == 4:
            count1 = (
                Client.objects.exclude(Q(borrado=1) | Q(id_agent=0))
                .exclude(Q(suscriberid="") | Q(suscriberid="n/a") | Q(suscriberid="N/A"))
                .filter(
                    tipoclient=1,
                    suscriberid=client.suscriberid,
                    aplication_date__range=[start, end],
                )
                .count()
            )
            count2 = (
                Client.objects.exclude(Q(borrado=1) | Q(id_agent=0))
                .exclude(Q(suscriberid="") | Q(suscriberid="n/a") | Q(suscriberid="N/A"))
                .filter(
                    tipoclient=3,
                    suscriberid=client.suscriberid,
                    aplication_date__range=[start, end],
                )
                .count()
            )
        count = count1 + count2
        if count > 1:
            raise ValidationException(
                "There is already a client with similar suscriber ID."
            )

    def apply_filters(self, request: HttpRequest, applicationsView=False) -> str:
        user: CustomUser = request.user
        sql = " "

        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.GET.get("agent"), user.pk)
        assistant = self.select_assistant(
            request.GET.get("assistant"), user.pk)
        agency = self.select_agency(request.GET.get("agency"), user.pk)

        if assistant:
            clients = self.get_assistant_clients(
                assistant.pk, applicationsView)
        elif applicationsView:
            clients = self.get_related_applications(
                user.pk, True, ["id", "id_agent"])
        else:
            clients = self.get_related_clients(
                user.pk, True, ["id", "id_agent"])

        if agent:
            agents = agents.filter(pk=agent.pk)
        if agency:
            agents = agents.filter(id_agency=agency.pk)
        clients = clients.filter(id_agent__in=self.queryset_to_list(agents))

        sql += f" and c.id in ({self.queryset_to_list(clients, to_string=True)})"

        search: str = self.check_none(request.GET.get("search"))
        if search:
            sql += f""" AND (concat(c.names,' ',c.lastname) like '%{search}%' 
                or c.suscriberid like '%{search}%' OR REPLACE(c.telephone, '-', '') LIKE '%{search}%') """
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            sql = sql + " AND c.id_insured=" + insured + " "
        state = self.check_none(request.GET.get("state"))
        if state:
            sql = sql + " AND c.id_state=" + state + " "
        worked_by = self.check_none(request.GET.get("worked_by"))
        if worked_by:
            sql = sql + f" AND c.worked_by='{worked_by}' "
        year = self.check_none(request.GET.get("year"))
        if year:
            sql = (
                sql
                + ' AND SUBSTRING(c.aplication_date,1,4)="'
                + str(request.GET.get("year"))
                + '" '
            )
        greaterThan63 = self.check_none(request.GET.get("greaterThan63"))
        if greaterThan63:
            today = date.today()
            minus63 = date(today.year - 64, today.month, today.day)
            sql = sql + f" AND c.date_birth<='{minus63}'"
        date_start = self.check_none(request.GET.get("date_start"))
        if date_start:
            sql = (
                sql
                + " AND c.fechacreado >'"
                + str(request.GET.get("date_start"))
                + "' "
            )
        date_end = self.check_none(request.GET.get("date_end"))
        if date_end:
            sql = (
                sql + " AND c.fechacreado <'" +
                str(request.GET.get("date_end")) + "' "
            )
        no_suscriber = self.check_none(request.GET.get("no_suscriber"))
        if no_suscriber:
            sql = (
                sql
                + f""" AND (c.suscriberid = 'n/a' or c.suscriberid = 'N/A' or c.suscriberid = '' or c.suscriberid is null)"""
            )

        pending = self.check_none(request.GET.get("pending"))
        if pending and pending != "0":
            sql = sql + \
                f""" AND c.pending {'=' if pending == '1' else '<>'} 1"""

        renewed = self.check_none(request.GET.get("renewed"))
        if renewed and renewed != "0":
            sql = sql + \
                f""" AND (c.renewed {'=1' if renewed == '1' else ' is NULL '})"""

        months = self.check_none(request.GET.getlist("month[]"), [])
        if len(months):
            sql += " and ("
            for m in months:
                sql += f""" month(c.aplication_date)={m} or"""
            sql = sql[:-2] + ")"

        return sql

    def apply_ordering(
        self, request: HttpRequest, default_order: str = "names, lastname"
    ) -> str:
        order = ""
        default = f"order by {default_order}"
        order_field = self.check_none(request.GET.get("order"))
        desc = self.check_none(request.GET.get("desc"))
        if order_field:
            if order_field == "agent":
                order += f"order by other.agent_name"
            elif order_field == "insured":
                order += f"order by other.names"
            elif order_field == "state":
                order += f"order by other.names"
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

    def apply_alternate_joins(self, request: HttpRequest) -> str:
        join = ""
        order_field = self.check_none(request.GET.get("order"))
        if order_field:
            if order_field == "agent":
                join = "left join agent other on c.id_agent=other.id"
            elif order_field == "insured":
                join = "left join insured other on c.id_insured=other.id"
            elif order_field == "state":
                join = "left join state other on c.id_state=other.id"
        return join

    def migrate_dependants(self, dependtants_list, new_client_id):
        for d in dependtants_list:
            d.pk = None
            d.id_client = new_client_id
            d.save()

    def migrate_notes(self, notes_list, new_client_id):
        for d in notes_list:
            d.pk = None
            d.id_client = new_client_id
            d.save()

    def migrate_client_consent_log(self, old_client_id, new_client_id):
        ClientConsentLog.objects.filter(
            id_client=old_client_id).update(id_client=new_client_id)

    def migrate_documents(self, docs_list, new_client_id):
        for d in docs_list:
            d.pk = None
            d.id_client = new_client_id
            d.save()

    def retrieve_client_app_response(self, client: Client):
        client_dict = model_to_dict(client)
        spouse = ClientParient.objects.filter(id_client=client.pk, pos=0)
        if spouse.exists():
            client_dict.update({"spouse_spouse": True})
            spouse_dict = spouse.values()[0]
            client_dict.update(
                {f"spouse_{k}": v for k, v in spouse_dict.items()})
            serilizer = ClientSpouseSerializer(client_dict)
        else:
            client_dict.update({"spouse_spouse": False})
            serilizer = ClientSerializer(client_dict)
        response = serilizer.data
        dpendants = ClientParient.objects.filter(
            id_client=client.pk).exclude(pos=0)
        pending_docs = PendingDocuments.objects.filter(id_client=client.pk)
        documents = ClientDocument.objects.filter(id_client=client.pk)
        notes = History.objects.filter(id_client=client.pk)
        response["allDependants"] = ClientParientSerializer(
            dpendants, many=True).data
        response["allPendingDocuments"] = PendingDocumentsSerializer(
            pending_docs, many=True
        ).data
        response["allDocuments"] = ClientDocumentSerializer(
            documents, many=True).data
        response["allNotes"] = HistorySerializer(notes, many=True).data
        return response

    def add_first_note(self, client, request):
        first_note = request.data.get("first_note")
        if first_note and first_note.strip() != "":
            serializer = HistorySerializer(
                data=dict(
                    id_client=client.pk,
                    id_agent=client.id_agent,
                    note=first_note,
                    h_date=date.today(),
                )
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()


class AgentAssistantCommon(CompanySMSCommons):
    def exists_users_with_phone(self, phone, current_user):
        correct_phone = self.sms_ready_phone_number(phone)
        user = self.sms_get_user_by_phone(correct_phone)
        if user and user.pk != (current_user.pk if current_user else -1):
            return True
        return False


class ClientSpouseSerializer(serializers.ModelSerializer):
    spouse_names = serializers.CharField()
    spouse_lastnames = serializers.CharField()
    spouse_coverrage = serializers.CharField()
    spouse_social_security = serializers.CharField()
    spouse_alien = serializers.CharField()
    spouse_card = serializers.CharField()
    spouse_src = serializers.CharField()
    spouse_catagory = serializers.CharField()
    spouse_folio = serializers.CharField()
    spouse_depature = serializers.CharField()
    spouse_date_brith = serializers.DateField()
    spouse_fechaexdition = serializers.DateField()
    spouse_cardexp = serializers.DateField()
    spouse_sexo = serializers.IntegerField()
    spouse_id_status = serializers.IntegerField()
    spouse_spouse = serializers.BooleanField()

    class Meta:
        fields = (
            "id",
            "id_agent",
            "id_status",
            "id_poliza",
            "id_insured",
            "id_state",
            "id_event",
            "names",
            "lastname",
            "social_security",
            "suscriberid",
            "marketplace_user",
            "remark",
            "application_id",
            "telephone",
            "email",
            "addreess",
            "agent2",
            "alien",
            "src",
            "card",
            "catagory",
            "folio",
            "depature",
            "princome",
            "conincome",
            "teltrabajo",
            "nomtrabajo",
            "totalincome",
            "aproxmontpay",
            "plansupp",
            "new_plan",
            "usermark",
            "usermarkpw",
            "ccnumber",
            "expdate",
            "toname",
            "billingaddreess",
            "bank",
            "bankacc",
            "routing",
            "paymentconf",
            "nameinsurance",
            "worked_by",
            "family_menber",
            "pending",
            "income",
            "migratory_status",
            "social_security_doc",
            "loss_medicaiad",
            "pendingno",
            "borrado",
            "coverage",
            "sexo",
            "new_ren",
            "priw21099",
            "targeta",
            "targetatipo",
            "cvccode",
            "automaticpay",
            "w2principal",
            "w2conyugue",
            "tipoclient",
            "acepto",
            "unemprincipal",
            "unemconyugue",
            "percent",
            "agent_pay",
            "mo_premium",
            "mensualidad",
            "payment",
            "aplication_date",
            "paid_date",
            "fechaexdition",
            "date_birth",
            "fechacreado",
            "fechainsert",
            "paymentday",
            "cardexp",
            "hora",
            "photo",
            "deductible",
            "max_out_pocket",
            "spouse_names",
            "spouse_lastnames",
            "spouse_coverrage",
            "spouse_social_security",
            "spouse_alien",
            "spouse_card",
            "spouse_src",
            "spouse_catagory",
            "spouse_folio",
            "spouse_depature",
            "spouse_date_brith",
            "spouse_fechaexdition",
            "spouse_cardexp",
            "spouse_sexo",
            "spouse_id_status",
            "spouse_spouse",
        )
        model = Client
