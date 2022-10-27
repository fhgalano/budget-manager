import datetime
import json
import logging

from datetime import datetime
from bank_transaction_processor.chase_processor import ChaseProcessor
from bank_transaction_processor.discover_processor import DiscoverProcessor
from definitions import PROCESSED_FILE_DIR

from utils import get_database_path

logger = logging.getLogger(__name__)


class TransactionLoader:
    cache: dict
    _db: str

    def __init__(
            self,
            cache=json.loads(PROCESSED_FILE_DIR / 'cache'),
            db='DB_URL'
    ):
        self._db = db
        self.cache = cache

    def process_files(self, files: list):
        for file in files:
            if file in self.cache:
                logger.debug(f'file {file} already processed')
            else:
                self._process_file_with_correct_processor(file)
                self._add_file_to_cache(file)

    def _process_file_with_correct_processor(self, file: str):
        processor = self._get_correct_processor(file)
        processor.open_db_connection()
        processor.process_transactions()

    def _add_file_to_cache(self, file: str):
        self.cache.update(
            {file, datetime.now.strftime("%m/%d/%Y, %H:%M:%S")}
        )

    def _get_correct_processor(self, file: str):
        if 'chase' in file.lower():
            processor = ChaseProcessor(get_database_path(self._db), file)
        elif 'discover' in file.lower():
            processor = DiscoverProcessor(get_database_path(self._db), file)

        return processor
