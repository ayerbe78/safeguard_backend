from ..imports import *

from django.db.models import F, Value
from django.db.models.functions import Concat, Trim


class AssistantProductionReport(APIView, LimitOffsetPagination, AgencyManagement, DirectSql):
    permission_classes = [HasAssistantProductionReportPermission]

    def get(self, request: APIViewRequest):
        entries = self.get_entries(request)
        page = self.paginate_queryset(entries, request, view=self)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(entries)

    def get_entries(self, request: HttpRequest) -> str:
        assistant = self.check_none(request.GET.get("assistant"), 0)
        date_start = self.check_none(request.GET.get("date_start"), None)
        date_end = self.check_none(request.GET.get("date_end"), None)
        search = self.check_none(request.GET.get("search"), None)

        if not date_start or not date_end:
            raise ValidationException('Missing filters')
        date_start = datetime.strptime(
            date_start, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = datetime.strptime(
            date_end, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=23, minute=59, second=59, microsecond=999999)

        # Calcular la diferencia en días
        days_difference = (date_end - date_start).days
        if days_difference == 0 and date_start.day == date_end.day:
            days_difference = 1

        received_apps = ClientLog.objects.filter(
            Q(description='Inserted as a new Application') | Q(
                description__contains='Application transfered from client'),
            added_on__range=[date_start, date_end]).exclude(client__borrado=1)
        worked_apps = ClientLog.objects.filter(
            description='Transfered from Application to Client', added_on__range=[date_start, date_end]).exclude(client__borrado=1)
        edited_apps = ClientLog.objects.filter(
            type='update', added_on__range=[date_start, date_end]).exclude(client__tipoclient=2).exclude(client__tipoclient=4).exclude(client__borrado=1)

        if assistant:
            assistants = Assistant.objects.filter(id=assistant)
        else:
            assistants = Assistant.objects.exclude(
                borrado=1).order_by("assistant_name")
        if search:
            assistants = assistants.annotate(
                full_name=Concat(Trim(F('assistant_name')), Value(
                    ' '), Trim(F('assistant_lastname')))
            ).filter(full_name__icontains=search)

        results = []
        for assistant_full in assistants:
            selected_user_id = self.get_user_by_user_type_id(
                'assistant', assistant_full.pk)
            local_worked_apps = worked_apps.filter(user=selected_user_id)
            related_apps = self.get_related_applications(
                selected_user_id, only=['id'])
            related_clients = self.get_related_clients(
                selected_user_id, only=['id'])
            local_received_apps = received_apps.filter(Q(
                client__id__in=related_apps) | Q(client__id__in=related_clients))

            local_edited_apps = edited_apps.filter(
                client__id__in=related_clients, user=selected_user_id)

            results.append(
                {
                    "assistant_name": assistant_full.assistant_name+" " + assistant_full.assistant_lastname,
                    "received_apps": local_received_apps.count(),
                    "worked_apps": local_worked_apps.count(),
                    "updated_apps": local_edited_apps.count(),
                }
            )

        return results


class DataForAssistantProductionReport(APIView, AgencyManagement):
    permission_classes = [HasAssistantProductionReportPermission]

    def get(self, request):
        user = request.user
        selects = self.get_selects(
            user.pk, "agents", "assistants", "insurances")
        return Response(selects)


class ExportExcelAssistantProductionReport(
    XLSXFileMixin, ReadOnlyModelViewSet, AssistantProductionReport
):
    permission_classes = [HasExportExcelAssistantProductionPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = AssistantProductionExcelSerializer
    xlsx_use_labels = True
    filename = "assistant_production.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        results = self.get_entries(request)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
