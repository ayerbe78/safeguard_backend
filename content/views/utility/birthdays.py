from ..imports import *


class UserBirthdays(APIView, AgencyManagement, DashboardCommons):
    def get(self, request: APIViewRequest):
        user_id = self.dash_get_alternative_user(request)

        bd_list = []
        today = date.today()

        if self.current_is("agent", user_id):
            insurances = Insured.objects.all()
            clients = self.get_related_clients(user_id, True)
            if (request.GET.get('by') == 'month'):
                clients = clients.filter(
                    date_birth__month=today.month,
                    aplication_date__year=today.year,
                ).order_by("names", "lastname").values()
            else:
                clients = clients.filter(
                    date_birth__day=today.day,
                    date_birth__month=today.month,
                    aplication_date__year=today.year,
                ).order_by("names", "lastname").values()

            bd_list = list(
                map(
                    lambda c: {
                        "id": c.get("id"),
                        "name": f"{c.get('names')} {c.get('lastname')}",
                        "telephone": c.get("telephone"),
                        "dob": c.get("date_birth"),
                        "type": "client",
                        "belongs": insurances.get(id=c.get("id_insured")).names
                        if c.get("id_insured")
                        and insurances.filter(id=c.get("id_insured")).exists()
                        else None,
                    },
                    clients,
                )
            )
        if self.current_is("assistant", user_id) or self.current_is("admin", user_id):
            agencies = Agency.objects.all()
            agents = self.get_related_agents(user_id, True)
            if (request.GET.get('by') == 'month'):
                agents = agents.filter(date_birth__month=today.month).order_by(
                    "agent_name", "agent_lastname").values()
            else:
                agents = agents.filter(date_birth__day=today.day, date_birth__month=today.month).order_by(
                    "agent_name", "agent_lastname").values()

            bd_list = list(
                map(
                    lambda c: {
                        "id": c.get("id"),
                        "name": f"{c.get('agent_name')} {c.get('agent_lastname')}",
                        "telephone": c.get("telephone"),
                        "dob": c.get("date_birth"),
                        "type": "agent",
                        "belongs": agencies.get(id=c.get("id_agency")).agency_name
                        if c.get("id_agency")
                        and agencies.filter(id=c.get("id_agency")).exists()
                        else None,
                    },
                    agents,
                )
            )

        return Response(bd_list)
