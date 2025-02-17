from ..imports import *


class GetCountyFips(APIView, AgencyManagement):
    permission_classes = [
        permissions.IsAuthenticated]

    def get(self, request: HttpRequest):
        zip = request.GET.get('zip')
        county_fips = USZips.objects.filter(zip=zip)
        if len(county_fips) == 1:
            serializer = USZipsSerializer(county_fips.get())
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            raise ValidationException(
                "The ZipCode doesn't match any location"
            )
