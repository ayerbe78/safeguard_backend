from ..imports import *


class ExpandedCommAgencySerializer(CommAgencySerializer):
    agency_name = serializers.CharField()
    insured_name = serializers.CharField()

    class Meta:
        fields = (
            "id",
            "comm",
            "yearcom",
            "id_agency",
            "id_insured",
            "agency_name",
            "insured_name",
        )
        model = CommAgency


class CommAgencyViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasCommAgencyPermission]
    serializer_class = CommAgencySerializer
    queryset = CommAgency.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.__get_entries()
        entries = self.__apply_filters(entries, request)
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "agency_name")

        page = self.paginate_queryset(entries)
        serializer = ExpandedCommAgencySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __get_entries(self):
        entries = (
            self.get_queryset()
            .prefetch_related("id_agency", "id_insured")
            .annotate(
                agency_name=F("id_agency__agency_name"),
                insured_name=F("id_insured__names"),
            )
        )
        return entries

    def __apply_filters(self, queryset, request: HttpRequest):
        user = request.user
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            queryset = queryset.filter(id_insured=request.GET.get("insured"))

        agencies = self.get_related_agencies(user.pk, True)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            agencies = agencies.filter(pk=agency.pk)
        queryset = queryset.filter(id_agency__in=self.queryset_to_list(agencies))

        year = self.check_none(request.GET.get("year"))
        if year:
            a = date(int(year), 1, 1)
            b = date(int(year), 12, 31)
            queryset = queryset.filter(yearcom__range=[a, b])

        return queryset

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(agency_name__icontains=search) | Q(insured_name__icontains=search)
            )
        return queryset


class CommAgencyOld(APIView, LimitOffsetPagination, AgencyManagement):
    permission_classes = [HasCommAgencyPermission]
    serializer_class = CommAgencySerializer

    def get(self, request):
        user = request.user
        comm_agency = CommAgency.objects.all()
        if request.GET.get("insured") != "0":
            comm_agency = comm_agency.filter(id_insured=request.GET.get("insured"))
        agencies = self.get_related_agencies(user.pk, True)
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            agencies = agencies.filter(pk=agency.pk)
        comm_agency = comm_agency.filter(id_agency__in=self.queryset_to_list(agencies))
        if request.GET.get("year") != "0":
            a = date(int(request.GET.get("year")), 1, 1)
            b = date(int(request.GET.get("year")), 12, 31)
            comm_agency = comm_agency.filter(yearcom__range=[a, b])

        results = self.paginate_queryset(
            comm_agency.order_by("yearcom"), request, view=self
        )
        serializer = self.serializer_class(results, many=True)
        return self.get_paginated_response(serializer.data)
