"""
Basically this will allow for further visualization to be applied to the
report. For now this is just gonna hold the dataframes
"""
from typing import Dict

from pandas import DataFrame

spend_per_day = 38.15
savings = 1000


class Report:
    total: float = 0

    def __init__(self, data: Dict[str, DataFrame], date_range):
        self.data = data
        self.date_range = date_range.days
        self.categories = list(data.keys())

    def create_report(self):
        category_summary = self._summarize_category_data()
        spend_summary = self._summarize_spending(category_summary)

        print('\n----Categories----')
        self._print_summary(category_summary)
        print("\n----Summary----")
        self._print_summary(spend_summary)

        return spend_summary

    def _summarize_category_data(self):
        print_data = {}
        for name, subreport in self.data.items():
            subreport_total = subreport.amount.sum()
            print_data[name] = subreport_total
            if 'known expenses' not in name.lower():
                self.total += subreport_total

        return print_data

    def _summarize_spending(self, category_summary):
        # TODO: This needs to be upgraded to use other budgeting tools.
        #  For now it's just a constant
        summary = {}
        available = spend_per_day * self.date_range
        summary['spent'] = self.total
        summary['remaining'] = available - self.total
        summary['savings'] = savings + summary['remaining']
        # ASPD = Actual Spend Per Day
        summary['ASPD'] = (
                (available - summary['remaining']) / self.date_range
        )

        return summary

    @staticmethod
    def _print_summary(summary):
        for key, value in summary.items():
            print(f'{key}: ${round(value,2)}')

    def _get_spending_config_data(self):
        pass  # pragma: no cover
