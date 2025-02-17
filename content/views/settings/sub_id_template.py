from ..imports import *


class ExpandedSubscriberIdTemplateSerializer(SubscriberIdTemplateSerializer):
    insured_name = serializers.CharField()

    class Meta:
        fields = ("id", "example", "id_insured", "insured_name")
        model = SubscriberIdTemplate


class SubscriberIdTemplateViewSet(viewsets.ModelViewSet, AgencyManagement):
    permission_classes = [HasSubscriberIdTemplatePermission]
    serializer_class = SubscriberIdTemplateSerializer
    queryset = SubscriberIdTemplate.objects.all()

    def list(self, request, *args, **kwargs):
        entries = self.__get_entries()

        page = self.paginate_queryset(entries)
        serializer = ExpandedSubscriberIdTemplateSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def __get_entries(self):
        entries = self.get_queryset()
        for entry in entries:
            insured = Insured.objects.filter(id=entry.id_insured)
            if len(insured):
                insured = insured.get()
                entry.insured_name = insured.names
        return entries

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_subidtemplate(self, request: HttpRequest):
        selects = self.get_selects(request.user.pk, "insurances")
        return Response(selects)

    @action(methods=["get"], detail=False, url_path="get_template_by_insured")
    def get_template_by_insured(self, request: HttpRequest):
        insured = request.GET.get('insured')
        template = SubscriberIdTemplate.objects.filter(id_insured=insured)
        if len(template) == 1:
            template = template.get()
            return Response(self.serializer_class(template).data)
        return Response(status=status.HTTP_204_NO_CONTENT)
