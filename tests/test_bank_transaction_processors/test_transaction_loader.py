import os
import pytest
import json
import logging

from definitions import TEST_RESOURCE_DIR
from bank_transaction_processor.transaction_loader import TransactionLoader
from bank_transaction_processor.discover_processor import DiscoverProcessor
from bank_transaction_processor.chase_processor import ChaseProcessor

LOGGER = logging.getLogger(__name__)


@pytest.fixture()
def loader():
    return TransactionLoader(
        cache_path=TEST_RESOURCE_DIR / 'cache',
        db='TEST_DB_URL'
    )


def test_attempt_to_process_cached_file(loader, caplog):
    loader._add_file_to_cache('test_file')
    loader._write_cache()
    LOGGER.info('Starting process_cached_file test')
    with caplog.at_level(logging.DEBUG):
        loader.process_files(['test_file'])
    assert 'file test_file already processed' in caplog.text


def test_add_file_to_cache(loader):
    _delete_cache()
    loader._add_file_to_cache('test_file')
    loader._write_cache()

    cache = json.loads((TEST_RESOURCE_DIR / 'cache').open().read())

    assert 'test_file' in cache


def test_get_correct_chase_processor(loader):
    processor = loader._get_correct_processor(
        str(TEST_RESOURCE_DIR / 'chase_test_transactions.csv')
    )

    assert type(processor) == ChaseProcessor


def test_get_correct_discover_processor(loader):
    processor = loader._get_correct_processor(
        str(TEST_RESOURCE_DIR / 'discover_test_transactions.csv')
    )

    assert type(processor) == DiscoverProcessor


def _delete_cache():
    open(TEST_RESOURCE_DIR / 'cache', 'w').close()
