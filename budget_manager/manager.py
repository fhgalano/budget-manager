from os import listdir
from os.path import isfile

import logging
import datetime

import argparse
import dateutil.relativedelta
from pathlib import Path


from budget_report_generator.report_generator import ReportGenerator
from bank_transaction_processor.transaction_loader import TransactionLoader
from definitions import CYCLE_DATE, PROCESSED_FILE_DIR


logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog='Budget DB Manager',
    description='enables transactions to be processed and reports to be'
                'generated through the budgetDB',
    epilog='deez nuts'
)
parser.add_argument('-pt', '--process-transactions', action='store_true')
parser.add_argument('-cr', '--current-report', action='store_true')


def _get_time_delta_for_current_cycle(date):
    if date.day > CYCLE_DATE:
        delta = dateutil.relativedelta.relativedelta(
            days=date.day - CYCLE_DATE
        )
    else:
        delta = dateutil.relativedelta.relativedelta(
            days=date.day - CYCLE_DATE,
            months=1
        )

    return delta


def _get_all_files_in_dir(path: Path):
    all_files_and_dirs = listdir(path)
    all_files = [file for file in listdir(path)
                 if isfile(path / file)]

    all_files.remove('cache')

    all_files = [str(path / file) for file in all_files]

    return all_files


def run_report_for_date(date=datetime.datetime.today(), pending: float = 0):
    # get report for this month starting from given day
    time_delta = _get_time_delta_for_current_cycle(date)
    print(date)
    print(time_delta)
    report = ReportGenerator().generate_report(
        year=date.year,
        month=date.month,
        day=date.day,
        time_range=time_delta,
        pending=pending,
    )

    return report


def load_new_transactions_to_db(filepath=PROCESSED_FILE_DIR, db='DB_URL'):
    # get list of files in dir
    path = Path(filepath)
    files = _get_all_files_in_dir(path)

    loader = TransactionLoader(db=db)
    loader.process_files(files)


def get_unknown_transactions():
    pass


if __name__ == "__main__":
    args = parser.parse_args()
    if args.process_transactions:
        print('Loading New Transactions...')
        load_new_transactions_to_db()
    if args.current_report:
        print('Running Report...')
        r = run_report_for_date(date=datetime.datetime(day=24, month=2, year=2023))

    print('done')
