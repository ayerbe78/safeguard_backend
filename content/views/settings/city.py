from ..imports import *


class ExpandedCitySerializer(CitySerializer):
    state_name = serializers.CharField()

    class Meta:
        fields = ("id", "names", "id_state", "state_name")
        model = City


class CityViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasCityPermission]
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.__get_entries()
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "names")

        page = self.paginate_queryset(entries)
        serializer = ExpandedCitySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __get_entries(self):
        return (
            self.get_queryset()
            .prefetch_related("id_state")
            .annotate(state_name=F("id_state__names"))
        )

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(names__icontains=search) | Q(state_name__icontains=search)
            )
        return queryset

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_client(self, request: HttpRequest):
        selects = self.get_selects(request.user.pk, "states")
        return Response(selects)
