from content.views.views import *
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
# Settings
router.register("product", ProductViewSet, "product")
router.register("county", CountyViewSet, "county")
router.register("state", StateViewSet, "state")
router.register("language", LanguageViewSet, "language")
router.register("insured", InsuredViewSet, "insured")
router.register("health_plan", HealthPlanViewSet, "health_plan")
router.register("special_election", SpecialElectionViewSet, "special_election")
router.register("agency", AgencyViewSet, "agency")
router.register("soc_service_refe", SocServiceRefeViewSet, "soc_service_refe")
router.register("type", TypeViewSet, "type")
router.register("plan_name", PlanNameViewSet, "plan_name")
router.register("problem", ProblemViewSet, "problem")
router.register("secondary_override",
                SecondaryOverrideViewSet, "secondary_override")
router.register("client_medicaid", ClientMedicaidView, "client_medicaid")
router.register("city", CityViewSet, "city")
router.register("pre_letter_log", PreLetterLogViewSet, "pre_letter_log")
router.register("sub_id_template",
                SubscriberIdTemplateViewSet, "sub_id_template")
router.register("status", StatusViewSet, "status")
router.register("policy", PolizaViewSet, "policy")
router.register("groups", GroupsViewSet, "groups")
router.register("document_type", DocumentTypeViewSet, "document_type")
router.register("comm_agency", CommAgencyViewSet, "comm_agency")
router.register("event", EventViewSet, "event")
# router.register("comm_agent", CommAgentViewSet, "comm_agent")
router.register("comm_group", CommissionsGroupViewSet, "comm_group")
router.register("pdf_notice", PDFNoticeViewSet, "pdf_notice")
router.register("comm_agent", AgentCommissionViewSet, "comm_agent")
router.register("group_comm", GroupCommissionViewSet, "group_comm")
router.register("secondary_agent", SecondaryAgentViewSet, "secondary_agent")
router.register("client_consent_log",
                ClientConsentLogViewSet, "client_consent_log")
router.register("income_letter_log",
                IncomeLetterLogViewSet, "income_letter_log")

# MAIN
router.register("agent", AgentViewSet, "agent")
router.register("assistant", AssistantViewSet, "assistant")
router.register("subassistant", SubassistantViewSet, "subassistant")
router.register("agent_document", AgentDocumentViewSet, "agent_document")
router.register("agent_tax_document",
                AgentTaxDocsViewSet, "agent_tax_document")
router.register("application", ApplicationViewSet, "application")
router.register("client", ClientViewSet, "client")
router.register("medicare", MedicareViewSet, "medicare")
router.register("client_medicare", ClientMedicareViewSet, "client_medicare")
router.register("prospect_manager", ProspectManagerViewSet, "prospect_manager")
router.register("up_document", UpdocumentViewSet, "up_document")
router.register("bob_global", BobGlobalViewSet, "bob_global")


# Otros
router.register("send_sms", SendsmsViewSet, "send_sms")
router.register("type_pending", TypePendingdocViewSet, "type_pending")
router.register("assist_insurance", AssitInsuranceViewSet, "assist_insurance")
router.register("video", VideoViewSet, "video")
router.register("agent_insured", AgentInsuredViewSet, "agent_insured")
router.register("agent_language", AgentLanguageViewSet, "agent_language")
router.register("agent_product", AgentProductViewSet, "agent_product")
router.register("assist_state", AssitStateViewSet, "assist_state")
router.register("claim", ClaimViewSet, "claim")
router.register("client_document", ClientDocumentViewSet, "client_document")
router.register("client_parient", ClientParientViewSet, "client_parient")
router.register("history", HistoryViewSet, "history")
router.register("log", LogViewSet, "log")
router.register("medicare_social", MedicareSocialViewSet, "medicare_social")
router.register("menu", MenuViewSet, "menu")
router.register("payments", PaymentsViewSet, "payments")
router.register("payments_global", PaymentsGlobalViewSet, "payments_global")
router.register("payments_global", PaymentsGlobalViewSet, "payments_global")
router.register("payments_global_tmp",
                PaymentsGlobalTmpViewSet, "payments_global_tmp")
router.register("payments_agency", PaymentsagencyViewSet, "payments_agency")
router.register("agent_state", AgentStateViewSet, "agent_state")
router.register("payments_assistant",
                PaymentsasistentViewSet, "payments_assistant")
router.register("pending_documents",
                PendingDocumentsViewSet, "pending_documents")
router.register("permisos", PermisosViewSet, "permisos")
router.register("prost_manager", ProstManegerViewSet, "prost_manager")
router.register("registre_asis", RegistreAsisViewSet, "registre_asis")
router.register("registro", RegistroViewSet, "registro")
router.register("table5", Table5ViewSet, "table5")
router.register("agent_portal", AgentPortalViewSet, "agent_portal")
router.register("extra_fields", ExtraFieldsViewSet, "extra_fields")
router.register(
    "export_excel_payment_agent", ExportExcelPaymentAgent, "export_excel_payment_agent"
)
router.register(
    "export_excel_assistant_production", ExportExcelAssistantProductionReport, "export_excel_assistant_production"
)
router.register(
    "export_excel_released_agents", ExportExcelReleseadAgentsReport, "export_excel_released_agents"
)
router.register(
    "generic_report/export_excel_unassigned_payments", UnAssignedPaymentsViewExportExcel, "export_excel_unassigned_payments"
)
router.register(
    "export_excel_agency_repayments", ExportExcelAgencyRepaymentsReport, "export_excel_agency_repayments"
)
router.register(
    "export_excel_repayments_report", ExportExcelRepaymentsReport, "export_excel_repayments_report"
)
router.register(
    "generic_report/export_excel_unprocesed_policies", UnprocesedPoliciesExportExcel, "export_excel_unprocesed_policies"
)
router.register(
    "generic_report/export_excel_agents_by_assistant", AgentsByAssistantExportExcel, "export_excel_agents_by_assistant"
)
router.register(
    "generic_report/export_excel_application_production", ApplicationProductionExportExcel, "export_excel_application_production"
)
router.register(
    "generic_report/export_excel_agents_by_commission_group", AgentsByCommissionGroupExportExcel, "export_excel_agents_by_commission_group"
)
router.register(
    "export_excel_override", ExportExcelPaymentAgency, "export_excel_override"
)
router.register(
    "export_excel_client_by_companies", FilterClientCompanyExportExcel, "export_excel_client_by_companies"
)
router.register(
    "export_excel_payment_agency_agent", ExportExcelPaymentGlobalAgencyAgent, "export_excel_payment_agency_agent"
)
router.register(
    "export_excel_agent_payments_details_by_insurance", ExportExcelAgentPaymentsDetailsByInsurancet, "export_excel_agent_payments_details_by_insurance"
)
router.register(
    "export_excel_agency_agent_payments_details_by_insurance", ExportExcelAgencyAgentPaymentsDetailsByInsurance, "export_excel_agency_agent_payments_details_by_insurance"
)
router.register(
    "export_excel_payment_global_client", ExportExcelPaymentGlobalClient, "export_excel_payment_global_client"
)
router.register(
    "generic_report/export_excel_production", ProductionExportExcel, "export_excel_production"
)
router.register(
    "generic_report/export_excel_agency_production", AgencyProductionExportExcel, "export_excel_agency_production"
)
router.register(
    "generic_report/export_excel_agent_production", AgentProductionExportExcel, "export_excel_agent_production"
)
router.register(
    "export_excel_payment_global_agent_details", ExportExcelPaymentGlobalAgentSummaryDetails, "export_excel_payment_global_agent_details"
)
router.register(
    "export_excel_payment_global_agent", ExportExcelPaymentGlobalAgent, "export_excel_payment_global_agent"
)
router.register(
    "export_excel_agency_payment_details", ExportExcelPaymentGloablAgencyDetails, "export_excel_agency_payment_details"
)
router.register(
    "export_excel_assistant_payment_details", ExportExcelPaymentAssistantSummaryDetails, "export_excel_assistant_payment_details"
)
router.register(
    "export_excel_agent_payment_details", ExportExcelPaymentAgentSummaryDetails, "export_excel_agent_payment_details"
)
router.register(
    "export_excel_original_payment_discrepancies", ExportExcelPaymentDiscrepanciesOriginal, "export_excel_original_payment_discrepancies"
)
router.register(
    "export_excel_payment_differences", ExportExcelPaymentDifferences, "export_excel_payment_differences"
)
router.register(
    "export_excel_payment_client_original", ExportExcelPaymentClientOriginal, "export_excel_payment_client_original"
)
router.register(
    "export_excel_payment_global_original", ExportExcelPaymentGlobalOriginal, "export_excel_payment_global_original"
)
router.register(
    "export_excel_payment_client",
    ExportExcelPaymentGlobal,
    "export_excel_payment_client",
)
router.register(
    "generic_report/export_excel_agents_by_agency",
    AgentsByAgencyExportExcel,
    "export_excel_agents_by_agency",
)
router.register(
    "export_excel_payment_global",
    ExportExcelPaymentInsuredOnly,
    "export_excel_payment_global",
)
router.register("export_excel_agent",
                ExportExcelAgentList, "export_excel_agent")
router.register(
    "export_excel_payment_discrepancies",
    ExportExcelPaymentDiscrepancies,
    "export_excel_payment_discrepancies",
)
router.register(
    "export/client/excel",
    ExportExcelClient,
    "export_client_excel",
)
router.register(
    "payment_agency/global/excel",
    ExportExcelPaymentGloablAgency,
    "payment_agency_global_excel",
)
router.register(
    "payment_agency/excel",
    ExportExcelPaymentAgency,
    "payment_agency_excel",
)
router.register(
    "reports/payment/assistants/excel",
    ExportExcelPaymentGloabalAssistatnt,
    "payment_assistant_report_excel",
)
router.register(
    "reports/payment/assistants/client/excel",
    PaymentAssistantPerClientExportExcel,
    "payment_assistant_client_report_excel",
)

urlpatterns = [
    path(
        "get_counties_by_state",
        GetCountiesByState.as_view(),
        name="get_counties_by_state",
    ),
    path(
        "get_assistant_production",
        AssistantProductionReport.as_view(),
        name="get_assistant_production",
    ),
    path("get_state_by_county", GetByStateCounty.as_view(),
         name="get_state_by_county"),
    path("languages_by_agent", LanguagesByAgent.as_view(),
         name="languages_by_agent"),
    path("states_by_agent", StatesByAgent.as_view(),
         name="states_by_agent"),
    path("agent_portals_by_agent", AgentPortalsByAgent.as_view(),
         name="agent_portals_by_agent"),
    path(
        "insurances_by_agent", InsurancesByAgent.as_view(), name="insurances_by_agent"
    ),
    path(
        "assist_state_by_agent",
        AssistStateByAgent.as_view(),
        name="assist_state_by_agent",
    ),
    path(
        "assist_insured_by_agent",
        AssistInsuranceByAgent.as_view(),
        name="assist_insured_by_agent",
    ),
    path(
        "edit_language_agent/",
        EditLanguageInAgent.as_view(),
        name="edit_language_agent",
    ),
    path(
        "edit_agent_state/",
        EditAgentState.as_view(),
        name="edit_agent_state",
    ),
    path(
        "edit_insurance_agent/",
        EditInsuranceInAgent.as_view(),
        name="edit_insurance_agent",
    ),
    path(
        "edit_insurance_assist_agent/",
        EditInsuranceAssistInAgent.as_view(),
        name="edit_insurance_assist_agent",
    ),
    path(
        "edit_state_assist_agent/",
        EditStateAssistInAgent.as_view(),
        name="edit_state_assist_agent",
    ),
    path(
        "get_payment_chart_data/",
        Insurance_Payment_Balance.as_view(),
        name="get_payment_chart_data",
    ),
    path("get_all_agents/", GetAllAgents.as_view(), name="get_all_agents"),
    path(
        "data_for_table_dashboard/",
        DataForTableDashboard.as_view(),
        name="data_for_table_dashboard",
    ),
    path(
        "data_for_assistant_production/",
        DataForAssistantProductionReport.as_view(),
        name="data_for_assistant_production",
    ),
    path(
        "data_for_client_medicaid/",
        DataForClientMedicaid.as_view(),
        name="data_for_client_medicaid",
    ),
    path(
        "agents_by_asssistant", AgentsByAssistant.as_view(), name="agents_by_asssistant"
    ),
    # path("data_for_client", DataForClient.as_view(), name="data_for_client"),
    path(
        "data_for_application",
        DataForApplication.as_view(),
        name="data_for_application",
    ),
    path("data_for_agent", DataForAgent.as_view(), name="data_for_agent"),
    # path("data_for_bob_global", DataForBobGlobal.as_view(), name="data_for_bob_global"),
    # path("data_for_city", DataForCity.as_view(), name="data_for_city"),
    # path("data_for_county", DataForCounty.as_view(), name="data_for_county"),
    # path(
    #     "data_for_commision_agent",
    #     DataForCommissionAgent.as_view(),
    #     name="data_for_commision_agent",
    # ),
    path(
        "data_for_commision_agency",
        DataForCommissionAgecy.as_view(),
        name="data_for_commision_agency",
    ),
    path("data_for_import_csv", DataForImportCsv.as_view(),
         name="data_for_import_csv"),
    path(
        "data_for_payment_global_agent",
        DataForPaymentGlobalAgent.as_view(),
        name="data_for_payment_global_agent",
    ),
    path(
        "data_for_payment_global_client",
        DataForPaymentGlobalClient.as_view(),
        name="data_for_payment_global_client",
    ),
    path(
        "data_for_payment_insured_only",
        DataForPaymentInsuredOnly.as_view(),
        name="data_for_payment_insured_only",
    ),
    path(
        "data_for_client_by_companies",
        DataForClientByCompanies.as_view(),
        name="data_for_client_by_companies",
    ),
    path("data_for_import_bob", DataForImportBob.as_view(), name="data_for_claim"),
    # path(
    #     "search_filters_application",
    #     SearchFiltersApplication.as_view(),
    #     name="search_filters_application",
    # ),
    # path(
    #     "search_filters_bob_global",
    #     SearchFiltersBobGlobal.as_view(),
    #     name="search_filters_bob_global",
    # ),
    # path(
    #     "search_filters_comm_agency",
    #     SearchFiltersCommAgency.as_view(),
    #     name="search_filters_comm_agency",
    # ),
    # path(
    #     "search_filters_comm_agent",
    #     SearchFiltersCommAgent.as_view(),
    #     name="search_filters_comm_agent",
    # ),
    # path(
    #     "search_filters_payment_agent",
    #     SearchFiltersPaymentAgent.as_view(),
    #     name="search_filters_payment_agent",
    # ),
    # path(
    #     "search_filters_payment_client",
    #     SearchFiltersPaymentClients.as_view(),
    #     name="search_filters_payment_client",
    # ),
    path(
        "search_filters_payment_global",
        SearchFiltersPaymentGlobalOnly.as_view(),
        name="search_filters_payment_global",
    ),
    path("search_filters_claim", FilterClaims.as_view(),
         name="search_filters_claim"),
    path(
        "search_filters_clients_company",
        FilterClientCompany.as_view(),
        name="search_filters_clients_company",
    ),
    path("get_agent_docs", AgentDocs.as_view(), name="get_agent_docs"),
    path("get_agent_tax_docs", AgentTaxDocs.as_view(), name="get_agent_tax_docs"),
    path("bob_by_client", BobByClient.as_view(), name="bob_by_client"),
    path("reports/original_payment_discrepancies", PaymentDiscrepanciesOriginal.as_view(),
         name="original_payment_discrepancies"),
    path("get_client_notes", ClientNotes.as_view(), name="get_client_notes"),
    path(
        "export_pdf_agent_payment",
        ExportPdfPaymentAgent.as_view(),
        name="export_pdf_agent_payment",
    ),
    path(
        "generic_report/export_pdf_UnAssignedPaymentsView",
        UnAssignedPaymentsViewExportPdf.as_view(),
        name="export_pdf_UnAssignedPaymentsView",
    ),
    path(
        "generic_report/export_pdf_unprocesed_policies",
        UnprocesedPoliciesExportPdf.as_view(),
        name="export_pdf_unprocesed_policies",
    ),
    path(
        "generic_report/export_pdf_agents_by_commission_group",
        AgentsByCommissionGroupExportPdf.as_view(),
        name="export_pdf_agents_by_commission_group",
    ),
    path(
        "generic_report/export_pdf_production",
        ProductionExportPdf.as_view(),
        name="export_pdf_production",
    ),
    path(
        "export_pdf_client_by_companies",
        ClientsByCompaniesExportPdf.as_view(),
        name="export_pdf_client_by_companies",
    ),
    path(
        "export_pdf_agency_agent",
        ExportPdfPaymentGlobalAgencyAgent.as_view(),
        name="export_pdf_agency_agent",
    ),
    path(
        "export_pdf_agency_agent_by_insured",
        ExportPdfAgencyAgentPaymentsDetailsByInsurance.as_view(),
        name="export_pdf_agency_agent_by_insured",
    ),
    path(
        "export_pdf_payment_global_agent",
        ExportPdfPaymentGlobalAgent.as_view(),
        name="export_pdf_payment_global_agent",
    ),
    path(
        "export_pdf_payment_global_client",
        ExportPdfPaymentGlobalClient.as_view(),
        name="export_pdf_payment_global_client",
    ),
    path(
        "export_pdf_payment_differences",
        ExportPdfPaymentDifferences.as_view(),
        name="export_pdf_payment_differences",
    ),
    path(
        "export_pdf_payment_discrepancies",
        ExportPdfPaymentDiscrepancies.as_view(),
        name="export_pdf_payment_discrepancies",
    ),
    path(
        "export_pdf_payment_discrepancies_original",
        ExportPdfPaymentDiscrepanciesOriginal.as_view(),
        name="export_pdf_payment_discrepancies_original",
    ),
    path(
        "export_pdf_client_payment",
        ExportPdfPaymentGlobal.as_view(),
        name="export_pdf_client_payment",
    ),
    path(
        "export_pdf_bob_payment",
        ExportPdfPaymentInsuredOnly.as_view(),
        name="export_pdf_bob_payment",
    ),
    path(
        "generic_report/export_pdf_agents_by_agency",
        AgentsByAgencyExportPdf.as_view(),
        name="export_pdf_agents_by_agency",
    ),
    path(
        "generic_report/export_pdf_agents_by_assistant",
        AgentsByAssistantExportPdf.as_view(),
        name="export_pdf_agents_by_assistant",
    ),
    path(
        "generic_report/export_pdf_application_production",
        ApplicationProductionExportPdf.as_view(),
        name="export_pdf_application_production",
    ),
    path("import_agent_payment/", ImportAgentPayments.as_view(),
         name="import_agent_payment/"),
    path("import_overrides/", ImportOverride.as_view(),
         name="import_overrides/"),
    path("import_sms_excel/", ImportSMSExcel.as_view(),
         name="import_sms_excel/"),
    path("import_bob/", ImportBobCSV.as_view(), name="import_bob/"),
    path("delete_agent_payment/", DeleteAgentPaymentCSV.as_view(),
         name="delete_agent_payment/"),
    path("make_agent_repayment/", MakeAgentRePayment.as_view(),
         name="make_agent_repayment"),
    path("released_agents/", ReleseadAgentsReport.as_view(),
         name="released_agents"),
    path("imported_payments_detail", ImportedPaymentsDetail.as_view(),
         name="imported_payments_detail"),
    path(
        "detail_payment_in_payment_table",
        DetailPaymentInPaymentTable.as_view(),
        name="detail_payment_in_payment_table",
    ),
    path(
        "payment_override",
        OverrideViewSet.as_view(),
        name="payment_override",
    ),
    path(
        "transfer_preletter_to_client",
        TransferPreLetterToClient.as_view(),
        name="transfer_preletter_to_client",
    ),
    path(
        "transfer_preletter_to_application",
        TransferPreLetterToApplication.as_view(),
        name="transfer_preletter_to_application",
    ),
    path(
        "data_for_payment_override",
        DataForOverride.as_view(),
        name="data_for_payment_override",
    ),
    path(
        "data_for_released_agents",
        DataForReleseadAgentsReport.as_view(),
        name="data_for_released_agents",
    ),
    path(
        "new_detail_payment_in_payment_table",
        NewDetailPaymentInPaymentTable.as_view(),
        name="new_detail_payment_in_payment_table",
    ),
    path(
        "detail_payment_in_repayment_table",
        ReportPaymentAgentSummaryDetails.as_view(),
        name="detail_payment_in_repayment_table",
    ),
    path(
        "detail_payment_agent_in_repayment_table",
        ReportPaymentGlobalAgentSummaryDetails.as_view(),
        name="detail_payment_agent_in_repayment_table",
    ),
    path("claim_history", OldClaimHistory.as_view(), name="claim_history"),
    path(
        "payment_discrepancies",
        PaymentDiscrepancies.as_view(),
        name="payment_discrepancies",
    ),
    path(
        "reports/payment_differences",
        PaymentDifferences.as_view(),
        name="payment_differences",
    ),
    path(
        "data_for_payment_differences",
        DataForPaymentDifferences.as_view(),
        name="data_for_payment_differences",
    ),
    path(
        "data_for_repayments_report",
        DataForRepaymentsReport.as_view(),
        name="data_for_repayments_report",
    ),
    path(
        "payment_discrepancies/data",
        DataForPaymentDiscrepancies.as_view(),
        name="data_for_payment_discrepancies",
    ),
    path(
        "old_client_year_details", ClientYearDeatails.as_view(), name="client_year_details"
    ),
    path(
        "client_year_details", NewClientYearDetails.as_view(), name="client_year_details"
    ),
    path(
        "reports/repayments", RepaymentsReport.as_view(), name="repayments_report"
    ),
    path(
        "reports/agency_repayments", AgencyRepaymentsReport.as_view(), name="agency_repayments_report"
    ),
    path(
        "data_for_agency_repayments_report", DataForAgencyRepaymentsReport.as_view(), name="data_for_agency_repayments_report"
    ),
    path(
        "reports/future_payments", FuturePaymentsReport.as_view(), name="future_payments_report"
    ),
    # path("transfer_client", TransferCLientToApp.as_view(), name="transfer_client"),
    path("payment_agency", PaymentsAgencyViewSet.as_view(), name="payment_agency"),
    path("payment_agency/global/summary", PaymentAgencySummary.as_view(),
         name="payment_agency_global_summary"),
    path("payment_agency/global/summary/detail", ReportPaymentAgencySummaryDetails.as_view(),
         name="payment_agency_global_summary_detail"),
    path("repayment_agency", MakeAgencyRepayment.as_view(), name="repayment_agency"),
    path(
        "payment_agency/pdf",
        ExportPdfPaymentsAgency.as_view(),
        name="payment_agency_pdf",
    ),
    path(
        "override/pdf",
        ExportPdfOverride.as_view(),
        name="override_pdf",
    ),
    path(
        "payment_agent/global/details/pdf",
        ExportPdfPaymentGloabalAgentDetails.as_view(),
        name="payment_agent_global_details_pdf",
    ),
    path(
        "payment_global/agent/details/pdf",
        ExportPdfPaymentGlobalAgentSummaryDetails.as_view(),
        name="payment_global_agent_details_pdf",
    ),
    path(
        "data_for_payment_agency",
        DataForPaymentsAgency.as_view(),
        name="data_for_payment_agency",
    ),
    path(
        "data_for_original_payment",
        DataForOriginalPayment.as_view(),
        name="data_for_original_payment",
    ),
    path(
        "payment_agency/global",
        PaymentsGlobalAgencyViewSet.as_view(),
        name="payment_agency_global",
    ),
    path(
        "payment_agency_commission_details",
        PaymentAgencyCommissionDetails.as_view(),
        name="payment_agency_commission_details",
    ),
    path(
        "payment_global_agency_agent",
        PaymentGlobalAgencyAgent.as_view(),
        name="payment_global_agency_agent",
    ),
    path(
        "payment_agency/global/data",
        DataForPaymentsGlobalAgency.as_view(),
        name="data_payment_agency_global",
    ),
    path(
        "payment_agency/global/pdf",
        ExportPdfPaymentsGlobalAgency.as_view(),
        name="payment_agency_global_pdf",
    ),
    path(
        "payment_agency/global/details/pdf",
        ExportPdfPaymentsGlobalAgencyDetails.as_view(),
        name="payment_agency_global_details_pdf",
    ),
    path(
        "application_dashboard_summary",
        ApplicationDashboardSummary.as_view(),
        name="application_dashboard_summary",
    ),
    path(
        "pendingdocs_dashboard_summary",
        PendingDocsDashboardSummary.as_view(),
        name="pendingdocs_dashboard_summary",
    ),
    path(
        "dashboard/summary/assistant",
        SingleAssistantMonthPayment.as_view(),
        name="assistant_commission_summary",
    ),
    path(
        "reset_all_credentials", ResetPasswords.as_view(), name="reset_all_credentials"
    ),
    path(
        "data_for_pending_docs_report",
        DataForPendingDocumentsReport.as_view(),
        name="data_for_pending_docs_report",
    ),
    path("reports/payment/agent", ReportPaymentAgent.as_view(), name="payment_agent"),
    path("reports/payment_agent/global",
         PaymentGlobalAgent.as_view(), name="payment_agent"),
    path("reports/original/payment/client",
         PaymentClientOriginal.as_view(), name="original_payment_client"),
    path(
        "reports/payment/agent/summary",
        ReportPaymentAgentSummary.as_view(),
        name="payment_agent_summary",
    ),
    path(
        "reports/payment_agent/global/summary",
        ReportPaymentGlobalAgentSummary.as_view(),
        name="payment_agent_global_summary",
    ),
    path(
        "reports/agent_payments_by_insured",
        AgentPaymentsDetailsByInsurance.as_view(),
        name="agent_payments_by_insured",
    ),
    path(
        "reports/agency_agent_payments_by_insured",
        AgencyAgentPaymentsDetailsByInsurance.as_view(),
        name="agency_agent_payments_by_insured",
    ),
    path(
        "reports/payment/agent/global/original",
        PaymentGlobalOriginal.as_view(),
        name="payment_global_original",
    ),
    path(
        "reports/payment/global", ReportPaymentGlobal.as_view(), name="payment_global"
    ),
    path(
        "reports/payment/global/client", PaymentGlobalClient.as_view(), name="payment_global_client"
    ),
    path(
        "generate_original_payment", GenerateOriginalPayments.as_view(), name="generate_original_payment"
    ),
    path(
        "reports/payment/global/summary",
        PaymentGlobalSummary.as_view(),
        name="payment_global_summary",
    ),
    path(
        "reports/payment/global_client/summary",
        PaymentGlobalClientSummary.as_view(),
        name="payment_global_summary",
    ),
    path(
        "payment/assistant",
        PaymentsGlobalAssistantViewSet.as_view(),
        name="payment_assistant",
    ),
    path(
        "payment/assistant/repayment",
        MakeAssistantRepayment.as_view(),
        name="payment_assistant_repayment",
    ),
    path(
        "import_agent_global_excel",
        ImportAgentGlobalExcel.as_view(),
        name="import_agent_global_excel",
    ),
    path(
        "payment/assistant/data",
        DataForPaymentsGlobalAssistant.as_view(),
        name="payment_assistant",
    ),
    path(
        "get_agent_excel_information",
        GETAgentExcelInformation.as_view(),
        name="get_agent_excel_information",
    ),
    path(
        "delete_agent_global_excel",
        DeleteAgentGlobalExcel.as_view(),
        name="delete_agent_global_excel",
    ),
    path(
        "check_agent_license",
        CheckAgentLicenseExp.as_view(),
        name="check_agent_license",
    ),
    path(
        "reports/payment/assistants/summary",
        PaymentGlobalAssistantSummary.as_view(),
        name="payment_assistant_report_summary",
    ),
    # path(
    #     "pay_florida",
    #     PayFlorida.as_view(),
    #     name="pay_florida",
    # ),
    # path(
    #     "pay_united",
    #     PayUnited.as_view(),
    #     name="pay_united",
    # ),
    # path(
    #     "fix_wrong_year",
    #     FixWrongYearForPayments.as_view(),
    #     name="fix_wrong_year",
    # ),
    # path(
    #     "fix_wrong_repaid_on",
    #     FixWrongRepaidOn.as_view(),
    #     name="fix_wrong_repaid_on",
    # ),
    # path(
    #     "fix_wrong_repaid_on_repayments",
    #     FixWrongRepaidOnRepayments.as_view(),
    #     name="fix_wrong_repaid_on",
    # ),
    path(
        "reports/payment/assistants/summary/details",
        ReportPaymentAssistantSummaryDetails.as_view(),
        name="payment_assistant_report_summary_details",
    ),
    path(
        "reports/payment/assistants",
        PaymentGlobalAssistantYearly.as_view(),
        name="payment_assistant_report",
    ),
    path(
        "reports/payment/assistants/pdf",
        ExportPdfPaymentGloabalAssistatnt.as_view(),
        name="payment_assistant_report_pdf",
    ),
    path(
        "reports/export_pdf_agent_payments_details_by_insurance",
        ExportPdfAgentPaymentsDetailsByInsurance.as_view(),
        name="export_pdf_agent_payments_details_by_insurance",
    ),
    path(
        "reports/payment/original/global/pdf",
        ExportPdfPaymentGlobalOriginal.as_view(),
        name="export_reports_original_global",
    ),
    path(
        "reports/payment/original/client/pdf",
        ExportPdfPaymentClientOriginal.as_view(),
        name="export_reports_original_client",
    ),
    path(
        "reports/payment/assistants/clients",
        PaymentGlobalAssistantPerClient.as_view(),
        name="payment_assistant_report_clients",
    ),
    path(
        "reports/payment/assistants/clients/pdf",
        PaymentAssistantPerClientExportPdf.as_view(),
        name="payment_assistant__client_report_pdf",
    ),
    path(
        "reports/payment/assistants/global/details/pdf",
        ExportPdfPaymentGloabalAssistantDetails.as_view(),
        name="payment_assistant__global_details_pdf",
    ),
    path(
        "reports/payment/assistants/clients/summary",
        PaymentGlobalAssistantPerClientSummary.as_view(),
        name="payment_assistant_report_clients_summary",
    ),
    path(
        "mail/",
        CheckEmails.as_view(),
        name="get_mail",
    ),
    path(
        "get_county_fips",
        GetCountyFips.as_view(),
        name="get_county_fips",
    ),
    path(
        "mail/get",
        GetEmail.as_view(),
        name="mail_details",
    ),
    path(
        "mail/move",
        MoveEmail.as_view(),
        name="move_mail",
    ),
    path(
        "mail/delete",
        DeleteEmail.as_view(),
        name="delete_mail",
    ),
    path(
        "mail/toggle_seen",
        ToggleSeen.as_view(),
        name="toggle_seen_message",
    ),
    path(
        "mail/send",
        SendEmail.as_view(),
        name="send_mail",
    ),
    path(
        "send_original_discrepancies",
        SendOriginalDiscrepancies.as_view(),
        name="send_original_discrepancies",
    ),
    path(
        "mail/reply",
        ReplyEmail.as_view(),
        name="send_mail",
    ),
    path(
        "mail/credentials",
        MailCredentials.as_view(),
        name="mail_credentials",
    ),
    path(
        "mail/toggle_fav",
        ToggleFav.as_view(),
        name="toggle_fav_message",
    ),
    path(
        "sms/send",
        SendSmsView.as_view(),
        name="send_sms",
    ),
    path('client_agreement/', ClientAgreementPDFView.as_view(),
         name='client_agreement'),
    path('pre_letter/', PreLetterPDFView.as_view(),
         name='pre_letter'),
    path('update_client_agreement/', UpdateClientAgreementPDFView.as_view(),
         name='update_client_agreement'),
    path('income_letter/', IncomeLetterPDFView.as_view(),
         name='income_letter'),
    path(
        "sms/send_client_agreement",
        SendClientAgreementSMSView.as_view(),
        name="send_sms",
    ),
    path(
        "sms/send_pre_letter",
        SendPreLetterSMSView.as_view(),
        name="send_sms",
    ),
    path(
        "sms/send_update_client_agreement",
        SendUpdateClientAgreementSMSView.as_view(),
        name="send_sms",
    ),
    path(
        "sms/send_income_letter",
        SendIncomeLetterSMSView.as_view(),
        name="send_sms",
    ),
    path(
        "email/send_client_agreement",
        SendClientAgreementEmail.as_view(),
        name="send_sms",
    ),
    path(
        "email/send_pre_letter",
        SendPreLetterEmail.as_view(),
        name="send_sms",
    ),
    path(
        "email/send_update_client_agreement",
        SendClientUpdateAgreementEmail.as_view(),
        name="send_sms",
    ),
    path(
        "email/send_income_letter",
        SendIncomeLetterEmail.as_view(),
        name="send_sms",
    ),
    path(
        "sms/update_status",
        ReceiveStatusUpdate.as_view(),
        name="sms_update_status",
    ),
    path(
        "sms",
        ListConversationsView.as_view(),
        name="fetch_conversations",
    ),
    path(
        "sms/media",
        GetSmsMMediaView.as_view(),
        name="receive_sms_media",
    ),
    path(
        "sms/service",
        SendServiceSMS.as_view(),
        name="service_sms",
    ),
    path(
        "sms/tempfile",
        SmsTempFileView.as_view(),
        name="get_temp_file",
    ),
    path(
        "sms/contacts",
        UserContactsView.as_view(),
        name="sms_contacts",
    ),
    path(
        "sms/recieve",
        SMSRecieveHook.as_view(),
        name="sms_recieve",
    ),
    path(
        "sms/conversation",
        GetConversationSMSView.as_view(),
        name="fetch_conversation",
    ),
    path(
        "sms/conversation/delete",
        DeleteConversation.as_view(),
        name="delete_conversation",
    ),
    path(
        "sms/resend",
        ReSendSmsView.as_view(),
        name="resend_sms",
    ),
    path(
        "chart/data",
        DataForChartData.as_view(),
        name="chart_data_data",
    ),
    path(
        "export/client/pdf",
        ExportPdfClient.as_view(),
        name="client_pdf",
    ),
    path(
        "birthdays",
        UserBirthdays.as_view(),
        name="birthdays_list",
    ),
    path(
        "reports/generic_reports",
        GenericReports.as_view(),
        name="generic_reports",
    ),
    path(
        "data_for_generic_reports",
        DataForGenericReports.as_view(),
        name="data_for_generic_reports",
    ),
    path(
        "data_for_pre_letter",
        DataForPreLetterLog.as_view(),
        name="data_for_pre_letter",
    ),
    path("filter_search", FilterSearch.as_view(), name="filter_search"),
    path(
        "get_supoused_payment",
        GetSupousedPaymentLog.as_view(),
        name="get_supouse_payment",
    ),
    path(
        "alternative",
        GetAlternativeData.as_view(),
        name="alternative",
    ),
    path(
        "get_client_log_information",
        GetClientLogInformation.as_view(),
        name="get_client_log_information",
    ),
    # path(
    #     "reports/self_managed_agency_payments",
    #     SelfManagedAgencyPaymentView.as_view(),
    #     name="reports/self_managed_agency_payments",
    # ),
    # path(
    #     "data_for_self_managed_agency_payments",
    #     DataForSelfManagedAgencyPayment.as_view(),
    #     name="self_managed_agency_payments_data",
    # ),
    path(
        "get_pre_letter_information",
        GetPreLetterInformation.as_view(),
        name="get_pre_letter_information",
    ),
    path(
        "get_income_letter_log_information",
        GetIncomeLetterLogInformation.as_view(),
        name="get_income_letter_log_information",
    ),
    path(
        "logs/zero_payment",
        ZeroPaymentsView.as_view(),
        name="zero_payment_logs",
    ),
    path(
        "logs/zero_payment/data",
        DataForZeroPaymentsView.as_view(),
        name="zero_payment_logs_data",
    ),
    path(
        "logs/clients",
        ClientLogsView.as_view(),
        name="client_logs",
    ),
    path(
        "logs/logs_by_client",
        SingleClientLogs.as_view(),
        name="client_logs",
    ),
    path(
        "logs/clients/data",
        DataForClientLogs.as_view(),
        name="client_logs_data",
    ),
    path(
        "logs/general",
        GeneralLogsView.as_view(),
        name="general_logs",
    ),
    path(
        "logs/general/data",
        DataForGeneralLogsView.as_view(),
        name="general_logs_data",
    ),
    path(
        "reports/agents_by_agency",
        AgentsByAgency.as_view(),
        name="agents_by_agency",
    ),
    #  path('mark_read',MarkReaded.as_view(),name='mark_read'),
] + router.urls
