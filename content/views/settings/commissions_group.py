from ..imports import *
from ._commons import CommissionCommons

# class
class CommissionsGroupViewSet(viewsets.ModelViewSet, CommissionCommons, Common):
    serializer_class = CommissionsGroupSerializer
    permission_classes = [HasCommissionGroupPermission]

    def get_queryset(self):
        return CommissionsGroup.objects.prefetch_related("commissions")

    def create(self, request: APIViewRequest, *args, **kwargs):
        with transaction.atomic():
            new_group = CommissionsGroup(
                **super().create(request, *args, **kwargs).data
            )
            commissions = self.check_none(request.data.get("commissions"), [])
            self.__add_commission(commissions, new_group.pk)
            group_with_comms = self.get_queryset().get(pk=new_group.pk)
            return Response(CommissionsGroupSerializerExtended(group_with_comms).data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.apply_order_queryset(queryset, request, "names")
        queryset = self.__apply_search(queryset, request)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="detailed")
    def detailed(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommissionsGroupSerializerExtended(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CommissionsGroupSerializerExtended(instance)
        return Response(serializer.data)

    def __add_commission(self, commissions, group_id):
        for c in commissions:
            c["group"] = group_id
            new_comm = GroupCommissionSerializer(data=c)
            new_comm.is_valid(raise_exception=True)
            if not self.check_existing_in_groups(
                c["group"], c["state"], c["insured"], c["yearcom"]
            ):
                new_comm.save()

    def __apply_search(self, queryset, request):
        search = self.check_none(request.query_params.get("search"))
        if search:
            queryset = queryset.filter(names__icontains=search)

        return queryset
