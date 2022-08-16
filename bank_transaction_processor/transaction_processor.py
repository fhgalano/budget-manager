"""
translates and writes transaction data to the db
"""
from os import getenv
from os.path import exists
import logging
from pathlib import Path
from typing import Tuple

from sqlite3 import connect, version, Error, Connection, Cursor
from pandas import read_csv, DataFrame, Series
from dotenv import load_dotenv

from definitions import ROOT_DIR, SYMBOLS, SELLER_NAME_MAP, POINT_OF_SALE

logger = logging.getLogger(__name__)


class Processor:
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

    def open_db_connection(self):
        if _db_file_exists(self.db_file):
            try:
                self.db_connection = connect(self.db_file)
                print(version)
            except Error as e:
                logger.warning("SQLite database connection failed: ", e)

    def close_db_connection(self):
        self.db_connection.close()
        self.db_connection = None

    def process_transactions(self):
        for idx, transaction in self.transaction_data.iterrows():
            if self._transaction_is_sale(transaction):
                transaction_tuple = self.format_transaction_for_db(transaction)
                self.upsert_transaction(transaction_tuple)

    def format_transaction_for_db(self, transaction: Series) -> Tuple:
        raise NotImplementedError

    def upsert_transaction(self, transaction: Tuple):
        sql = '''INSERT INTO transactions
        (date, seller, bank-category, budget-category, amount)
        VALUES
        (?,?,?,?,?)'''

        self._run_sql_query(sql, transaction)

        self.db_connection.commit()

    def _run_sql_query(self, query, options) -> Cursor:
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, options)
        except Error as e:
            logger.warning(e)

        return cursor

    def _get_budget_category(self, bank_category):
        sql = '''SELECT * FROM transaction-category WHERE
        bank-category=?'''

        possible_categories = (
            self._run_sql_query(sql, bank_category)
            .fetchall()
        )

        # need method to pick a category if multiple

    @staticmethod
    def _convert_transaction_csv_to_dataframe(
            transaction_csv: str
    ) -> DataFrame:
        return read_csv(transaction_csv)

    @staticmethod
    def _transaction_is_sale(self, transaction: Series) -> bool:
        raise NotImplementedError

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


def _get_database_path():
    env_path = ROOT_DIR / '.env'
    load_dotenv(env_path)
    return getenv('DB_URL')


def _db_file_exists(db_file: Path) -> bool:
    if not exists(db_file):
        logger.warning(f"db file, {db_file}, does not exist")
        raise Error("db does not exist at specified path")

    return True
