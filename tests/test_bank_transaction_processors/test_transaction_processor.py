import pytest
import os

from dotenv import load_dotenv
from pandas import read_csv
from sqlite3 import Error

from bank_transaction_processor.transaction_processor import Processor
from definitions import ROOT_DIR, TEST_RESOURCE_DIR

env_path = ROOT_DIR / '.env'
load_dotenv(env_path)


@pytest.fixture
def processor():
    return Processor(
        os.getenv('DB_URL'),
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
    try:
        fake_processor.open_db_connection()
    except Error as e:
        print(f"successfully caught error: {e}")
        assert True

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


