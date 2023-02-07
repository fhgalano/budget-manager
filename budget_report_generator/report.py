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
    total: float = 0
    summary: dict
    raw_total: float = 0

    def __init__(self, data: Dict[str, DataFrame], date_range):
        self.data = data
        self.date_range = date_range.days
        self.categories = list(data.keys())

        self.summarize_report()

    def summarize_report(self):
        category_summary = self._summarize_category_data()
        spend_summary = self._summarize_spending(category_summary)

        print('\n----Categories----')
        self._print_summary(category_summary)
        print("\n----Summary----")
        self._print_summary(spend_summary)

        spend_summary['categories'] = category_summary

        self.summary = spend_summary

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
            print(name.lower())
            if name.lower() not in ['known expenses', 'big purchases']:
                self.total += subreport_total
                print('skipped')
            self.raw_total += subreport_total

        return print_data

    def _summarize_spending(self, category_summary):
        # TODO: This needs to be upgraded to use other budgeting tools.
        #  For now it's just a constant
        summary = {}
        available = spend_per_day * self.date_range
        summary['raw_spent'] = self.raw_total
        summary['spent'] = self.total
        summary['remaining'] = available - self.total
        summary['savings'] = savings_per_day * self.date_range + summary['remaining']
        # ASPD = Actual Spend Per Day
        summary['ASPD'] = (
                (available - summary['remaining']) / self.date_range
        )
        summary['PBSR'] = category_summary['Known Expenses'] / self.date_range

        return summary

    @staticmethod
    def _print_summary(summary):
        for key, value in summary.items():
            print(f'{key}: ${round(value,2)}')

    def _get_spending_config_data(self):
        pass  # pragma: no cover
