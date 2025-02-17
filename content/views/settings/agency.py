from ..imports import *


class AgencyViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasAgencyPermission]
    serializer_class = AgencySerializer
    queryset = Agency.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.__get_entries(request)
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "agency_name")
        serializer = self.get_serializer_class()

        page = self.paginate_queryset(entries)
        serializer = serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_agency(self, request: HttpRequest):
        user: CustomUser = request.user
        users = (
            CustomUser.objects.values("id")
            .annotate(
                user_name=Concat("first_name", V(" "), "last_name"),
                user_email=F("email"),
            )
            .order_by("user_name")
        )
        selects = self.get_selects(user.pk, "agencies")
        selects.update(dict(users=users))
        return Response(selects)

    def __get_entries(self, request):
        entries = self.get_related_agencies(request.user.pk, True)
        return entries

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(agency_name__icontains=search)
                | Q(agency_email__icontains=search)
                | Q(agency_account__icontains=search)
                | Q(agency_person__icontains=search)
                | Q(agency_number__icontains=search)
                | Q(agency_phone__icontains=search)
            )
        return queryset


class DataForCommissionAgecy(APIView, AgencyManagement):
    permission_classes = [HasAgencyPermission]
    serializer_class = AssitStateSerializer

    def get(self, request):
        user = request.user
        agency = (
            self.get_related_agencies(user.pk, True)
            .values("id", "agency_name")
            .order_by("agency_name")
        )
        insurances = (
            Insured.objects.all()
            .order_by("names")
            .values("id", "names")
            .order_by("names")
        )
        insurance_serializer = InsuredOnlyNameSerializer(insurances, many=True)
        agency_serializer = AgencyOnlyNameSerializer(agency, many=True)
        return Response(
            {
                "insurances": insurance_serializer.data,
                "agency": agency_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
