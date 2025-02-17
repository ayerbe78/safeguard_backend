from ..imports import *
from ._commons import CommissionCommons


class GroupCommissionViewSet(
    viewsets.ModelViewSet, CommissionCommons, AgencyManagement
):
    serializer_class = GroupCommissionSerializer
    permission_classes = [HasGroupCommissionPermission]

    def get_queryset(self):
        return GroupCommission.objects.all()

    def create(self, request, *args, **kwargs):
        if not self.check_existing_in_groups_request(request):
            return super().create(request, *args, **kwargs)
        else:
            return Response(
                data="Already exists element with similar attributes",
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        commissions = self.__apply_filters(request)
        commissions = self.__apply_search(commissions, request)
        commissions = self.apply_order_queryset(commissions, request, "group_name")

        page = self.paginate_queryset(commissions.values())
        if page is not None:
            return self.get_paginated_response(page)

        return Response(commissions.values())

    @action(methods=["post"], detail=False, url_path="batch")
    def batch_create(self, request: APIViewRequest):
        commissions = self.check_none(request.data.get("commissions"))
        defaults = self.__get_defaults_from_batch_create(request)

        count = 0
        if commissions:
            with transaction.atomic():
                for c in commissions:
                    c.update(defaults)
                    if not self.check_existing_in_groups(
                        group=c["group"],
                        state=c["state"],
                        insured=c["insured"],
                        yearcom=c["yearcom"],
                    ):
                        serializer = self.get_serializer(data=c)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        count += 1
                    else:
                        actual = self.__get_actual_from_data(c)
                        if actual:
                            serializer = self.get_serializer(actual, data=c)
                            if serializer.is_valid(raise_exception=True):
                                serializer.save()
                                count += 1
        return Response({"count": count})

    @action(methods=["get"], detail=False, url_path="data")
    def data_for(self, request):
        data = {}
        data["groups"] = CommissionsGroup.objects.all().values("id", "names")
        commons = self.get_selects(request.user.pk, "states", "insurances")
        data.update(commons)
        return Response(data)

    def __apply_filters(self, request):
        yearcom = self.check_none(request.query_params.get("year"), date.today().year)
        commissions = (
            GroupCommission.objects.prefetch_related(
                "group",
                "insured",
                "state",
            )
            .annotate(
                insured_name=F("insured__names"),
                state_name=F("state__names"),
                group_name=F("group__names"),
            )
            .filter(yearcom=yearcom)
        )

        group = self.check_none(request.query_params.get("group"))
        if group:
            commissions = commissions.filter(group=group)

        yearcom = self.check_none(request.query_params.get("year"))
        if yearcom:
            commissions = commissions.filter(yearcom=yearcom)
        insured = self.check_none(request.query_params.get("insured"))
        if insured:
            commissions = commissions.filter(insured=insured)
        state = self.check_none(request.query_params.get("state"))
        if state:
            commissions = commissions.filter(state=state)

        return commissions

    def __apply_search(self, queryset, request):
        search = self.check_none(request.query_params.get("search"))
        if search:
            queryset = queryset.filter(
                Q(insured_name__icontains=search)
                | Q(state_name__icontains=search)
                | Q(group_name__icontains=search)
            )
        return queryset

    def __get_actual_from_data(self, data):
        actual = None
        try:
            actual = self.get_queryset().get(
                group=data["group"],
                insured=data["insured"],
                state=data["state"],
                yearcom=data["yearcom"],
            )
        except:
            pass
        return actual

    def __get_defaults_from_batch_create(self, request: APIViewRequest) -> dict:
        defaults = {}
        group = self.check_none(request.data.get("group"))
        comm_new = self.check_none(request.data.get("comm_new"))
        comm_rew = self.check_none(request.data.get("comm_rew"))
        comm_set = self.check_none(request.data.get("comm_set"))
        comm_set2 = self.check_none(request.data.get("comm_set2"))
        yearcom = self.check_none(request.data.get("yearcom"))
        if group:
            defaults["group"] = group
        if comm_new:
            defaults["comm_new"] = comm_new
        if comm_rew:
            defaults["comm_rew"] = comm_rew
        if comm_set:
            defaults["comm_set"] = comm_set
        if comm_set2:
            defaults["comm_set2"] = comm_set2
        if yearcom:
            defaults["yearcom"] = yearcom

        return defaults
