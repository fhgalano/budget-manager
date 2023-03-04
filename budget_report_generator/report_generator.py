from datetime import date
from typing import List

import pandas
from dateutil.relativedelta import relativedelta

from budgetdb_communication_layer.sql_runner import Runner, db_file_exists
from .report import Report
from utils import get_database_path
from definitions import CYCLE_DATE, EXPECTED_COST_TOLERANCE


class ReportGenerator(Runner):
    report = None

    def __init__(
            self,
            db_file=get_database_path('DB_URL'),
    ):
        self.db_file = db_file
        self.open_db_connection()

    def generate_report(self,
                        year=date.today().year,
                        month=date.today().month,
                        day=date.today().day,
                        time_range: relativedelta = relativedelta(months=1),
                        pending: float = 0,
                        ):
        # Parse date range with defaults setup
        end_date = date(year, month, day)
        start_date = end_date - time_range
        date_range = end_date - start_date
        # TODO: make the date range more customizable

        transactions = self._get_transactions_in_date_range(
            start_date, end_date
        )
        transactions, known_transactions = self._filter_known_transactions(
            transactions
        )

        # get all budget categories (lol not needed)
        report_categories = self._get_budget_categories()

        # add transaction category column
        transactions = self._insert_transaction_categories(transactions)

        # split transactions by category
        category_report_data = self._split_transactions_by_category(
            transactions
        )
        category_report_data = self._add_known_transactions_to_data(
            category_report_data, known_transactions
        )

        # create the report
        self.report = Report(category_report_data, date_range, pending=pending)

        return self.report

    def _get_transactions_in_date_range(self, start_date, end_date) -> pandas.DataFrame:
        # get the data from the date range
        date_range_query = '''
                SELECT * FROM transactions
                WHERE
                    DATE(date) > DATE(?) AND DATE(date) <= DATE(?)
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
        ).iloc[:, :5].dropna(how='all')

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

        known_transactions = self._query_to_df__keep_column_names(cursor)

        return known_transactions

    def _get_budget_categories(self) -> List:
        budget_category_query = '''
            SELECT DISTINCT * FROM `transaction-category`
        '''

        cursor = self._run_sql_query(budget_category_query)

        return self._query_to_df__keep_column_names(cursor)

    def _insert_transaction_categories(self, transactions):
        categorized_transactions = (
            self._get_budget_categories()
            .set_index('common-name')
            .to_dict()['budget-category']
        )
        if not transactions.empty:
            transactions['budget-category'] = transactions.apply(
                lambda row: categorized_transactions.get(row['seller'], 'Unknown'),
                axis=1
            )

        return transactions

    def _split_transactions_by_category(self, transactions: pandas.DataFrame):
        categories = transactions['budget-category'].unique()
        category_report_data = {}
        for category in categories:
            category_report_data[category] = (
                transactions.where(transactions['budget-category'] == category)
                .dropna(how='all')
                .reset_index(drop=True)
            )

        return category_report_data

    def _query_to_df__keep_column_names(self, cursor):
        column_names = self._get_column_names_from_cursor(cursor)
        return pandas.DataFrame(cursor.fetchall(), columns=column_names)

    def _add_known_transactions_to_data(self, category_data, known_data):
        category_data['Known Expenses'] = known_data
        return category_data


    @staticmethod
    def _get_column_names_from_cursor(cursor):
        return list(map(lambda x: x[0], cursor.description))


