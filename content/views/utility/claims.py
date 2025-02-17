from ..imports import *
from django.db.models.functions import Coalesce
from django.db.models import Max, Value


class OldClaimHistory(APIView):
    def get(self, request):
        user: CustomUser = request.user
        serializer = ClaimSerializer
        suscriberid = request.GET.get("suscriberid")

        if suscriberid == None:
            raise ValidationException("No Suscriber Id provided")

        x = date.today()
        a = date(x.year, 1, 1)
        b = date(x.year, 12, 31)

        if not (isAgent(user) or user.is_admin):
            raise ForbiddenException("Only Agents can see History")

        client = Client.objects.filter(
            suscriberid=suscriberid, aplication_date__range=[a, b]
        )
        if isAgent(user):
            current_agent = Agent.objects.filter(
                email=request.user.email).get()
            client = client.filter(id_agent=current_agent.pk)
        if client.exists():
            claims = Claim.objects.filter(
                subcriberid=suscriberid, date_begin__range=[a, b]
            ).order_by("months")
            serializer = serializer(claims, many=True)
            return Response(serializer.data)
        else:
            return Response([])


class ClaimViewSet(viewsets.ModelViewSet, AgencyManagement, DirectSql):
    permission_classes = [HasClaimPermission]
    serializer_class = ClaimSerializer
    queryset = Claim.objects.all()

    def create(self, request: APIViewRequest, *args, **kwargs):
        user: CustomUser = request.user
        data = request.data

        id_agent = self.current_is("agent", user.pk)
        if not id_agent:
            raise ValidationException("Only Agent can create Claim")
        suscriber = request.data.get('subcriberid', None)

        client, year_from_request = self.__check_correct_subscriber(
            request, id_agent, suscriber)
        self.__check_payment_status(
            request, client.id, id_agent, year_from_request, suscriber)
        self.__check_duplicated_claim(suscriber)
        months = data.get("months")
        insured = self.check_none(data.get("insured"))
        with transaction.atomic():
            data["id_agent"] = id_agent
            data["date_begin"] = date.today()
            data["months"] = ",".join(months)
            data["insured"] = insured
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
            self.__create_claim_history(result, True, result.note, result.file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def __create_claim_history(self, claim, claimer, message, file):
        max_claim_history_number = ClaimHistory.objects.filter(id_claim=claim.id).aggregate(
            max_message_number=Coalesce(Max('message_number'), Value(0))
        )['max_message_number']

        data = ClaimHistory(
            id_claim=claim.id,
            claimer=claimer,
            seen=False,
            message=message,
            message_number=max_claim_history_number+1,
            file=file if file is not None else None
        )
        data.save()

    def __check_correct_subscriber(self, request: HttpRequest, id_agent, suscriber):

        if suscriber:
            application_date = request.data.get('efectibedate')
            year_from_request = datetime.strptime(
                application_date, "%Y-%m-%d").year
            client = Client.objects.filter(
                suscriberid=suscriber, aplication_date__year=year_from_request, id_agent=id_agent).exclude(borrado=1)
            if not len(client) == 1:
                raise ValidationException(
                    "This subscriber id doesn't match any client in the year of the Effective Date")
            else:
                return client.get(), year_from_request

    def __check_payment_status(self, request: HttpRequest, client, agent, year, suscriber):
        months = request.data.get("months")
        for month in months:
            old_paid = self.__check_old_paid(
                self.map_month(month), year, client, agent)
            info_month = f"{int(month)}/1/{year}"
            new_paid = self.__check_new_paid(info_month, year, suscriber)
            repaid = self.__check_repaid(info_month, year, suscriber)

            if old_paid:
                raise ValidationException("This Policy is already paid")
            if repaid:
                raise ValidationException(
                    f"This Policy will be paid on {repaid.month}/1/{year}")
            if new_paid:
                raise ValidationException(
                    f"This Policy was paid on {new_paid.month}/1/{year}")

    def __check_old_paid(self, month, year, client, agent):
        sql = f"Select * from payments where {month}<>0 and fecha={year} and id_client={client} and id_agent={agent}"
        payment = self.sql_select_first(sql)
        if payment:
            return True

    def __check_new_paid(self, info_month, year, suscriberid):
        payment = AgentPayments.objects.filter(
            info_month=info_month, year=year, suscriberid=suscriberid).exclude(commission=0)
        if len(payment) > 0:
            return payment.get()

    def __check_repaid(self, info_month, year, suscriberid):
        payment = Repayments.objects.filter(
            info_month=info_month, year=year, suscriberid=suscriberid)
        if len(payment) > 0:
            return payment.get()

    def __check_duplicated_claim(self, suscriberid):
        claims = Claim.objects.filter(
            subcriberid=suscriberid, finished=None)
        if len(claims) > 0:
            raise ValidationException(
                "There is already a claim on this policy. Wait for it to be resolved")

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        current: Claim = self.get_object()
        current.date_end = date.today()
        current.finished = 1
        current.save()
        serializer = self.get_serializer(current)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        pending = self.__get_pending_calims(request.user)
        data = {}
        data["pending"] = pending
        return Response(data)

    @action(methods=["get"], detail=False, url_path="data")
    def data_for_claims(self, request):
        user = request.user
        selects = self.get_selects(user.pk, "insurances", "agents")
        return Response(selects)

    @action(methods=["get"], detail=False, url_path="pending")
    def pending_claims_summary(self, request: APIViewRequest):
        user: CustomUser = request.user
        count = self.__get_pending_calims(user)

        return Response({"count": count})

    @action(methods=["post"], detail=True, url_path="finish")
    def finish(self, request: APIViewRequest, pk):
        super().update(request)
        current: Claim = self.get_object()
        current.date_end = date.today()

        if request.user.is_admin:
            current.finished = 1
            current.seen = 0
            claimer = False
            message = current.note_responce
        else:
            current.finished = 0
            current.seen = 1
            claimer = True
            message = current.note

        current.save()
        serializer = self.get_serializer(current)
        data = serializer.data
        pending = self.__get_pending_calims(request.user)
        data["pending"] = pending

        file = request.data.get('file', None)
        self.__create_claim_history(
            current, claimer, message, file)

        history = ClaimHistory.objects.filter(id_claim=current.id)
        history_serializer = ClaimHistorySerializer(
            history, many=True)
        data['history'] = history_serializer.data

        return Response(data)

    @action(methods=["post"], detail=True, url_path="setseen")
    def set_seen(self, request: APIViewRequest, pk):
        user: CustomUser = request.user
        agent_id = self.current_is("agent", user.pk)

        current: Claim = self.get_object()
        if current.id_agent == agent_id and current.finished:
            current.seen = 1
            current.save()

        serializer = self.get_serializer(current)
        data = serializer.data
        pending = self.__get_pending_calims(request.user)
        data["pending"] = pending
        return Response(data)

    @action(methods=["get"], detail=False, url_path="filter")
    def filter(self, request: APIViewRequest):
        claims = self.__apply_filter(request)
        claims_dict = claims.values()
        for claim in claims_dict:
            try:
                agent = Agent.objects.get(pk=claim["id_agent"])
                claim["agent"] = f"{agent.agent_name} {agent.agent_lastname}"
                claim["client"] = f"{claim['names']} {claim['lastname']}"

                history = ClaimHistory.objects.filter(id_claim=claim['id'])
                serializer = ClaimHistorySerializer(
                    history, many=True)
                claim['history'] = serializer.data
            except Exception as e:
                claim["agent"] = ""
        claims_dict = self.apply_order_dict_list(claims_dict, request, "agent")
        page = self.paginate_queryset(claims_dict)
        data = self.get_paginated_response(page).data
        pending = self.__get_pending_calims(request.user)
        data["pending"] = pending

        return Response(data)

    def __apply_filter(self, request):
        user: CustomUser = request.user
        agents = self.get_related_agents(user.pk, True)
        agent = self.select_agent(request.query_params.get("agent"), user.pk)
        if agent:
            agents = agents.filter(id=agent.pk)

        claims = (
            Claim.objects.prefetch_related("insured")
            .annotate(insured_name=F("insured__names"))
            .filter(id_agent__in=self.queryset_to_list(agents))
        )

        option = self.check_none(request.GET.get("option"))
        if option == "1":
            claims = claims.filter(finished=1)
        elif option == "2":
            claims = claims.filter(
                date_end__range=["2000-01-01", date.today()])
        elif option == "3":
            claims = claims.filter(Q(finished=None) | Q(finished=0))
        elif option == "4":
            claims = claims.filter(finished=1).exclude(seen=1)

        year = self.check_none(request.GET.get("year"))
        if year:
            a = date(int(year), 1, 1)
            b = date(int(year) + 1, 1, 1)
            claims = claims.filter(date_begin__range=[a, b])

        month = self.check_none(request.GET.get("month"))
        if month:
            month2 = f"0{month}"
            claims = claims.filter(
                Q(months__icontains=month) | Q(months__icontains=month2)
            )

        insured = self.check_none(request.GET.get("insured"))
        if insured:
            claims = claims.filter(insured=insured)

        search = self.check_none(request.GET.get("search"), "")
        claims = claims.filter(
            Q(names__icontains=search)
            | Q(lastname__icontains=search)
            | Q(subcriberid__icontains=search)
            | Q(note__icontains=search)
        )

        return claims

    def __get_pending_calims(self, user):
        count = 0
        agents = self.get_related_agents(user.pk, True)
        agent_ids = self.queryset_to_list(agents)
        all_claims = Claim.objects.filter(id_agent__in=agent_ids)
        if user.is_admin:
            year = date.today().year
            count = (
                all_claims.filter(Q(finished=None) | Q(finished=0))
                .filter(
                    Q(date_begin__icontains=year) | Q(
                        date_begin__icontains=year - 1)
                )
                .count()
            )
        agent_id = self.current_is("agent", user.pk)
        if agent_id:
            count = all_claims.filter(finished=1).exclude(seen=1).count()

        return count


class FilterClaims(APIView, LimitOffsetPagination):
    permission_classes = [HasClaimPermission]
    serializer_class = ClaimSerializer
    queryset = Claim.objects.all()

    def get(self, request):
        agent = request.GET.get("agent")
        year = request.GET.get("year")
        month = request.GET.get("month")
        option = request.GET.get("option")
        if agent == None or year == None or month == None or option == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class
        if isAgent(request.user):
            agent_obj = Agent.objects.filter(email=request.user.email).get()
            if option == "0":
                queryset = Claim.objects.filter(id_agent=agent_obj.id)
            elif option == "1":
                queryset = Claim.objects.filter(
                    finished=1, id_agent=agent_obj.id)
            elif option == "2":
                queryset = Claim.objects.filter(
                    date_end__range=["2000-01-01", date.today()], id_agent=agent_obj.id
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if year != "0":
                x = date.today()
                a = date(x.year, 1, 1)
                b = date(x.year, 12, 31)
                queryset = queryset.filter(date_begin__range=[a, b])

            if month != "0":
                if int(month) == 1:
                    month1 = "01"
                    month2 = "1"
                elif int(month) == 2:
                    month1 = "02"
                    month2 = "2"
                elif int(month) == 3:
                    month1 = "03"
                    month2 = "3"
                elif int(month) == 4:
                    month1 = "04"
                    month2 = "4"
                elif int(month) == 5:
                    month1 = "05"
                    month2 = "5"
                elif int(month) == 6:
                    month1 = "06"
                    month2 = "6"
                elif int(month) == 7:
                    month1 = "07"
                    month2 = "7"
                elif int(month) == 8:
                    month1 = "08"
                    month2 = "8"
                elif int(month) == 9:
                    month1 = "09"
                    month2 = "9"
                elif int(month) == 10:
                    month1 = "10"
                    month2 = "10"
                elif int(month) == 11:
                    month1 = "11"
                    month2 = "11"
                elif int(month) == 12:
                    month1 = "12"
                    month2 = "12"
                queryset1 = queryset.filter(months=month1)
                queryset2 = queryset.filter(months=month2)
                queryset = queryset1 | queryset2

            page = self.paginate_queryset(queryset, request, view=self)
            if page is not None:
                serializer = serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = serializer(queryset, many=True)
            return Response(serializer.data)
        else:

            if option == "0":
                queryset = self.queryset
            elif option == "1":
                queryset = Claim.objects.filter(finished=1)
            elif option == "2":
                queryset = Claim.objects.filter(
                    date_end__range=["2000-01-01", date.today()]
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if agent != "0":
                agent_obj = Agent.objects.filter(id=agent)
                if len(agent_obj) == 1:
                    queryset = queryset.filter(id_agent=agent)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            if year != "0":
                x = date.today()
                a = date(x.year, 1, 1)
                b = date(x.year, 12, 31)
                queryset = queryset.filter(date_begin__range=[a, b])

            if month != "0":
                if int(month) == 1:
                    month1 = "01"
                    month2 = "1"
                elif int(month) == 2:
                    month1 = "02"
                    month2 = "2"
                elif int(month) == 3:
                    month1 = "03"
                    month2 = "3"
                elif int(month) == 4:
                    month1 = "04"
                    month2 = "4"
                elif int(month) == 5:
                    month1 = "05"
                    month2 = "5"
                elif int(month) == 6:
                    month1 = "06"
                    month2 = "6"
                elif int(month) == 7:
                    month1 = "07"
                    month2 = "7"
                elif int(month) == 8:
                    month1 = "08"
                    month2 = "8"
                elif int(month) == 9:
                    month1 = "09"
                    month2 = "9"
                elif int(month) == 10:
                    month1 = "10"
                    month2 = "10"
                elif int(month) == 11:
                    month1 = "11"
                    month2 = "11"
                elif int(month) == 12:
                    month1 = "12"
                    month2 = "12"
                queryset1 = queryset.filter(months=month1)
                queryset2 = queryset.filter(months=month2)
                queryset = queryset1 | queryset2

            page = self.paginate_queryset(queryset, request, view=self)
            if page is not None:
                serializer = serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = serializer(queryset, many=True)
            return Response(serializer.data)
