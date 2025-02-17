from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from customauth.GroupsPermission import HasUserPermission, IsAdmin
from .serializers import *
from datetime import timedelta
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import LimitOffsetPagination
from django.db import transaction
from content.business.business import AgencyManagement, CompanySMSCommons, Common
from content.views.sms.models.sms_models import SMSConversation
from django.db.models import Max, Sum, Q, F, Value as V, Count
from django.db.models.functions import Concat


class RegisterAPI(generics.GenericAPIView):
    permission_classes = [IsAdmin]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if (
            request.data.get("first_name") != None
            and request.data.get("last_name") != None
        ):
            CustomUser.objects.filter(id=user.id).update(
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
            )
            user = CustomUser.objects.filter(id=user.id).get()
        if request.data.get("is_admin"):
            CustomUser.objects.filter(id=user.id).update(is_admin=True)
            user = CustomUser.objects.filter(id=user.id).get()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )

        # ip = request.META['REMOTE_ADDR']
        # if ip in ALLOWED_IP:
        #
        # else:
        #     return Response(status=status.HTTP_403_FORBIDDEN)


class UserInitialUpdate(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        user = CustomUser.objects.get(id=request.data.get("id"))
        if request.data.get("is_agent"):
            user.is_agent = True
        if request.data.get("is_assistant"):
            user.is_assistant = True
        if request.data.get("is_subassistant"):
            user.is_subassistant = True
        if request.data.get("is_admin"):
            user.is_admin = True
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if request.data.get("remember"):
            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "token": AuthToken.objects.create(user, expiry=timedelta(hours=24))[
                        1
                    ],
                }
            )
        else:
            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "token": AuthToken.objects.create(user)[1],
                }
            )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    # def get_object(self):
    #     return self.request.user

    def retrieve(self, request):
        user: CustomUser = request.user
        serializer = self.get_serializer(user)
        response = serializer.data
        if user.is_agent:
            agent: Agent = Agent.objects.get(email=user.email)
            response["id_agent"] = agent.id if agent else None
        elif user.is_assistant:
            assistant: Assistant = Assistant.objects.get(email=user.email)
            response["id_assistant"] = assistant.id if assistant else None

        return Response(response)


class UserUpdateAPI(generics.UpdateAPIView, CompanySMSCommons):
    permission_classes = [HasUserPermission]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            user: CustomUser = self.get_object()
            new_phone = request.data.get("company_phone_number")
            new_phone = new_phone if new_phone else user.company_phone_number
            if new_phone:
                new_phone = self.sms_ready_phone_number(new_phone)
                self.sms_check_no_user_with_same_phone(new_phone, user.pk)
            else:
                new_phone = None
            SMSConversation.objects.filter(peer=user).update(
                peer_number=new_phone if new_phone else ""
            )
            response = super().update(request, *args, **kwargs)
            user: CustomUser = self.get_object()
            permission = Permission.objects.get(codename="has_sms")
            if user.company_phone_number and user.company_phone_number != "":
                if not user.has_perm(f"content.{permission.codename}"):
                    user.user_permissions.add(permission)
            else:
                if user.has_perm(f"content.{permission.codename}"):
                    user.user_permissions.remove(permission)

            return response


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user


class AdminChangeAgentPasswordView(generics.UpdateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminChangeAgentPasswordSerializer

    def get_object(self):
        return self.request.user


class AdminChangeAssistantPasswordView(generics.UpdateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminChangeAssistantPasswordSerializer

    def get_object(self):
        return self.request.user


class AdminChangeUserPasswordView(generics.UpdateAPIView):

    permission_classes = [IsAdmin]
    serializer_class = AdminChangeUserPasswordSerializer

    def get_object(self):
        return self.request.user


class AddNewGroup(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        name = request.data.get("name")
        if name != None:
            new_group = Group.objects.create(name=name)
            serializer = GroupSerializer(new_group, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class EditGroup(generics.UpdateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAdmin]
    queryset = Group.objects.all()


class DeleteGroup(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        group = Group.objects.filter(id=request.data.get("group_id"))
        if len(group) == 1:
            group = group.get()
            group.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetGroups(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetUsers(APIView, LimitOffsetPagination, Common):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = CustomUser.objects.all().order_by("first_name", "last_name")

        for user in users:
            groups = ""
            user_groups = user.groups.all()
            for group in user_groups:
                if groups == "":
                    groups = group.name
                else:
                    groups = groups + "," + group.name
            user.groups_name = groups
        results = self.paginate_queryset(users, request, view=self)
        serializer = ListUserSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def get(self, request):
        users = self.__apply_filters(request)
        users = self.__apply_search(users, request)
        users = self.apply_order_queryset(users, request, "full_name")

        results = self.paginate_queryset(users, request, view=self)
        serializer = NewListUserSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_filters(self, request):
        group = self.check_none(request.GET.get('permission_group'))
        users = CustomUser.objects.all().annotate(
            full_name=Concat("first_name", V(" "), "last_name")
        )
        if group:
            users = users.filter(groups=group)
        return users

    def __apply_search(self, queryset, request):
        search = request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(company_phone_number__icontains=search)
            )
        return queryset


class GetUsersSelects(APIView, AgencyManagement):
    def get(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "agencies", "permission_groups")
        return Response(selects)


class GetUserLoginPermissions(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = CustomUser.objects.filter(id=request.GET.get("id"))
        if len(user) == 1:
            user = user.get()
            if user == request.user:
                arr = []
                if user.is_admin:
                    all_permissions = Permission.objects.all()
                    for permission in all_permissions:
                        arr.append(permission.codename)
                    all_groups = Group.objects.all()
                    for group in all_groups:
                        arr.append("group_" + group.name)
                else:
                    user_permissions = user.user_permissions.all()
                    for permission in user_permissions:
                        arr.append(permission.codename)
                    groups = user.groups.all()
                    for group in groups:
                        group_permissions = group.permissions.all()
                        arr.append("group_" + group.name)
                        for permission in group_permissions:
                            arr.append(permission.codename)
                return Response(arr)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AddPermissionToGroup(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        model = request.data.get("model")
        type = request.data.get("type")
        group = Group.objects.filter(id=request.data.get("group_id"))
        if (
            len(group) == 1
            and model != None
            and type == "add"
            or type == "view"
            or type == "change"
            or type == "delete"
        ):
            group = group.get()
            permission = Permission.objects.filter(codename=f"{type}_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RemovePermissionFromGroup(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        permission = Permission.objects.filter(
            id=request.data.get("permission_id"))
        group = Group.objects.filter(id=request.data.get("group_id"))
        if len(permission) == 1 and len(group) == 1:
            permission = permission.get()
            group = group.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        group.permissions.remove(permission)
        return Response(status=status.HTTP_200_OK)


class AddUserToGroup(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        user = CustomUser.objects.filter(id=request.data.get("user_id"))
        group = Group.objects.filter(id=request.data.get("group_id"))
        if len(user) == 1 and len(group) == 1:
            user = user.get()
            group = group.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.groups.add(group)
        return Response(status=status.HTTP_200_OK)


class RemoveUserFromGroup(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        user = CustomUser.objects.filter(id=request.data.get("user_id"))
        group = Group.objects.filter(id=request.data.get("group_id"))
        if len(user) == 1 and len(group) == 1:
            user = user.get()
            group = group.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)


class AddPermissionToUser(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        model = request.data.get("model")
        type = request.data.get("type")
        user = CustomUser.objects.filter(id=request.data.get("user_id"))
        if (
            len(user) == 1
            and model != None
            and type == "add"
            or type == "view"
            or type == "change"
            or type == "delete"
        ):
            user = user.get()
            permission = Permission.objects.filter(codename=f"{type}_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class EditUserPermissions(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        model = request.data.get("model")
        user = CustomUser.objects.filter(id=request.data.get("user_id"))
        if len(user) == 1:
            user = user.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if (
            int(request.data.get("add")) == 1
            and user.has_perm(f"content.add_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"add_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("add")) == 0 and user.has_perm(
                f"content.add_{model}"
            ):
                permission = Permission.objects.filter(codename=f"add_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("change")) == 1
            and user.has_perm(f"content.change_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"change_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("change")) == 0 and user.has_perm(
                f"content.change_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"change_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("view")) == 1
            and user.has_perm(f"content.view_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"view_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("view")) == 0 and user.has_perm(
                f"content.view_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"view_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("del")) == 1
            and user.has_perm(f"content.delete_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"delete_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("del")) == 0 and user.has_perm(
                f"content.delete_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"delete_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)

        return Response(status=status.HTTP_200_OK)


class EditGroupPermissions(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        model = request.data.get("model")
        group = Group.objects.filter(id=request.data.get("group_id"))
        if len(group) == 1:
            group = group.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (
            int(request.data.get("add")) == 1
            and group.permissions.filter(codename=f"add_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"add_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("add")) == 0
                and group.permissions.filter(codename=f"add_{model}").count() == 1
            ):
                permission = Permission.objects.filter(codename=f"add_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("change")) == 1
            and group.permissions.filter(codename=f"change_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"change_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("change")) == 0
                and group.permissions.filter(codename=f"change_{model}").count() == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"change_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("view")) == 1
            and group.permissions.filter(codename=f"view_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"view_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("view")) == 0
                and group.permissions.filter(codename=f"view_{model}").count() == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"view_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("del")) == 1
            and group.permissions.filter(codename=f"delete_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"delete_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("del")) == 0
                and group.permissions.filter(codename=f"delete_{model}").count() == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"delete_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)

        return Response(status=status.HTTP_200_OK)


class NewEditUserPermissions(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        model = request.data.get("model")
        user = CustomUser.objects.filter(id=request.data.get("user_id"))
        if len(user) == 1:
            user = user.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if (
            int(request.data.get("add")) == 1
            and user.has_perm(f"content.add_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"add_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("add")) == 0 and user.has_perm(
                f"content.add_{model}"
            ):
                permission = Permission.objects.filter(codename=f"add_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("change")) == 1
            and user.has_perm(f"content.change_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"change_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("change")) == 0 and user.has_perm(
                f"content.change_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"change_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("view")) == 1
            and user.has_perm(f"content.view_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"view_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("view")) == 0 and user.has_perm(
                f"content.view_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"view_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("del")) == 1
            and user.has_perm(f"content.delete_{model}") == False
        ):
            permission = Permission.objects.filter(codename=f"delete_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("del")) == 0 and user.has_perm(
                f"content.delete_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"delete_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("export_pdf")) == 1
            and user.has_perm(f"content.export_pdf_{model}") == False
        ):
            permission = Permission.objects.filter(
                codename=f"export_pdf_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("export_pdf")) == 0 and user.has_perm(
                f"content.export_pdf_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"export_pdf_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)
        if (
            int(request.data.get("export_excel")) == 1
            and user.has_perm(f"content.export_excel_{model}") == False
        ):
            permission = Permission.objects.filter(
                codename=f"export_excel_{model}")
            if len(permission) == 1:
                permission = permission.get()
                user.user_permissions.add(permission)
        else:
            if int(request.data.get("export_excel")) == 0 and user.has_perm(
                f"content.export_excel_{model}"
            ):
                permission = Permission.objects.filter(
                    codename=f"export_excel_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    user.user_permissions.remove(permission)

        return Response(status=status.HTTP_200_OK)


class NewEditGroupPermissions(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        model = request.data.get("model")
        group = Group.objects.filter(id=request.data.get("group_id"))
        if len(group) == 1:
            group = group.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (
            int(request.data.get("add")) == 1
            and group.permissions.filter(codename=f"add_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"add_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("add")) == 0
                and group.permissions.filter(codename=f"add_{model}").count() == 1
            ):
                permission = Permission.objects.filter(codename=f"add_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("change")) == 1
            and group.permissions.filter(codename=f"change_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"change_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("change")) == 0
                and group.permissions.filter(codename=f"change_{model}").count() == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"change_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("view")) == 1
            and group.permissions.filter(codename=f"view_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"view_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("view")) == 0
                and group.permissions.filter(codename=f"view_{model}").count() == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"view_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("del")) == 1
            and group.permissions.filter(codename=f"delete_{model}").count() == 0
        ):
            permission = Permission.objects.filter(codename=f"delete_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("del")) == 0
                and group.permissions.filter(codename=f"delete_{model}").count() == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"delete_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("export_pdf")) == 1
            and group.permissions.filter(codename=f"export_pdf_{model}").count() == 0
        ):
            permission = Permission.objects.filter(
                codename=f"export_pdf_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("export_pdf")) == 0
                and group.permissions.filter(codename=f"export_pdf_{model}").count()
                == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"export_pdf_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)
        if (
            int(request.data.get("export_excel")) == 1
            and group.permissions.filter(codename=f"export_excel_{model}").count() == 0
        ):
            permission = Permission.objects.filter(
                codename=f"export_excel_{model}")
            if len(permission) == 1:
                permission = permission.get()
                group.permissions.add(permission)
        else:
            if (
                int(request.data.get("export_excel")) == 0
                and group.permissions.filter(codename=f"export_excel_{model}").count()
                == 1
            ):
                permission = Permission.objects.filter(
                    codename=f"export_excel_{model}")
                if len(permission) == 1:
                    permission = permission.get()
                    group.permissions.remove(permission)

        return Response(status=status.HTTP_200_OK)


class RemovePermissionFromUser(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        permission = Permission.objects.filter(
            id=request.data.get("permission_id"))
        user = CustomUser.objects.filter(id=request.data.get("user_id"))
        if len(permission) == 1 and len(user) == 1:
            permission = permission.get()
            user = user.get()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.user_permissions.remove(permission)
        return Response(status=status.HTTP_200_OK)


class PermissionCommons:
    def get_main_maps(self):
        return (
            "Main",
            [
                ["agent"],
                ["assistant"],
                ["application"],
                ["client"],
                ["clientdocument", "Client Documents"],
                ["bobglobal", "BOB Global"],
                ["marketplace", "Marketplace"],
                ["clientmedicaid", "Client Medicaid"],
            ],
        )

    def get_settings_maps(self):
        return (
            "Settings",
            [
                ["product"],
                ["state"],
                ["city"],
                ["county"],
                ["language"],
                ["insured", "Insurance Carrier"],
                ["healthplan", "Health Plan"],
                ["specialelection", "Special Election"],
                ["socservicerefe", "Soc. Services Referral"],
                ["type"],
                ["planname", "Plan Name"],
                ["status"],
                ["poliza", "Policy"],
                ["documenttype", "Document Types"],
                ["event", "Events"],
                ["agency", "Agency Name"],
                ["groups"],
                ["commagent", "Commision Agent"],
                ["groupcommission", "Commision Groups"],
                ["commissionsgroup", "Groups Commissions"],
                ["commagency", "Commision Agency"],
                ["secondaryagent", "Secondary Agent"],
                ["secondaryoverride", "Secondary Overrides"],
                ["subidtemplate", "Subscriber ID Template"],
                ["problem", "App Problems"],
                ["agenttaxdocument", "Agent Tax Document"],
            ],
        )

    def get_utility_maps(self):
        return (
            "Utilities",
            [
                ["importpaymentcsv", "Import Payment"],
                ["importbob", "Import BOB"],
                ["sms_excel", "SMS Excel"],
                ["video", "Upload Video"],
                ["importfloridablue", "Import Florida Blue"],
                ["importclients", "Import Client"],
                ["add_agentexcel", "Import Agent Excel"],
                ["deletepayment", "Delete Payment"],
                ["generatepayment", "Generate Payment"],
                ["preletterlog", "PreLetter"],
                ["pdfnotice", "PDF Notice"],
                ["generateoriginalpayment", "Generate Original Payment"],
            ],
        )

    def get_reports_maps(self):
        return (
            "Reports",
            [
                ["generalpayment", "General Payments Table"],
                ["paymentglobalagent", "Payment Global Agent"],
                ["paymentglobalagency", "Payment Global Agency"],
                ["paymentglobalagencyagent", "Payment Global Agency Agent"],
                ["paymentglobalclient", "Payment Global"],
                ["paymentinsuredonly", "Payment Insured Only"],
                ["paymentdiscrepancies", "Payment Discrepancies"],
                ["clientbycompanies", "Client By Companies"],
                ["pendingdocs", "Pending Documents"],
                ["paymentglobalassistant", "Payment Global Assistant"],
                ["paymentglobaloriginal", "Original Payment Global"],
                ["paymentclientoriginal", "Original Payment Global"],
                ["paymentdiscrepanciesoriginal", "Original Payment Discrepancies"],
                ["paymentdifferences", "Payment Differences"],
                ["clientconsentlog", "Client Consent Log"],
                ["assistantproduction", "Assistant Production"],
                ["override"],
                [
                    "paymentoverrideassistant",
                    "Payment Override Assistant",
                ],
                [
                    "genericreports",
                    "Generic Reports",
                ],
                [
                    "repaymentsreport",
                    "Repayments Report",
                ],
                [
                    "agencyrepayment",
                    "Agency Repayments",
                ],
                [
                    "releasedagents",
                    "Realesed Agents",
                ],
                ["claim"],
            ],
        )

    def get_dashboard_maps(self):
        return (
            "Dashboard",
            [
                ["assistantpanel", "Assistants Panel"],
                ["clientapppanel", "Applications/Client Panel"],
                ["pendingdocssummary", "Pending Documents Panel"],
                ["insurancepaymentbalance", "Insurance Payments Balance"],
                ["clientsummary", "Insurances Client Summary"],
                ["clientsummarypercentage", "Clients Summary Percentages"],
                ["birthdays", "Today Birthdays Table"],
            ],
        )


class GETGroupPermissions(APIView, PermissionCommons):
    permission_classes = [IsAdmin]

    def get(self, request):
        group_id = request.GET.get("group_id")
        groups = Group.objects.filter(pk=group_id)
        if groups.exists():
            group = groups.get(pk=group_id)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

        permissions = []
        permissions = self.__update_permission(
            permissions, group, self.get_main_maps)
        permissions = self.__update_permission(
            permissions, group, self.get_settings_maps
        )
        permissions = self.__update_permission(
            permissions, group, self.get_utility_maps
        )
        permissions = self.__update_permission(
            permissions, group, self.get_reports_maps
        )
        permissions = self.__update_permission(
            permissions, group, self.get_dashboard_maps
        )

        return Response(permissions)

    def __update_permission(self, permissions: list, group, map_func):
        section, new_perms = map_func()
        permissions += list(
            map(lambda i: self.__generate_permission(
                section, i, group), new_perms)
        )
        return permissions

    def __generate_permission(self, section: str, model_name: list, group):
        model = model_name[0]
        name = model_name[1] if len(model_name) > 1 else model.capitalize()

        return {
            "id": f"{group.pk}-{section}-{model}-{name}",
            "section": section,
            "model": model,
            "displayName": name,
            "add": self.__get_permission(group, "add", model),
            "view": self.__get_permission(group, "view", model),
            "change": self.__get_permission(group, "change", model),
            "delete": self.__get_permission(group, "delete", model),
            "export_pdf": self.__get_permission(group, "export_pdf", model),
            "export_excel": self.__get_permission(group, "export_excel", model),
        }

    def __get_permission(self, group, action, model):
        permission = f"{action}_{model}"
        if Permission.objects.filter(codename=permission).exists():
            return group.permissions.filter(codename=permission).count()
        else:
            return -1


class GETUserPermissions(APIView, PermissionCommons):
    permission_classes = [IsAdmin]

    def get(self, request):
        user_id = request.GET.get("user_id")
        users = CustomUser.objects.filter(pk=user_id)
        if users.exists():
            user = users.get(pk=user_id)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

        permissions = []
        permissions = self.__update_permission(
            permissions, user, self.get_main_maps)
        permissions = self.__update_permission(
            permissions, user, self.get_settings_maps
        )
        permissions = self.__update_permission(
            permissions, user, self.get_utility_maps)
        permissions = self.__update_permission(
            permissions, user, self.get_reports_maps)
        permissions = self.__update_permission(
            permissions, user, self.get_dashboard_maps
        )

        return Response(permissions)

    def __update_permission(self, permissions: list, user, map_func):
        section, new_perms = map_func()
        permissions += list(
            map(lambda i: self.__generate_permission(section, i, user), new_perms)
        )
        return permissions

    def __generate_permission(self, section: str, model_name: list, user):
        model = model_name[0]
        name = model_name[1] if len(model_name) > 1 else model.capitalize()

        return {
            "id": f"{user.pk}-{section}-{model}-{name}",
            "section": section,
            "model": model,
            "displayName": name,
            "add": self.__get_permission(user, "add", model),
            "view": self.__get_permission(user, "view", model),
            "change": self.__get_permission(user, "change", model),
            "delete": self.__get_permission(user, "delete", model),
            "export_pdf": self.__get_permission(user, "export_pdf", model),
            "export_excel": self.__get_permission(user, "export_excel", model),
        }

    def __get_permission(self, user: CustomUser, action, model):
        permission = f"{action}_{model}"
        if Permission.objects.filter(codename=permission).exists():
            return 1 if user.has_perm(f"content.{permission}") else 0
        else:
            return -1
