from rest_framework import serializers
from .sms_models import *


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SMSConversation


class SMSMediaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SMSMedia


class SMSSerializer(serializers.ModelSerializer):
    media = SMSMediaSerializer(many=True)

    class Meta:
        fields = "__all__"
        model = SMS


class ContactUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    phone = serializers.CharField()
    company = serializers.BooleanField()
    contact_id = serializers.CharField()

    class Meta:
        fields = ("name", "email", "phone", "company", "groups", "contact_id")
        model = CustomUser


class SMSConversationListSerializer(serializers.ModelSerializer):
    peer_name = serializers.CharField()
    peer_email = serializers.CharField()
    last_message_text = serializers.CharField()
    last_message_date = serializers.DateTimeField()
    last_message_received = serializers.BooleanField()
    last_message_sended = serializers.BooleanField()

    class Meta:
        fields = (
            "id",
            "peer_name",
            "peer_email",
            "peer_number",
            "unread_count",
            "last_message_text",
            "last_message_date",
            "last_message_received",
            "last_message_sended",
        )
        model = SMSConversation
