#import pytest
import os
from os import getenv
from dotenv import load_dotenv

from bank_transaction_processor.transaction_processor import Processor
from definitions import ROOT_DIR

env_path = ROOT_DIR / '.env'
load_dotenv(env_path)

#@pytest.fixture
def processor():
    return Processor(
        os.getenv('DB_URL'),
        ROOT_DIR / 'tests/resources/test_transactions.csv'
    )

def fake_processor():
    return Processor(
        'fake_url',
        ROOT_DIR / 'tests/resources/test_transactions.csv'
    )


def test_open_db(processor, fake_processor):
    processor.open_db_connection()
    fake_processor.open_db_connection()
    #TODO: The connection creates an empty db when given a url that doesn't exist

    assert processor.db_connection is not None
    assert fake_processor.db_connection is None


if __name__ == '__main__':
    test_open_db(processor(), fake_processor())

