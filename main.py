from os import listdir
from os.path import isfile

import logging
import datetime

import dateutil.relativedelta
from pathlib import Path


from budget_report_generator.report_generator import ReportGenerator
from bank_transaction_processor.transaction_loader import TransactionLoader
from definitions import CYCLE_DATE, PROCESSED_FILE_DIR


logger = logging.getLogger(__name__)


def _get_time_delta_for_current_cycle():
    today = datetime.datetime.today()
    if today.day >= CYCLE_DATE:
        delta = dateutil.relativedelta.relativedelta(
            days=today.day - CYCLE_DATE
        )
    else:
        delta = dateutil.relativedelta.relativedelta(
            days=today.day - CYCLE_DATE,
            months=1
        )

    return delta


def _get_all_files_in_dir(path: Path):
    all_files_and_dirs = listdir(path)
    all_files = [file for file in listdir(path)
                 if isfile(path / file)]

    return all_files


def run_report_for_this_month():
    # get report for this month starting from today
    time_delta = _get_time_delta_for_current_cycle()

    report = ReportGenerator().generate_report(
        time_range=time_delta
    )

    return report


def load_new_transactions_to_db():
    # get list of files in dir
    path = Path('./transactions/')
    files = _get_all_files_in_dir(path)

    loader = TransactionLoader()
    loader.process_files(files)


if __name__ == "__main__":
    load_new_transactions_to_db()
    print('done')
