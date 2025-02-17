from ..imports import *
import os

# import magic
from django.http import HttpResponse


class TestApiView(APIView, AgencyManagement):
    def get(self, request: APIViewRequest):
        media_folder = settings.MEDIA_URL
        file_name = request.query_params.get("file")
        # return Response(f".{media_folder}{file_name}")
        file_path = f".{media_folder}{file_name}"
        file = None
        try:
            with open(file_path, "rb") as f:
                file = f.read()
            if os.path.isfile(file_path):
                os.remove(file_path)
            return HttpResponse(file, content_type="image/jpg")
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        client = Client.objects.get(id_insured=1)
        return Response(client.pk)
