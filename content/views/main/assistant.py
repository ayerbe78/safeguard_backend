from ..imports import *
from .__common import AgentAssistantCommon


class ListAssistantSerializer(serializers.ModelSerializer):
    agent_count = serializers.IntegerField()
    full_name = serializers.CharField()

    class Meta:
        fields = (
            "id",
            "full_name",
            "email",
            "email2",
            "telephone",
            "comition",
            "agent_count",
        )
        model = Assistant


class AssistantViewSet(viewsets.ModelViewSet, AgencyManagement, AgentAssistantCommon, DirectSql):
    permission_classes = [HasAssistantPermission]
    serializer_class = AssistantSerializer

    def get_queryset(self):
        return Assistant.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.get_entries(request)
        page = self.paginate_queryset(entries)
        return self.get_paginated_response(page)

    def get_entries(self, request):
        query = self.__get_query(request)
        maps = [
            "id",
            "full_name",
            "email",
            "email2",
            "telephone",
            "comition",
            "agent_count"
        ]
        result = self.sql_select_all(query, maps)
        for el in result:
            clients = self.get_assistant_clients(
                el.get('id')).filter(aplication_date__year=2024)
            el["client_count"] = len(clients)
            total_family_members_sum = clients.aggregate(
                total_family_members_sum=Sum('family_menber'))['total_family_members_sum']
            el["member_count"] = total_family_members_sum

        return result

    def __get_query(self, request: APIViewRequest):
        return self.__get_base_query(request) + self.apply_order_sql(
            request, "full_name"
        )

    def __get_base_query(self, request: APIViewRequest):
        search = self.check_none(request.GET.get("search"))
        search_filter = ""
        if search:
            search = self.sql_curate_query(search)
            search_filter += f" and (LOWER(CONCAT(a.assistant_name,' ', a.assistant_lastname)) like '%{search.lower()}%' or LOWER(email) like '%{search.lower()}%' or LOWER(email2) like '%{search.lower()}%')"

        sql = f"""
            SELECT 
                a.id,
                CONCAT(a.assistant_name,' ', a.assistant_lastname) AS full_name,
                a.email,
                a.email2,
                a.telephone,
                a.comition,
                COUNT(ag.id) AS agent_count
            FROM
                assistant a
                LEFT JOIN 
                agent ag ON (a.id=ag.id_assistant)
                
            WHERE (a.borrado IS NULL OR a.borrado<>1)  AND ag.borrado <> 1
            GROUP BY a.id {search_filter}
	
        """

        return sql

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response: Response = super().create(request)
                data = {
                    "password": request.data.get("password"),
                    "email": request.data.get("email"),
                    "username": request.data.get("email"),
                    "first_name": request.data.get("assistant_name"),
                    "last_name": request.data.get("assistant_lastname"),
                    "personal_phone_number": request.data.get("telephone"),
                }
                if self.exists_users_with_phone(data["personal_phone_number"], None):
                    raise ValidationException(
                        "There is a user with same phone already")
                new_user_id = self.add_to_users(data)
                self.add_to_group(new_user_id, "Assistant")
                return response
        except Exception as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def add_to_users(self, data):
        serializer = RegisterSerializer
        new_user = serializer(data=data)
        new_user.is_valid(raise_exception=True)
        created = new_user.save()
        CustomUser.objects.filter(id=created.pk).update(
            first_name=data["first_name"],
            last_name=data["last_name"],
            is_assistant=True,
        )
        return created.pk

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            prev_assistant: Assistant = self.get_object()
            response = super().update(request, *args, **kwargs)
            assistant: Assistant = self.get_object()
            assistant_user = CustomUser.objects.get(email=prev_assistant.email)
            assistant_user.email = assistant.email
            assistant_user.username = assistant.email
            if self.exists_users_with_phone(assistant.telephone, assistant_user):
                raise ValidationException(
                    "There is a user with same phone already")
            assistant_user.personal_phone_number = assistant.telephone
            assistant_user.save()
            return response

    def add_to_group(self, user_id, group_name):
        group = Group.objects.get(name=group_name)
        user = CustomUser.objects.get(id=user_id)
        user.groups.add(group)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.borrado = 1
        instance.save()
        return Response(instance.pk)

    @action(methods=["get"], detail=False, url_path="data")
    def data_assistants(self, request: HttpRequest):
        user = request.user
        selects = self.get_selects(user.pk, "agencies")
        return Response(selects)
