from datetime import date
from dateutil.relativedelta import relativedelta

from budgetdb_communication_layer.sql_runner import Runner, db_file_exists
from utils import get_database_path
from definitions import CYCLE_DATE


class ReportGenerator(Runner):
    def __init__(
            self,
            time_range: relativedelta,
            db_file=get_database_path(),
    ):
        if db_file_exists(db_file):
            self.open_db_connection()

    def generate_report(self,
                        year=date.today().year,
                        month=date.today().month,
                        day_cycles_on: int = CYCLE_DATE,
                        time_range: relativedelta = relativedelta(months=1),
                        ):
        # Parse date range with defaults setup
        end_date = date(year, month, day_cycles_on)
        start_date = end_date - relativedelta(months=1)
        # TODO: make the date range more customizable

        # get the data from the date range
        date_range_query = '''
        SELECT * FROM transactions
        WHERE
            
        '''
        # grab data from the known transactions
        # filter out known transactions from data in date range
        # get all budget categories
        # split transactions into multiple categorized tables

        pass
