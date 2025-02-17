from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from customauth.models import CustomUser
from django.contrib.auth import authenticate
from content.models import Agent, Assistant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "is_admin",
            "is_agent",
            "is_assistant",
            "is_subassistant",
            "first_name",
            "last_name",
            "mail_account",
            "personal_phone_number",
            "company_phone_number",
        )


class ListUserSerializer(serializers.ModelSerializer):
    groups_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "is_admin",
            "is_agent",
            "is_assistant",
            "is_subassistant",
            "first_name",
            "last_name",
            "groups_name",
            "groups",
            "company_phone_number",
        )
        depth = 1


class NewListUserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)
    full_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "is_admin",
            "is_agent",
            "is_assistant",
            "is_subassistant",
            "first_name",
            "last_name",
            "full_name",
            "groups",
            "company_phone_number",
        )
        depth = 1


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "password",
            "is_admin",
            "is_agent",
            "is_assistant",
            "is_subassistant",
            "username",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            validated_data["email"],
            validated_data["username"],
            validated_data["password"],
        )
        # if validated_data['is_agent']:
        #     user.is_agent=True
        # if validated_data['is_assistant']:
        #     user.is_assistant=True
        # if validated_data['is_subassistant']:
        #     user.is_subassistant=True
        # if validated_data['is_admin']:
        #     user.is_admin=True
        # user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ("old_password", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."}
            )

        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data["password"])
        instance.save()

        return instance


class AdminChangeAgentPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    id = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ("id", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."}
            )

        return attrs

    def update(self, instance, validated_data):
        agent = Agent.objects.get(id=validated_data["id"])
        user = CustomUser.objects.get(email=agent.email)
        user.set_password(validated_data["password"])
        user.save()

        return user


class AdminChangeAssistantPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    id = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ("id", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."}
            )

        return attrs

    def update(self, instance, validated_data):
        assistant = Assistant.objects.get(id=validated_data["id"])
        user = CustomUser.objects.get(email=assistant.email)
        user.set_password(validated_data["password"])
        user.save()

        return user


class AdminChangeUserPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    id = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ("id", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."}
            )

        return attrs

    def update(self, instance, validated_data):
        user = CustomUser.objects.get(id=validated_data["id"])
        user.set_password(validated_data["password"])
        user.save()

        return user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
        depth = 1
