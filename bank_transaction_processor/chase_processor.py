from bank_transaction_processor.transaction_processor import Processor
from pandas import Series
from typing import Tuple


class ChaseProcessor(Processor):
    def format_transaction_for_db(self, transaction: Series) -> Tuple:
        """
        Tuple must match format:
        (date, seller, bank-category, budget-category, amount)
        :param transaction:
        :return: Tuple
        """
        date = transaction['Transaction Date']
        seller = self._clean_up_seller_name(transaction['Description'])
        bank_category = transaction['Category']
        budget_category = self._get_budget_category(seller)
        amount = self._process_amount_signage(transaction['Amount'])

        return date, seller, bank_category, budget_category, amount

    @staticmethod
    def _process_amount_signage(amount):
        return abs(amount)

    @staticmethod
    def _transaction_is_sale(transaction: Series) -> bool:
        if transaction['Type'] == 'Sale':
            transaction_type = True
        else:
            transaction_type = False

        return transaction_type
