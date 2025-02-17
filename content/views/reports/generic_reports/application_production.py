from ...imports import *


class ApplicationProduction(
    APIView, AgencyManagement, DirectSql, LimitOffsetPagination
):
    permission_classes = [HasGenericReportsPermission]

    def _get_results(self, request: HttpRequest) -> str:
        assistant = self.check_none(request.GET.get("assistant"), 0)
        date_start = self.check_none(request.GET.get("date_start"), None)
        date_end = self.check_none(request.GET.get("date_end"), None)

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

        if assistant:
            selected_user_id = self.get_user_by_user_type_id(
                'assistant', assistant)
            worked_apps = worked_apps.filter(user=selected_user_id)

            received_apps = received_apps.filter(Q(
                client__id__in=self.get_related_applications(selected_user_id, only=['id'])) | Q(client__id__in=self.get_related_clients(selected_user_id, only=['id'])))

        received_apps_mean = received_apps.count(
        )/days_difference if received_apps.count() != 0 and days_difference != 0 else 0
        worked_apps_mean = worked_apps.count(
        )/days_difference if worked_apps.count() != 0 and days_difference != 0 else 0

        return {
            "received_apps": received_apps.count(),
            "worked_apps": worked_apps.count(),
            "received_apps_mean": received_apps_mean,
            "worked_apps_mean": worked_apps_mean,
        }


class ApplicationProductionExportExcel(
    XLSXFileMixin, ReadOnlyModelViewSet, ApplicationProduction
):
    permission_classes = [HasExportExcelGenericReportsPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = ApplicationProductionExcelSerializer
    xlsx_use_labels = True
    filename = "app_production.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request):
        results = self._get_results(request)

        serializer = self.get_serializer(results)

        return Response(serializer.data)


class ApplicationProductionExportPdf(ApplicationProduction, PDFCommons):
    permission_classes = [HasExportPDFGenericReportsPermission]

    def get(self, request):
        results = self._get_results(request)
        data = [
            [
                results.get('received_apps'),
                results.get('worked_apps'),
                results.get('received_apps_mean'),
                results.get('worked_apps_mean'),
            ]
        ]

        headers = [
            "Received",
            "Worked",
            "Received Mean",
            "Worked Mean"
        ]
        return self.pdf_create_table(headers, data, A4, 'Application Production')
