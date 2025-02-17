from ..imports import *


class ImportOverride(APIView, PaymentCommons):
    permission_classes = [HasImportPaymentCSVPermission]

    def post(self, request: APIViewRequest):
        with transaction.atomic():
            insured = request.data.get("insured")
            insured_obj = Insured.objects.filter(id=insured).get()
            param_date = request.data.get("date")  #

            divided_date = param_date.split("-")
            year = str(divided_date[0])
            month = str(divided_date[1])
            month = month if len(month) == 2 else "0" + month

            self.make_payment(
                request, insured, year, month, insured_obj.names
            )
        return Response(status=status.HTTP_202_ACCEPTED)

    def make_payment(
        self, request, insured, year, month, insured_name
    ):
        file = request.data.get("file")
        decoded_file = file.read().decode()
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        overrides = []

        first_check = 1
        for pos, row in enumerate(reader):
            if first_check:
                first_check = 0
                continue
            client_name = self.__aux_get_value(request, row, "client_name", "").replace(
                ",", " "
            )
            if self.check_none(request.data.get('client_lastname'), None):
                client_name = client_name + " " + \
                    self.__aux_get_value(request, row, "client_lastname", "")
            info_month_str = self.__aux_get_value(request, row, "month", None)
            info_month = self.date_from_text(
                info_month_str, multiple_formats=[
                    "%m/%d/%Y", "%Y-%m-%d", "%Y%m%d"]
            )
            if not info_month:
                raise ValidationException(
                    f"Info Month in row {pos+1} must be a string field with format YYYY/mm/dd/ or mm/dd/YYYY, not {info_month_str}"
                )
            info_month = f"{info_month.month}/{info_month.day}/{info_month.year}"
            payment_type = self.__aux_get_value(request, row, "new_ren", "")
            suscriberid = self.__aux_get_p_number(request, row, insured, pos)
            members_number = self.__aux_get_num_members(request, row, pos)
            agent_name = self.__aux_get_value(request, row, "agent_name", "")

            data = self.match_insurance(request, row, pos, insured, month, year, insured_name,
                                        info_month, payment_type, suscriberid, members_number, client_name, agent_name)
            if data:
                overrides.append(data)
                if len(overrides) > 5000:
                    Override.objects.bulk_create(overrides)
                    overrides.clear()

        if overrides:
            Override.objects.bulk_create(overrides)

    def match_insurance(self, request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name):
        override_instance = None
        if int(insured) == 1:
            override_instance = self.pay_molina(
                request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name)
        if int(insured) == 2:
            override_instance = self.pay_ambetter(
                request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name)
        if int(insured) == 9:
            override_instance = self.pay_oscar(
                request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name)
        if int(insured) == 11:
            override_instance = self.pay_cigna(
                request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name)
        if int(insured) == 17:
            override_instance = self.pay_aetna(
                request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name)

        return override_instance

    def pay_oscar(self, request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name):
        state = self.__aux_get_value(request, row, "state", "")
        data = Override(
            id_insured=insured,
            year=year,
            month=month,
            info_month=info_month,
            payment_type=payment_type,
            client_name=client_name,
            agent_name=agent_name,
            state=state,
            insured_name=insured_name,
            suscriberid=suscriberid,
            members_number=members_number,
            commission=self.__aux_get_value(
                request, row, "commision", 0.0, floated=True
            ),
        )
        return data

    def pay_aetna(self, request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name):
        ga = self.__aux_get_value(request, row, "gaType", "no")
        state = self.__aux_get_value(request, row, "state", "")

        if ga == 'yes':
            data = Override(
                id_insured=insured,
                year=year,
                month=month,
                info_month=info_month,
                payment_type=payment_type,
                client_name=client_name,
                agent_name=agent_name,
                state=state,
                insured_name=insured_name,
                suscriberid=suscriberid,
                members_number=members_number,
                commission=self.__aux_get_value(
                    request, row, "commision", 0.0, floated=True
                ),
            )
            return data
        else:
            return None

    def pay_molina(self, request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name):
        policy_number = self.__aux_get_value(
            request, row, "policy_number", None)
        state = policy_number[:2]

        if agent_name == 'Safeguard & Associates, Inc.':
            data = Override(
                id_insured=insured,
                year=year,
                month=month,
                info_month=info_month,
                payment_type=payment_type,
                client_name=client_name,
                agent_name="",
                state=state,
                insured_name=insured_name,
                suscriberid=suscriberid,
                members_number=members_number,
                commission=self.__aux_get_value(
                    request, row, "commision", 0.0, floated=True
                ),
            )
            return data
        else:
            return None

    def pay_ambetter(self, request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name):
        state = self.__aux_get_value(request, row, "state", "")
        ambetter_commission = request.data.get('ambetter_commission')
        data = Override(
            id_insured=insured,
            year=year,
            month=month,
            info_month=info_month,
            payment_type=payment_type,
            client_name=client_name,
            agent_name=agent_name,
            state=state,
            insured_name=insured_name,
            suscriberid=suscriberid,
            members_number=members_number,
            commission=int(members_number) * float(ambetter_commission),
        )
        return data

    def pay_cigna(self, request, row, pos, insured, month, year, insured_name, info_month, payment_type, suscriberid, members_number, client_name, agent_name):
        pmpm = self.__aux_get_value(request, row, "pmpmType", "no")
        state = self.__aux_get_value(request, row, "state", "")
        state = state[:2]

        if pmpm == 'PMPM Fee':
            data = Override(
                id_insured=insured,
                year=year,
                month=month,
                info_month=info_month,
                payment_type=payment_type,
                client_name=client_name,
                agent_name=agent_name,
                state=state,
                insured_name=insured_name,
                suscriberid=suscriberid,
                members_number=members_number,
                commission=self.__aux_get_value(
                    request, row, "commision", 0.0, floated=True
                ),
            )
            return data
        else:
            return None

    def __aux_get_value(
        self, request, row, param, default=0, integer=False, floated=False
    ):
        element = request.data.get(param)
        if element == None:
            return default
        try:
            value = row[int(element)]
            if floated:
                value = float(value)
            elif integer:
                value = int(value)
        except:
            value = default
        return value

    def __aux_get_p_number(self, request, row, insured, pos):
        value = self.__aux_get_value(request, row, "policy_number", None)
        aetna_mode = 1 if int(insured) == 17 else 0
        molina_mode = 1 if int(insured) == 1 else 0

        if value == None:
            raise ValidationException(
                f"Suscriber Id in row {pos+1} must be a valid string"
            )

        if aetna_mode:
            value = value[4:-7]
        elif molina_mode:
            value = value[3:]

        return value

    def __aux_get_num_members(self, request, row, pos):
        value = self.__aux_get_value(
            request, row, "num_member", integer=True, default=None
        )
        if value == None:
            return 0
            # raise ValidationException(
            #     f"Members # in row {pos+1} must be a valid decimal number"
            # )
        return abs(value)
