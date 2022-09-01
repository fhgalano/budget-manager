from os.path import exists
import logging
from pathlib import Path

from sqlite3 import connect, version, Error, Connection, Cursor
from pandas import DataFrame

logger = logging.getLogger(__name__)


class Runner:
    db_connection: Connection
    db_file: Path

    def __init__(
            self,
            db_file
    ):
        self.db_file = db_file
        self.db_connection = None

    def open_db_connection(self):
        if db_file_exists(self.db_file):
            try:
                self.db_connection = connect(self.db_file)
                print(version)
            except Error as e:  # pragma: no cover
                logger.warning("SQLite database connection failed: ", e)

    def close_db_connection(self):
        self.db_connection.close()
        self.db_connection = None

    def _run_sql_query(self, query, *options) -> Cursor:
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, *options)
        except Error as e:  # pragma: no cover
            logger.warning(f"{e}, {options}")

        return cursor


def db_file_exists(db_file: Path) -> bool:
    if not exists(db_file):
        logger.warning(f"db file, {db_file}, does not exist")
        raise Error("db does not exist at specified path")

    return True
