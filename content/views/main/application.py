from ..imports import *
from .__common import ClientAppUtils, ClientSpouseSerializer
from django.db.models.functions import Concat, Replace


class ApplicationViewSet(viewsets.ModelViewSet, ClientAppUtils):
    permission_classes = [HasApplicationPermission]
    serializer_class = ClientSerializer
    queryset = Client.objects.filter(Q(tipoclient=2) | Q(tipoclient=4)).exclude(
        Q(id_agent=0) | Q(borrado=1)
    )

    def create(self, request, *args, **kwargs):
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
            new_client.tipoclient = 2
            new_client.save()
            self.check_existing_client(new_client)
            if dependants and isinstance(dependants, list):
                self.add_to_dependants(dependants, new_client.pk)
            if len(spouse_data.keys()):
                self.add_spouse(spouse_data, new_client.pk)
            if pendingdocs and isinstance(pendingdocs, list):
                self.add_to_pending_docs(pendingdocs, new_client.pk)
            # self.add_to_payment(response.data)
            self.add_first_note(new_client, request)
            self.log_application_insert(request.user, new_client.pk)
            return response

    def list(self, request, *args, **kwargs):
        x = date.today()
        a = date(x.year, 1, 1)
        b = date(x.year, 12, 31)
        if request == None:
            queryset = (
                Client.objects.filter(aplication_date__range=[
                                      a, b], tipoclient=2)
                .order_by("names")
                .exclude(id_agent=0)
                .exclude(borrado=1)
            )
        else:
            if request.GET.get("order") == "true":
                queryset = (
                    Client.objects.filter(aplication_date__range=[
                                          a, b], tipoclient=2)
                    .order_by("names")
                    .exclude(id_agent=0)
                    .exclude(borrado=1)
                )
            else:
                queryset = (
                    Client.objects.filter(aplication_date__range=[
                                          a, b], tipoclient=2)
                    .order_by("-names")
                    .exclude(id_agent=0)
                    .exclude(borrado=1)
                )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        client = self.get_object()
        client.borrado = 1
        client.save()
        return Response(client.pk)

    def retrieve(self, request, *args, **kwargs):
        client: Client = self.get_object()
        response = self.retrieve_client_app_response(client)
        return Response(response)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            client = self.get_object()
            spouse_data = {
                k.replace("spouse_", ""): v
                for k, v in request.data.items()
                if "spouse_" in k
            }
            if len(spouse_data.keys()):
                self.add_spouse(spouse_data, client.pk)

            super().update(request, *args, **kwargs)
            return self.retrieve(request)

    @action(methods=["post"], detail=True, url_path="transfer")
    def transfer_to_client(self, request: HttpRequest, pk=None):
        current_app = self.get_object()
        user = request.user
        pendingdocs = self.check_none(request.data.get("pendingdocs"))
        with transaction.atomic():
            if current_app.tipoclient == 4:
                self.mark_old_client_as_renewed(current_app)
            new_date = date.today().strftime("%Y-%m-%d")
            new_data: dict = request.data
            new_data["tipoclient"] = 3
            serializer = self.get_serializer(current_app, data=new_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            client = Client(**serializer.data)
            client.fechainsert = new_date
            client.save()
            self.check_existing_client(client)
            if pendingdocs and isinstance(pendingdocs, list):
                self.add_to_pending_docs(pendingdocs, client.pk)
            self.add_to_payment(serializer.data)
            self.log_client_transfer(user, client.pk)
            return Response(self.get_serializer(client).data)

    def mark_old_client_as_renewed(self, app):
        old_client = Client.objects.filter(aplication_date__year=int(
            app.aplication_date.year)-1, suscriberid=app.suscriberid).exclude(borrado=1).exclude(tipoclient=2).exclude(tipoclient=4)
        if len(old_client) == 1:
            old_client = old_client.get()
            old_client.renewed = 1
            old_client.save()

    @action(methods=["post"], detail=True, url_path="set_visible")
    def set_application_visible(self, request: HttpRequest, pk=None):
        app: Client = self.get_object()
        app.not_visible = 0
        app.app_problem_note = None
        app.sended_to_assistant = datetime.now()
        app.save()
        return Response(self.get_serializer(app).data)

    @action(methods=["post"], detail=True, url_path="set_app_with_problems")
    def set_app_with_problems(self, request: HttpRequest, pk=None):
        app: Client = self.get_object()
        app.not_visible = 1
        app.app_problem_note = request.data.get('app_problem_note')
        app.save()
        self.add_app_problems(request.data.get('problems'), app.id)

        return Response(self.get_serializer(app).data)

    @action(methods=["get"], detail=True, url_path="get_problems")
    def get_problems(self, request: HttpRequest, pk=None):
        app: Client = self.get_object()
        problems = ApplicationProblem.objects.filter(
            id_client=app.id).values("id_problem")
        problems = self.queryset_to_list(problems, "id_problem")
        int_list = [int(item) for item in problems]
        return Response(int_list)

    @action(methods=["get"], detail=False, url_path="filter")
    def filter(self, request: HttpRequest):
        filters = self.apply_filters(request, True)
        ordering = self.apply_ordering(request)
        alternate_joins = self.apply_alternate_joins(request)

        problem_id = self.check_none(request.GET.get('problem'))
        problem_filter = ""
        if problem_id and int(problem_id) > 0:
            problem_filter = f" AND apl.id_problem={problem_id}"
        elif problem_id and int(problem_id) == -1:
            problem_filter = " and (not_visible is null or not_visible = 0) and apl.id_problem is null"
        elif problem_id and int(problem_id) == -2:
            problem_filter = " and (not_visible is not null and not_visible <>0  ) and (app_problem_note is null or app_problem_note='') and apl.id_problem is null"
        elif problem_id and int(problem_id) == -3:
            problem_filter = " and (apl.id_problem is not null or (not_visible is not null and not_visible <>0 ))"

        sql = """Select c.*,  GROUP_CONCAT(pro.names ORDER BY pro.names SEPARATOR ', ') AS problems
            from client c 
            LEFT JOIN application_problems apl ON c.id= apl.id_client
		    LEFT JOIN problems pro ON apl.id_problem = pro.id {}
            where c.borrado <>1 and (c.tipoclient=2 or c.tipoclient = 4) {} {} 
            group by c.id {}""".format(alternate_joins, problem_filter, filters.replace(
            "%", "%%"), ordering
        )

        applications = Client.objects.raw(sql)
        results = self.paginate_queryset(applications)
        serializer = ApplicationSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["get"], detail=False, url_path="lite")
    def get_applications_lite(self, request: HttpRequest):
        user: CustomUser = request.user
        search = self.check_none(
            request.GET.get('search'), '').replace(" ", "")
        applications = self.get_related_applications(user.pk, include_self=True, only=['id', 'names', 'lastname']).annotate(
            full_name=Concat("names", V(" "), "lastname"),
            full_name_no_spaces=Replace(
                Replace(
                    Replace(Concat("names", V(" "), "lastname"), V(" "), V("")),
                    V("\t"), V(""),
                ),
                V("\n"), V(""),
            )
        ).filter(full_name_no_spaces__icontains=search)[:50]
        results = self.paginate_queryset(applications)
        serializer = ClientSerializerLite(results, many=True)
        return self.get_paginated_response(serializer.data)


class DataForApplication(APIView, AgencyManagement):
    permission_classes = [HasApplicationPermission]
    serializer_class = AssitStateSerializer

    def get(self, request):
        user = request.user
        if not (user.is_admin or user.has_perm("content.view_application")):
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
        problems = (
            Problem.objects.all()
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
        problems_serializer = ProblemSerializer(problems, many=True)

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
            "problems": problems_serializer.data,
        }
        response.update(new_selects)
        return Response(
            response,
            status=status.HTTP_200_OK,
        )
