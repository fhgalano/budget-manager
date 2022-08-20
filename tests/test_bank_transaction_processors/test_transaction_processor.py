import pytest

import string
import random

from pandas import read_csv
from sqlite3 import Error

from bank_transaction_processor.transaction_processor import Processor
from definitions import ROOT_DIR, TEST_RESOURCE_DIR
from utils import get_database_path


@pytest.fixture
def processor():
    return Processor(
        get_database_path('TEST_DB_URL'),
        ROOT_DIR / 'tests/resources/test_transactions.csv'
    )


@pytest.fixture
def fake_processor():
    return Processor(
        'fake_url',
        ROOT_DIR / 'tests/resources/test_transactions.csv'
    )


@pytest.fixture()
def transaction_df():
    return read_csv(TEST_RESOURCE_DIR / 'test_transactions.csv')


def test_open_db(processor, fake_processor):
    processor.open_db_connection()
    with pytest.raises(Error):
        fake_processor.open_db_connection()

    assert processor.db_connection is not None
    assert fake_processor.db_connection is None


def test_close_db(processor):
    processor.open_db_connection()
    processor.close_db_connection()

    assert processor.db_connection is None


def test_get_budget_category():
    # TODO: Finish
    pass


def test_clean_up_seller_name(processor, transaction_df):
    test_cases = transaction_df.Description.tolist()

    # TODO: Make the test have an actual assert
    for seller_name in test_cases:
        print(processor._clean_up_seller_name(seller_name))


def test_reprocess_transactions(processor):
    processor.open_db_connection()

    # Generate random category
    letters = string.ascii_uppercase
    category = ''.join(random.choice(letters) for i in range(6))

    # Change some categories
    processor._run_sql_query('''
    INSERT INTO `transaction-category` (`common-name`, `budget-category`)
    VALUES ('TABLE22 NY', ?)
    ''', [category])
    processor.db_connection.commit()

    # Reprocess
    processor.reprocess_budget_category()

    # Check that the change was captured
    changed_transaction = processor._run_sql_query('''
    SELECT * FROM transactions
    WHERE seller = 'TABLE22 NY'    
    ''').fetchall()

    new_category = changed_transaction[0][3]

    # delete changes
    processor._run_sql_query('''DELETE FROM `transaction-category`;''')
    processor.db_connection.commit()

    assert new_category == category
