from budgetdb_communication_layer.sql_runner import Runner
from utils import get_database_path


def write_transaction_category_to_db(common_name, budget_category):
    runner = Runner(get_database_path('DB_URL'))
    runner.open_db_connection()

    sql = '''INSERT INTO `transaction-category`
        (`common-name`, `budget-category`)
        VALUES
        (?,?)'''

    cursor = runner._run_sql_query(sql, [common_name, budget_category])
    stuff = cursor.fetchall()
    runner.db_connection.commit()
    print("wrote new transaction category ", common_name, budget_category)


def write_known_expense_to_db(common_name, budget_category, cost):
    runner = Runner(get_database_path('DB_URL'))
    runner.open_db_connection()

    sql = '''INSERT INTO `known-transactions`
        (`common-name`, `budget-category`, `expected-cost`)
        VALUES
        (?,?,?)'''

    cursor = runner._run_sql_query(
        sql,
        [common_name, budget_category, cost]
    )
    stuff = cursor.fetchall()
    runner.db_connection.commit()
    print("Added new expense ", common_name, budget_category, cost)
