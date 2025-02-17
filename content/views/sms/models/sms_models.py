from django.db import models
from content.views.imports import *
from django.utils import timezone


class SMSConversation(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="conversations"
    )
    peer = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    peer_number = models.CharField(max_length=20)
    unread_count = models.IntegerField(default=0)
    # updated = models.DateTimeField(default=datetime.datetime.now)
    last_message = models.ForeignKey(
        "SMS", null=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        managed = True
        db_table = "sms_conversation"


class SMS(models.Model):
    sid = models.TextField(blank=True, null=True)
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    from_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, related_name="+", null=True
    )
    to_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, related_name="+", null=True
    )
    received = models.BooleanField(default=False)
    received_date = models.DateTimeField(null=True)
    sended = models.BooleanField(null=True, default=False)
    sended_date = models.DateTimeField(null=True)
    readed = models.BooleanField(default=True)
    body = models.TextField(blank=True)
    created = models.DateTimeField(default=timezone.now)
    conversation = models.ForeignKey(
        SMSConversation, on_delete=models.CASCADE, related_name="sms"
    )

    class Meta:
        managed = True
        db_table = "sms_object"


class SMSMedia(models.Model):
    url = models.TextField(blank=True, null=True)
    content_type = models.TextField(blank=True, null=True)
    sms = models.ForeignKey(SMS, on_delete=models.CASCADE, related_name="media")

    class Meta:
        managed = True
        db_table = "sms_media"
