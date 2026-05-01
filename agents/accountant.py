import os
from typing import Dict, Any

class AccountantAgent:
    def __init__(self):
        pass

    def verify_budget(self, budget_limit: float, costs: Dict[str, float]) -> Dict[str, Any]:
        total_cost = sum(costs.values())
        within_budget = total_cost <= budget_limit
        return {
            "total_cost": total_cost,
            "budget_limit": budget_limit,
            "within_budget": within_budget,
            "details": costs
        }