import pytest

from pandas import read_csv

from definitions import ROOT_DIR, TEST_RESOURCE_DIR
from bank_transaction_processor.discover_processor import DiscoverProcessor
from utils import get_database_path


@pytest.fixture()
def transaction_df():
    df = read_csv(TEST_RESOURCE_DIR / 'discover_test_transactions.csv')
    return df[df.Category != 'Payments and Credits']


@pytest.fixture()
def processor():
    return DiscoverProcessor(
        get_database_path('TEST_DB_URL'),
        ROOT_DIR / 'tests/resources/discover_test_transactions.csv'
    )


def test_process_transactions(processor, transaction_df):
    processor.open_db_connection()
    _delete_all_table_entries(processor)
    processor.process_transactions()

    rows_in_transactions_table = _number_of_rows_in_transactions_table(
        processor.db_connection.cursor()
    )
    assert rows_in_transactions_table == transaction_df.shape[0]


def test_processing_duplicate_transactions(processor, transaction_df):
    processor.open_db_connection()
    _delete_all_table_entries(processor)
    processor.process_transactions()
    processor.process_transactions()

    rows_in_transactions_table = _number_of_rows_in_transactions_table(
        processor.db_connection.cursor()
    )
    assert rows_in_transactions_table == transaction_df.shape[0]


def _delete_all_table_entries(conn_processor: DiscoverProcessor):
    cursor = conn_processor.db_connection.cursor()
    cursor.execute('DELETE FROM transactions;')
    print(f"deleted {cursor.rowcount} entries")
    conn_processor.db_connection.commit()


def _number_of_rows_in_transactions_table(cursor):
    cursor.execute('SELECT COUNT(*) FROM transactions')
    results = cursor.fetchall()

    return results[0][0]
