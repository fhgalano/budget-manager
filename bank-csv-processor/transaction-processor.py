"""
translates and writes transaction data to the db
"""
from os import getenv
import logging
from pathlib import Path
from typing import Tuple

from sqlite3 import connect, version, Error, Connection
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
        self.transaction_data = self.convert_transaction_csv_to_dataframe(
            transaction_csv
        )
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
            transaction_tuple = self.format_transaction_for_db(transaction)
            self.upsert_transaction(transaction_tuple)

    def format_transaction_for_db(self, transaction: Series):
        raise NotImplementedError

    def upsert_transaction(self, transaction: Tuple):
        sql = '''INSERT INTO transactions
        (date, seller, bank-category,budget-category, amount)
        VALUES
        (?,?,?,?,?)'''

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(sql, transaction)
            self.db_connection.commit()
        except Error as e:
            logger.warning(e)

    @staticmethod
    def convert_transaction_csv_to_dataframe(
            transaction_csv: str
    ) -> DataFrame:
        return read_csv(transaction_csv)


def _get_database_path():
    env_path = ROOT_DIR / '.env'
    load_dotenv(env_path)
    return getenv('DB_URL')
