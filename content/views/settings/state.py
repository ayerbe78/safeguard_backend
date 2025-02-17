from ..imports import *


class StateViewSet(viewsets.ModelViewSet, Common):
    permission_classes = [HasStatePermission]
    serializer_class = StateSerializer
    queryset = State.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.get_queryset()
        entries = self.__apply_search(entries, request)
        entries = self.apply_order_queryset(entries, request, "names")

        page = self.paginate_queryset(entries)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __apply_search(self, queryset, request: HttpRequest):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(names__icontains=search) | Q(sigla__icontains=search)
            )
        return queryset
