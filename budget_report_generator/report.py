"""
Basically this will allow for further visualization to be applied to the
report. For now this is just gonna hold the dataframes
"""
from typing import Dict

from pandas import DataFrame, concat

from budget_report_generator.budget import Budget

my_budget = Budget()
spend_per_day = my_budget.spend_per_day
savings = my_budget.savings
savings_per_day = my_budget.savings / 30.5


class Report:
    wallet_spent: float = 0
    summary: dict = {}
    total_spent: float = 0
    excluded_categories = ['known expenses', 'big purchases']

    def __init__(self, data: Dict[str, DataFrame], date_range):
        self.data = data
        self.date_range = date_range.days
        self.categories = list(data.keys())

        self.summarize_report()

    def summarize_report(self):
        category_summary = self._summarize_category_data()
        self._summarize_spending(category_summary)

        self.summary['categories'] = category_summary

    def get_all_transactions(self):
        all_transactions = DataFrame()
        for name, subreport in self.data.items():
            all_transactions = concat(
                (all_transactions, subreport),
                ignore_index=True
            )

        return all_transactions

    def get_known_transactions(self):
        return self.data['Known Expenses']

    def _summarize_category_data(self):
        print_data = {}
        for name, subreport in self.data.items():
            subreport_total = subreport.amount.sum()
            print_data[name] = subreport_total
            if name.lower() not in self.excluded_categories:
                self.wallet_spent += subreport_total
            self.total_spent += subreport_total

        return print_data

    def _summarize_spending(self, category_summary):
        self.total_spent += my_budget.rent
        self.total_spent_per_day = self.total_spent / self.date_range
        self.available = spend_per_day * self.date_range
        self.wallet_remaining = self.available - self.wallet_spent
        self.current_savings = savings_per_day * self.date_range \
            + self.wallet_remaining
        self.wallet_spend_per_day = (
                (self.available - self.wallet_remaining) / self.date_range
        )
        self.known_spend_per_day = (
                category_summary['Known Expenses'] / self.date_range
        )

        self.expected_savings = (
                my_budget.savings
                + (self.available - self.wallet_spend_per_day * 30.5)
                + (my_budget.expected - self.known_spend_per_day * 30.5)
        )

    @staticmethod
    def _print_summary(summary):
        for key, value in summary.items():
            print(f'{key}: ${round(value, 2)}')

    def _get_spending_config_data(self):
        pass  # pragma: no cover
