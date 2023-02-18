import yaml

from pathlib import Path

from definitions import ROOT_DIR


class Budget:
    extra: float
    spend_per_day: float
    savings: float
    expected: float
    takehome: float

    def __init__(self):
        self.load_budget()

    def load_budget(self):
        with open(
                Path(
                    ROOT_DIR / 'budget_report_generator/spending_config.yaml'
                ), 'r'
        ) as b:
            budget = yaml.safe_load(b)
            budget = budget['budget']['monthly']

            self.extra = (
                budget['take-home']
                - budget['rent']
                - budget['savings']
                - self._get_expected_totals(budget['expected'])
            )

            self.spend_per_day = self.extra / 30.5
            self.savings = budget['savings']
            self.takehome = budget['take-home']
            self.rent = budget['rent']

    def _get_expected_totals(self, expected):
        total = 0
        for name, val in expected.items():
            total += val

        self.expected = total

        return total
