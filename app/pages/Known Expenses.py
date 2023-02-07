import streamlit as st

from definitions import CATEGORIES
from database_interaction_tools.database_interaction_tools \
    import write_known_expense_to_db


report = st.session_state.get('report')

report.categories

st.title("Manage Pre-Budgeted Expenses")

if report is None:
    st.error("No Report Available")
    st.info("Run a report on the Overview page")

else:
    try:
        st.write(report.get_known_transactions())
        all_transactions = report.get_all_transactions()
    except:
        all_transactions = None

    if all_transactions is None or all_transactions.empty:
        st.info('No Transactions in this Report')
    else:
        all_transactions

        with st.form(key='add_expense', clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            name = c1.selectbox(
                'Seller Name',
                options=all_transactions['seller'].unique())
            category = c2.selectbox(
                label='Category',
                options=CATEGORIES,
            )
            amount = c3.number_input(
                'Expected Cost',
                step=5.0,
            )
            submit = c4.form_submit_button('Add Expense')

        if submit:
            if None not in [name, category] and amount > 0:
                write_known_expense_to_db(
                    name,
                    category,
                    amount
                )
            else:
                st.error('Invalid Transaction')


