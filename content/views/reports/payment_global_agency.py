from ..imports import *
from django.db.models import Case, When


class PaymentsGlobalAgencyViewSet(APIView, AgencyManagement, LimitOffsetPagination):
    permission_classes = [HasPaymentGlobalAgencyPermission]

    def get(self, request: HttpRequest):
        entries = self.get_entries(request)

        page = self.paginate_queryset(entries, request, view=self)
        serilizer = PaymentsGlobalAgencySerializer(page, many=True)
        response = self.get_paginated_response(serilizer.data)
        return response

    def get_entries(self, request):
        agencies = self.__apply_filters(request)
        agencies = self.__apply_search(agencies, request)
        agencies = self.apply_order_queryset(
            agencies, request, "agency__agency_name")
        return agencies

    def __apply_filters(self, request):
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            result = PaymentsGlobalAgency.objects.filter(insured=insured)
        else:
            result = PaymentsGlobalAgency.objects.all()

        payment = self.check_none(request.GET.get("payment"))
        if payment and int(payment) == 1:
            result = result.exclude(total_commission=0)
        elif payment and int(payment) == 2:
            result = result.filter(total_commission=0)

        agency = self.select_agency(request.GET.get("agency"), request.user.pk)
        if agency:
            result = result.filter(agency=agency.pk)
        else:
            result = result.filter(
                agency__in=self.get_related_agencies(request.user.pk, True)
            )

        agent = self.select_agent(request.GET.get("agent"), request.user.pk)
        if agent:
            result = result.filter(agent=agent)

        month = self.check_none(request.GET.get("month"))
        if month:
            try:
                result = result.filter(month=self.map_month(int(month)))
            except:
                pass
            payment = self.check_none(request.GET.get("payment"))
            if payment and int(payment) == 1:
                result = result.exclude(total_commission=0)
            elif payment and int(payment) == 2:
                result = result.filter(total_commission=0)

        year = self.check_none(request.GET.get("year"))
        if year:
            try:
                result = result.filter(year=year)
            except:
                pass

        result = result.exclude(client__borrado=1)

        result = result.values(
            "insured__names", "agency__agency_name", "year", "month", "insured_id", "agency_id"
        ).annotate(
            commission=Sum("total_commission"),
            members=Sum(Case(
                When(~Q(total_commission=0), then="members_number"),
                default=0
            )),
        )

        return result

    def __apply_search(self, queryset, request):
        search = self.check_none(request.GET.get("search"))
        if search:
            queryset = queryset.filter(
                Q(agency__agency_name__icontains=search)
            )
        return queryset


class DataForPaymentsGlobalAgency(APIView, AgencyManagement):
    permission_classes = [HasPaymentGlobalAgencyPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "agencies", "insurances"))


class ExportExcelPaymentGloablAgency(
    XLSXFileMixin, ReadOnlyModelViewSet, PaymentsGlobalAgencyViewSet
):
    permission_classes = [HasExportExcelPaymentGlobalAgencyPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentsGlobalAgencySerializer
    xlsx_use_labels = True
    filename = "payment_global_agency.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request: APIViewRequest):

        results = self.get_entries(request)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)


class ExportPdfPaymentsGlobalAgency(PaymentsGlobalAgencyViewSet, PDFCommons):
    permission_classes = [HasExportPDFPaymentGlobalAgencyPermission]

    def get(self, request):
        results = self.get_entries(request)

        data = [
            [
                i + 1,
                r.get("agency__agency_name"),
                r.get("insured__names"),
                r.get("month"),
                r.get("members"),
                r.get("commission"),
            ]
            for i, r in enumerate(results)
        ]
        headers = [
            "Indx",
            "Agency",
            "Insurance",
            "Month",
            "Members",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A3, 'Agency Report', True)


class PaymentAgencySummary(APIView, PaymentCommons):
    def get(self, request: HttpRequest):
        filters = self._apply_filters(request)
        sql = f"""
                SELECT
                    p.indx,
                    COUNT(CASE WHEN p.total_commission <> 0 THEN 1 END),
                    SUM(p.total_commission)
                FROM
                    payments_global_agency p
                JOIN agency a on p.id_agency = a.id
                
                WHERE 1 {filters}
                GROUP BY
                    p.indx
                """
        response = self.sql_select_all(
            sql, ["indx", "count", "commission"])
        return Response(response)

    def _apply_filters(self, request: HttpRequest):
        user = request.user
        filters = ""
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        filters += f" and p.year={year} "
        insured = self.check_none(request.GET.get("insured"))
        if insured:
            filters += f" AND p.id_insured={insured} "

        agencies = self.get_related_agencies(user.pk, True, ["id"])
        filters += f" and p.id_agency in ({self.queryset_to_list(agencies, to_string=True)})"
        agency = self.select_agency(request.GET.get("agency"), user.pk)
        if agency:
            filters += f" and p.id_agency = {agency.id}"

        month = self.check_none(request.GET.get("month"))
        if month:
            month = self.map_month(int(month))
            filters += f" and p.month='{month}' "
        payment = self.check_none(request.GET.get("payment"))
        if payment and int(payment) == 1:
            filters += f" AND p.total_commission<>0 "
        elif payment and int(payment) == 2:
            filters += f" AND p.total_commission=0 "
        search = self.check_none(request.GET.get("search"))
        if search:
            filters += (
                f" and a.agency_name like '%{search}%' "
            )
        return filters


class PaymentAgencyCommissionDetails(
    PaymentAgencySummary, LimitOffsetPagination
):
    def get(self, request):
        results = self.get_entries(request)
        results = self.paginate_queryset(results, request, view=self)
        response = self.get_paginated_response(results)
        return response

    def get_entries(self, request):
        agency = self.check_none(request.GET.get("agency"))
        insured = self.check_none(request.GET.get("insured"))
        month = self.check_none(request.GET.get("month"))
        month = self.sql_curate_query(month).lower()
        year = self.check_none(request.GET.get("year"), str(date.today().year))

        if not agency or not insured or not month or not year:
            raise ValidationException()

        query = f"""
            SELECT 
                ch.id_children_agency, ch.agency_name, 'Secondary Payment' AS payment_type, SUM(pay.policies), SUM(pay.commission)
            FROM
                (
                    SELECT 
                        so.id_children_agency, ag.agency_name, a.id AS id_agent
                    FROM
                        secondary_override so LEFT JOIN agent a ON (so.id_children_agency = a.id_agency)
                        LEFT JOIN agency ag ON(so.id_children_agency=ag.id) 
                    WHERE
                        so.id_parent_agency={agency} AND  so.id_insured={insured}
                    
                )	ch
                
                LEFT JOIN
                (
                    SELECT 
                        p.id_agent, COUNT(id) AS policies, SUM(p.total_commission) AS commission
                    FROM
                        payments_global_agency p
                    WHERE 	p.id_insured={insured} AND p.id_agency={agency} AND p.`month`='{month}' AND  p.`year`={year} AND p.indx=5
                    GROUP BY p.id_agent
                ) pay
                ON (ch.id_agent=pay.id_agent)
                
            GROUP BY ch.id_children_agency, ch.agency_name
            ORDER BY ch.agency_name
        """

        secondary_agency = self.sql_select_all(
            query, ["id", "agency_name", "payment_type", "policies", "commission"])

        query = f"""
            SELECT 
                p.id_agency, a.agency_name , 'Principal Payment' AS payment_type, COUNT(p.id) AS policies, SUM(p.total_commission) AS commission
            FROM
                payments_global_agency p JOIN agency a ON (p.id_agency =  a.id)
            WHERE 	p.id_insured={insured} AND p.id_agency={agency} AND p.`month`='{month}' AND  p.`year`={year} AND p.indx<>5
               
        """

        main_agency = self.sql_select_all(
            query, ["id", "agency_name", "payment_type", "policies", "commission"])
        secondary_agency.append(main_agency[0])
        return secondary_agency


class ReportPaymentAgencySummaryDetails(
    PaymentAgencySummary, LimitOffsetPagination
):
    def get(self, request):
        primary_results = self.get_entries(request)
        total_paid = 0
        for p in primary_results:
            try:
                total_paid += float(p["comission"])
            except:
                pass
        data = self.__apply_order(primary_results, request)
        results = self.paginate_queryset(data, request, view=self)
        response = self.get_paginated_response(results)
        response.data["total_paid"] = total_paid

        return response

    def get_entries(self, request):
        index = self.check_none(request.GET.get("index"), 0)
        year = self.check_none(request.GET.get("year"), str(date.today().year))
        index = self.sql_curate_query(index)
        filters = self._apply_filters(request)
        query = f"""
            SELECT
                concat(a.agent_name,' ', a.agent_lastname),
                concat(c.names, ' ', c.lastname ),
                i.names,
                a.npn,
                c.suscriberid,
                c.family_menber,
                c.aplication_date,
                p.month,
                p.total_commission as commission
            FROM
                payments_global_agency p
            JOIN agent a ON
                p.id_agent = a.id 
            JOIN insured i on (p.id_insured=i.id)
            JOIN client c on (p.id_client=c.id)
            WHERE 1 {filters} AND p.indx = {index} and c.borrado <> 1 and SUBSTRING(c.aplication_date,1,4) ='{year}'
        """

        primary_results = self.sql_select_all(
            query, ["agent_name", "client_name", "insured", "npn", "suscriberid", "family_menber", "aplication_date", "month", "comission"])

        return primary_results

    def __apply_order(self, data, request):
        order_default = "agent_name"
        order = self.check_none(request.GET.get("order"), order_default)
        desc = self.check_none(request.GET.get("desc"), False)
        desc = 1 if desc else 0

        if order not in ["commission", "num_member"]:
            return self.apply_order_dict_list(data, request, order_default)

        def key_func(x):
            return x[order] if x[order] else -1

        try:
            queryset = sorted(data, key=key_func, reverse=desc)
        except KeyError:
            order = order_default
            queryset = sorted(data, key=key_func, reverse=desc)

        return queryset


class ExportPdfPaymentsGlobalAgencyDetails(ReportPaymentAgencySummaryDetails, PDFCommons):
    permission_classes = [HasExportPDFPaymentGlobalAgencyPermission]

    def get(self, request):
        results = self.get_entries(request)
        data = [
            [
                i + 1,
                r.get("agent_name"),
                r.get("client_name"),
                r.get("insured"),
                r.get("npn"),
                r.get("suscriberid"),
                r.get("family_menber"),
                r.get("aplication_date"),
                r.get("month"),
                r.get("comission")
            ]
            for i, r in enumerate(results)
        ]
        headers = [
            "Indx",
            "Agent",
            "Client",
            "Insurance",
            "NPN",
            "Suscriber ID",
            "Members",
            "Application Date",
            "Month",
            "Commission",
        ]

        return self.pdf_create_table(headers, data, A2, 'Agency Report', True)


class ExportExcelPaymentGloablAgencyDetails(
    XLSXFileMixin, ReadOnlyModelViewSet, ReportPaymentAgencySummaryDetails
):
    permission_classes = [HasExportExcelPaymentGlobalAgencyPermission]
    renderer_classes = (XLSXRenderer,)
    serializer_class = PaymentsGlobalAgencyDetailsSerializer
    xlsx_use_labels = True
    filename = "payment_global_agency_details.xlsx"
    xlsx_ignore_headers = ["id"]

    def list(self, request: APIViewRequest):

        results = self.get_entries(request)

        serializer = self.get_serializer(results, many=True)

        return Response(serializer.data)
