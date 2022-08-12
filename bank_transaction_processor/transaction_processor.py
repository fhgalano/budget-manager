"""
translates and writes transaction data to the db
"""
from os import getenv
import logging
from pathlib import Path
from typing import Tuple

from sqlite3 import connect, version, Error, Connection, Cursor
from pandas import read_csv, DataFrame, Series
from dotenv import load_dotenv

from definitions import ROOT_DIR

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
        try:
            self.db_connection = connect(self.db_file)
            print(version)
        except Error as e:
            logger.warning("SQLite database connection failed: ", e)

    def close_db_connection(self):
        self.db_connection.close()

    def process_transactions(self):
        for transaction in self.transaction_data.iterrows():
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

        possible_categories = self._run_sql_query(sql, bank_category).fetchall()
        # I don't


    @staticmethod
    def _convert_transaction_csv_to_dataframe(
            transaction_csv: str
    ) -> DataFrame:
        return read_csv(transaction_csv)

    @staticmethod
    def _transaction_is_sale(self, transaction: Series) -> bool:
        raise NotImplementedError


def _get_database_path():
    env_path = ROOT_DIR / '.env'
    load_dotenv(env_path)
    return getenv('DB_URL')
