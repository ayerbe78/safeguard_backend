from ..imports import *


class ExpandedSecondaryOverrideSerializer(SecondaryOverrideSerializer):
    parent_agency_name = serializers.CharField()
    insured_name = serializers.CharField()
    children_agency_name = serializers.CharField()

    class Meta:
        fields = ("id", "id_insured", "insured_name", "id_parent_agency", "parent_agency_name",
                  "id_children_agency", "children_agency_name", "amount_per_member")
        model = SecondaryOverride


class SecondaryOverrideViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasSecondaryOverridePermission]
    serializer_class = SecondaryOverrideSerializer
    queryset = SecondaryOverride.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.__get_entries()
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(
            entries, request, "parent_agency_name")

        page = self.paginate_queryset(entries)
        serializer = ExpandedSecondaryOverrideSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __get_entries(self):
        return (
            self.get_queryset()
            .prefetch_related("id_insured")
            .annotate(insured_name=F("id_insured__names"))
            .prefetch_related("id_parent_agency")
            .annotate(parent_agency_name=F("id_parent_agency__agency_name"))
            .prefetch_related("id_children_agency")
            .annotate(children_agency_name=F("id_children_agency__agency_name"))
        )

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(parent_agency_name__icontains=search) | Q(
                    children_agency_name__icontains=search) | Q(insured_name__icontains=search)
            )
        return queryset

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_client(self, request: HttpRequest):
        selects = self.get_selects(request.user.pk, "insurances", "agencies")
        return Response(selects)
