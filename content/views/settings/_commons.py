from ..imports import *


class CommissionCommons:
    def check_existing_in_agents(self, agent, state, insured, yearcom):
        selection = AgentCommission.objects.filter(
            agent=agent, state=state, insured=insured, yearcom=yearcom
        )
        return selection.exists()

    def check_existing_in_groups(self, group, state, insured, yearcom):
        selection = GroupCommission.objects.filter(
            group=group, state=state, insured=insured, yearcom=yearcom
        )
        return selection.exists()

    def check_existing_in_agents_request(self, request: APIViewRequest):
        agent = request.data.get("agent")
        state = request.data.get("state")
        insured = request.data.get("insured")
        yearcom = request.data.get("yearcom")
        return self.check_existing_in_agents(agent, state, insured, yearcom)

    def check_existing_in_groups_request(self, request: APIViewRequest):
        group = request.data.get("group")
        state = request.data.get("state")
        insured = request.data.get("insured")
        yearcom = request.data.get("yearcom")
        return self.check_existing_in_groups(group, state, insured, yearcom)

    # def apply_order(self, queryset, request: APIViewRequest, defaultOrder: str):
    #     order = self.check_none(request.query_params.get("order"))
    #     desc = self.check_none(request.query_params.get("desc"), 0)
    #     if order:
    #         queryset = queryset.order_by(
    #             f"{'-'+order if desc else order}", defaultOrder
    #         )
    #     else:
    #         queryset = queryset.order_by(defaultOrder)
    #     return queryset
