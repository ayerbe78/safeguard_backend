from django.conf import settings
from twilio.rest import Client
import requests
from requests.auth import HTTPBasicAuth
from asgiref.sync import async_to_sync, sync_to_async
import logging

logger = logging.getLogger("django")


class SMSService:
    def __init__(self) -> None:
        self.__account_sid = settings.SMS_ACCOUNT
        self.__auth_token = settings.SMS_TOKEN
        self.__service_id = settings.SMS_SERVICE_ID
        self.client = Client(self.__account_sid, self.__auth_token)

    def send_sms(self, from_: str, to: str, sms: str, medias: list = []):
        try:
            if not len(medias):
                message = self.client.messages.create(
                    body=sms, from_=from_, to=to
                )
            else:
                message = self.client.messages.create(
                    body=sms, from_=from_, to=to, media_url=medias, status_callback=settings.SMS_RECEIVE_UPDATE_URL
                )
            return message
        except Exception as e:
            logger.error(e)
            return None

    def send_custom_sms(self, from_: str, to: str, sms: str):
        try:
            message = self.client.messages.create(
                body=sms, from_=from_, to=to
            )

            return message
        except Exception as e:
            logger.error(e)
            return None

    def list_sms(self, to: str, from_: str = None, limit=100):
        if from_:
            sms = self.client.messages.list(limit=limit, to=to, from_=from_)
        else:
            sms = self.client.messages.list(limit=limit, to=to)
        return sms

    def get_sms(self, uid: str):
        sms = self.client.messages.get(uid)
        return sms.fetch()

    def get_media_list(self, uid: str):
        media_list = self.client.messages(uid).media.list()
        return media_list

    def service_sms(self, sms: str, to: str, media=None):
        try:
            if media:
                message = self.client.messages.create(
                    body=sms, from_=self.__service_id, to=to, media_url=media
                )
            else:
                message = self.client.messages.create(
                    body=sms, from_=self.__service_id, to=to
                )
            return True
        except Exception as e:
            logger.error(e)
            return False

    def get_media(self, media) -> bytes:
        base_url = "https://api.twilio.com"
        uri = media.uri.split(".")[0]
        try:
            response = requests.get(
                base_url + uri,
                auth=HTTPBasicAuth(self.__account_sid, self.__auth_token),
                headers={"Connection": "keep-alive"},
            )
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None

    def get_media(self, url) -> bytes:
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.__account_sid, self.__auth_token),
                headers={"Connection": "keep-alive"},
            )
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None
