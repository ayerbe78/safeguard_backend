from django.db import models
from rest_framework import serializers
from content.views.imports import *
import datetime
import os
import mimetypes
from django.http import HttpResponse

logger = logging.getLogger("django")


class SmsTempFile(models.Model):
    file = models.FileField(max_length=4500)
    created = models.DateField(
        null=True, blank=True, default=datetime.date.today)

    class Meta:
        managed = False
        db_table = "temp_sms_file"


class SmsImageTempSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = SmsTempFile


class SmsTempFileView(APIView):
    permission_classes = [HasTwilioPermission]

    def get(self, request: HttpRequest):
        media_folder = settings.MEDIA_ROOT
        file_id = request.query_params.get("file")
        logger.info('getting media')
        logger.info(file_id)
        file_obj = None
        try:
            file_obj = SmsTempFile.objects.get(pk=file_id)
            logger.info('returned media successfuly')
        except Exception as e:
            logger.info(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        file_name = file_obj.file.name
        file_path = f"{media_folder}/{file_name}"
        file = None
        file_type = None
        try:
            with open(file_path, "rb") as f:
                file = f.read()
                file_type = mimetypes.guess_type(file_path)[0]
            # if os.path.isfile(file_path):
            #     os.remove(file_path)
            # file_obj.delete()
            return HttpResponse(file, content_type=file_type)
        except Exception as e:
            logger.info(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
