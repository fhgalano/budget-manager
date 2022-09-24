from datetime import date
from typing import List

import pandas
from dateutil.relativedelta import relativedelta

from budgetdb_communication_layer.sql_runner import Runner, db_file_exists
from utils import get_database_path
from definitions import CYCLE_DATE, EXPECTED_COST_TOLERANCE


class ReportGenerator(Runner):
    def __init__(
            self,
            # time_range: relativedelta,
            db_file=get_database_path('DB_URL'),
    ):
        self.db_file = db_file

        self.open_db_connection()

    def generate_report(self,
                        year=date.today().year,
                        month=date.today().month,
                        day_cycles_on: int = CYCLE_DATE,
                        time_range: relativedelta = relativedelta(months=1),
                        ):
        # Parse date range with defaults setup
        end_date = date(year, month, day_cycles_on)
        start_date = end_date - time_range
        # TODO: make the date range more customizable

        transactions = self._get_transactions_in_date_range(
            start_date, end_date
        )
        transactions, known_transactions = self._filter_known_transactions(
            transactions
        )

        # get all budget categories
        report_categories = self._get_budget_categories()
        # split transactions into multiple categorized tables

        print('end')

        pass

    def _get_transactions_in_date_range(self, start_date, end_date) -> pandas.DataFrame:
        # get the data from the date range
        date_range_query = '''
                SELECT * FROM transactions
                WHERE
                    DATE(date) BETWEEN DATE(?) AND DATE(?)
                '''

        cursor = self._run_sql_query(
            date_range_query, (start_date, end_date)
        )
        column_names = self._get_column_names_from_cursor(cursor)
        applicable_transactions = cursor.fetchall()

        return pandas.DataFrame(applicable_transactions, columns=column_names)

    def _filter_known_transactions(self, transactions):
        # grab data from the known transactions
        known_transactions = self._get_known_transactions()

        # filter out known transactions from data in date range
        name_matched_transactions = pandas.merge(
            transactions, known_transactions,
            how='inner',
            left_on='seller',
            right_on='common-name',
            suffixes=[None, '_y']
        )

        cost_matched_transactions = name_matched_transactions.where(
            (name_matched_transactions['amount'] - name_matched_transactions[
                'expected-cost'])
            < name_matched_transactions[
                'expected-cost'] * EXPECTED_COST_TOLERANCE
        ).iloc[:, :5]

        filtered_transactions = pandas.concat(
            [transactions, cost_matched_transactions]
        ).drop_duplicates(keep=False)

        return filtered_transactions, cost_matched_transactions

    def _get_known_transactions(self) -> pandas.DataFrame:
        known_transactions_query = '''
            SELECT * FROM `known-transactions`
        '''
        cursor = self._run_sql_query(
            known_transactions_query
        )
        column_names = self._get_column_names_from_cursor(cursor)

        return pandas.DataFrame(cursor.fetchall(), columns=column_names)

    def _get_budget_categories(self) -> List:
        budget_category_query = '''
            SELECT DISTINCT `budget-category` FROM `transaction-category`
        '''

        return self._run_sql_query(budget_category_query).fetchall()

    @staticmethod
    def _get_column_names_from_cursor(cursor):
        return list(map(lambda x: x[0], cursor.description))
