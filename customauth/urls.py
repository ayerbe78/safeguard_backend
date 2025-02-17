from django.urls import path, include
from .views import *
from knox import views as knox_views


urlpatterns = [
    # Auth views
    path("register", RegisterAPI.as_view()),
    path("login", LoginAPI.as_view()),
    path("user", UserAPI.as_view()),
    path("user_update/<int:pk>/", UserUpdateAPI.as_view()),
    path("edit_group/<int:pk>/", EditGroup.as_view()),
    path("user_initial_update", UserInitialUpdate.as_view()),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "admin_change_agent_password",
        AdminChangeAgentPasswordView.as_view(),
        name="admin_change_agent_password",
    ),
    path(
        "admin_change_assistant_password",
        AdminChangeAssistantPasswordView.as_view(),
        name="admin_change_assistant_password",
    ),
    path(
        "admin_change_user_password",
        AdminChangeUserPasswordView.as_view(),
        name="admin_change_user_password",
    ),
    path("logout", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("create_group/", AddNewGroup.as_view(), name="create_group"),
    path("delete_group/", DeleteGroup.as_view(), name="delete_group"),
    path("get_groups", GetGroups.as_view(), name="get_groups"),
    path("get_users", GetUsers.as_view(), name="get_users"),
    path("get_users_selects", GetUsersSelects.as_view(), name="get_users_selects"),
    path(
        "get_user_login_permissions",
        GetUserLoginPermissions.as_view(),
        name="get_user_login_permissions",
    ),
    path(
        "add_permission_to_group/",
        AddPermissionToGroup.as_view(),
        name="add_permission_to_group",
    ),
    path(
        "add_permission_to_user/",
        AddPermissionToUser.as_view(),
        name="add_permission_to_user",
    ),
    path("add_user_to_group/", AddUserToGroup.as_view(), name="add_user_to_group"),
    path(
        "remove_user_from_group/",
        RemoveUserFromGroup.as_view(),
        name="remove_user_from_group",
    ),
    path(
        "remove_permission_from_group/",
        RemovePermissionFromGroup.as_view(),
        name="remove_permission_from_group",
    ),
    path(
        "edit_user_permissions/",
        NewEditUserPermissions.as_view(),
        name="edit_user_permissions",
    ),
    path(
        "edit_group_permissions/",
        EditGroupPermissions.as_view(),
        name="edit_group_permissions",
    ),
    path(
        "new_edit_user_permissions/",
        NewEditUserPermissions.as_view(),
        name="new_edit_user_permissions",
    ),
    path(
        "new_edit_group_permissions/",
        NewEditGroupPermissions.as_view(),
        name="new_edit_group_permissions",
    ),
    path(
        "remove_permission_from_user/",
        RemovePermissionFromUser.as_view(),
        name="remove_permission_from_user",
    ),
    path(
        "get_group_permissions",
        GETGroupPermissions.as_view(),
        name="get_group_permissions",
    ),
    path(
        "get_user_permissions",
        GETUserPermissions.as_view(),
        name="get_user_permissions",
    ),
    path(
        "password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
]
