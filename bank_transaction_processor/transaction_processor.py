"""
translates and writes transaction data to the db
"""
import logging
from pathlib import Path
from typing import Tuple

from sqlite3 import Connection
from pandas import read_csv, DataFrame, Series

from budgetdb_communication_layer.sql_runner import Runner
from definitions import SYMBOLS, SELLER_NAME_MAP, POINT_OF_SALE

logger = logging.getLogger(__name__)


class Processor(Runner):
    transaction_data: DataFrame
    db_connection: Connection
    db_file: Path

    def __init__(
            self,
            db_file,
            transaction_csv
    ):
        self.db_file = db_file
        self.transaction_data = self._convert_transaction_csv_to_dataframe(
            transaction_csv)
        self.db_connection = None

    def process_transactions(self):
        for idx, transaction in self.transaction_data.iterrows():
            if self._transaction_is_sale(transaction):
                transaction_tuple = self.format_transaction_for_db(transaction)
                self.insert_transaction(transaction_tuple)

    def format_transaction_for_db(self, transaction: Series) -> Tuple:
        raise NotImplementedError  # pragma: no cover

    def insert_transaction(self, transaction: Tuple):
        sql = '''INSERT INTO transactions
        (date, seller, `bank-category`, `budget-category`, amount)
        VALUES
        (?,?,?,?,?)'''

        self._run_sql_query(sql, transaction)

        self.db_connection.commit()

    def reprocess_budget_category(self):
        get_data_sql = '''
            SELECT
                seller,
                `budget-category`
            FROM transactions
        '''
        transaction_data = self._run_sql_query(get_data_sql).fetchall()
        # iterate through data
        category_reprocessed_cache = []
        for transaction in transaction_data:
            seller = transaction[0]
            budget_category = transaction[1]
            if seller not in category_reprocessed_cache:
                new_budget_category = self._get_budget_category(
                    seller
                )
                if new_budget_category != budget_category:
                    replace_sql = '''
                        UPDATE transactions
                        SET `budget-category` = (?)
                        WHERE seller = (?)
                    '''
                    self._run_sql_query(
                        replace_sql,
                        (new_budget_category,
                        seller)
                    )

                    self.db_connection.commit()

    def _get_budget_category(self, seller):
        sql = '''SELECT * FROM `transaction-category` WHERE
        `common-name`=(?)'''

        possible_categories = (
            self._run_sql_query(sql, (seller,))
            .fetchall()
        )

        if not possible_categories:
            category = "Unknown"
        elif len(possible_categories) == 1:
            category = possible_categories[0][1]
        else:
            category = "Multiple"

        return category

        # need method to pick a category if multiple

    @staticmethod
    def _convert_transaction_csv_to_dataframe(
            transaction_csv: str
    ) -> DataFrame:
        return read_csv(transaction_csv)

    @staticmethod
    def _transaction_is_sale(self, transaction: Series) -> bool:
        raise NotImplementedError  # pragma: no cover

    def _clean_up_seller_name(self, category: str):
        category.strip()
        category_name, corner_case_is_applied = (
            self._category_name_corner_case(category)
        )
        if not corner_case_is_applied:
            for sym in SYMBOLS:
                category = category.replace(sym, ' ')

            words = category.split(' ')
            words = [word for word in words if word]  # removes empty items

            words_to_remove = []
            for word in words:
                if word.isnumeric() or self._is_point_of_sale_method(word):
                    words_to_remove.append(word)

            words = [i for i in words if i not in words_to_remove]

            category_name = ' '.join(words)

        return category_name

    @staticmethod
    def _category_name_corner_case(category: str):
        category_name = None
        category_is_overwritten = False
        for key, val in SELLER_NAME_MAP.items():
            if key in category.lower():
                category_name = val
                category_is_overwritten = True

        return category_name, category_is_overwritten

    @staticmethod
    def _is_point_of_sale_method(word: str):
        if word.lower() in POINT_OF_SALE:
            return True
        else:
            return False
