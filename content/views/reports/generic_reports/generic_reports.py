from ...imports import *


class GenericReports(APIView, LimitOffsetPagination):
    permission_classes = [HasGenericReportsPermission]

    def __get_excel_url(self, request):
        insured = request.GET.get('insured', None)
        month = request.GET.get('month', None)
        year = request.GET.get('year', None)
        if insured and month and year:
            excel_obj = PaymentExcel.objects.filter(
                insured=insured, year=year).filter(Q(month=month) | Q(month="0"+month)).first()
            if excel_obj:
                return {"name": excel_obj.file.name, "url": excel_obj.file.url}
        return ""

    def get(self, request):
        generic_reports = [
            {
                "id": 1,
                "name": "Agents By Agency",
                "description": "All Agents that belong to an Agency",
                "excel_url": "/api/generic_report/export_excel_agents_by_agency",
                "pdf_url": "/api/generic_report/export_pdf_agents_by_agency",
                "filters": "Agency"
            },
            {
                "id": 2,
                "name": "Download Payment Excel",
                "description": "Download the Original Payment Excel sended by the Insurance",
                "excel_url": self.__get_excel_url(request),
                "pdf_url": "",
                "filters": "Insurance, Month, Year"
            },
            {
                "id": 3,
                "name": "Production",
                "description": "Produced policies by the selected group by",
                "excel_url": "/api/generic_report/export_excel_production",
                "pdf_url": "/api/generic_report/export_pdf_production",
                "filters": "Group By, Year, Insurance, Agency, State, Agent, Assistant"
            },
            {
                "id": 4,
                "name": "Unprocesed Policies",
                "description": "Policies entered in the excel of payments that were not paid to agents",
                "excel_url": "/api/generic_report/export_excel_unprocesed_policies",
                "pdf_url": "/api/generic_report/export_pdf_unprocesed_policies",
                "filters": "Month, Year, Insurance"
            },
            {
                "id": 5,
                "name": "Agents By Commission Groups",
                "description": "Agents that belong to the selected Commission Group",
                "excel_url": "/api/generic_report/export_excel_agents_by_commission_group",
                "pdf_url": "/api/generic_report/export_pdf_agents_by_commission_group",
                "filters": "Commission Group"
            },
            {
                "id": 6,
                "name": "Application Production",
                "description": "Applications received and worked by assistants in the selected period",
                "excel_url": "/api/generic_report/export_excel_application_production",
                "pdf_url": "/api/generic_report/export_pdf_application_production",
                "filters": "Assistant, Date Start*, Date End*"
            },
            {
                "id": 7,
                "name": "Agency Production",
                "description": "Produced policies by agencies, for each Insurance",
                "excel_url": "/api/generic_report/export_excel_agency_production",
                "pdf_url": "",
                "filters": "Year, Agency, State"
            },
            {
                "id": 8,
                "name": "Agent Production",
                "description": "Produced policies by agents, for each Insurance",
                "excel_url": "/api/generic_report/export_excel_agent_production",
                "pdf_url": "",
                "filters": "Year, Agency, State"
            },
            {
                "id": 9,
                "name": "Agents By Assistant",
                "description": "All Agents that belong to the selected Assistant",
                "excel_url": "/api/generic_report/export_excel_agents_by_assistant",
                "pdf_url": "/api/generic_report/export_pdf_agents_by_assistant",
                "filters": "Assistant*, Date Start, Date End"
            },
            {
                "id": 10,
                "name": "Unassigned Payments",
                "description": "All Unassigned rows of the excel when the payment was imported",
                "excel_url": "/api/generic_report/export_excel_unassigned_payments",
                "pdf_url": "/api/generic_report/export_pdf_UnAssignedPaymentsView",
                "filters": "Month*, Year*, Insurance*"
            },
        ]
        return Response({"results": generic_reports, "count": len(generic_reports)})


class DataForGenericReports(APIView, AgencyManagement):
    permission_classes = [
        HasGenericReportsPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "insurances", "agents", "assistants", "agencies", "states", "commission_groups"))
