import datetime

import dateutil.relativedelta
import pytest

from budget_report_generator.report_generator import ReportGenerator
from utils import get_database_path


@pytest.fixture
def report_generator():
    return ReportGenerator(db_file=get_database_path('TEST_DB_URL'))


def test_generate_report_with_defaults(report_generator):
    start_date = datetime.date(2022, 7, 22)
    time_delta = dateutil.relativedelta.relativedelta(months=2)

    report = report_generator.generate_report(
        year=2022,
        month=7,
        day_cycles_on=22,
        time_range=time_delta
    )
    pass
