from ..imports import *


class ExpandedCountySerializer(CountySerializer):
    city_name = serializers.CharField()

    class Meta:
        fields = ("id", "names", "id_city", "city_name")
        model = County


class CountyViewSet(viewsets.ModelViewSet, Common):
    permission_classes = [HasCountyPermission]
    serializer_class = CountySerializer
    queryset = County.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.__get_entries()
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "names")

        page = self.paginate_queryset(entries)
        serializer = ExpandedCountySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __get_entries(self):
        return (
            self.get_queryset()
            .prefetch_related("id_city")
            .annotate(city_name=F("id_city__names"))
        )

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(names__icontains=search) | Q(city_name__icontains=search)
            )
        return queryset

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_client(self, request: HttpRequest):
        selects = City.objects.values("id", "names")
        return Response({"states": selects})
