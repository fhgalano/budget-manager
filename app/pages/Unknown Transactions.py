import streamlit as st

from definitions import CATEGORIES
from database_interaction_tools.database_interaction_tools import write_transaction_category_to_db


class UnknownTransaction:
    def __init__(self, seller, bank_category, new_category):
        self.seller = seller
        self.bank_category = bank_category
        self.new_category = new_category

report = st.session_state.get('report')

st.title("Complete Unknown Transactions")

if report is None:
    st.error("No Report Available")
    st.info("Run a report on the Overview page")

else:
    try:
        unknown = report.data.get('Unknown').copy()
    except:
        unknown = None

    if unknown is None or unknown.empty:
        st.info('No Unknown Transactions in this Report')
    else:
        unknown
        unknown.drop(['date', 'amount'], axis='columns', inplace=True)
        unknown.drop_duplicates(inplace=True)
        updated_transactions = []
        with st.form(key='Transactions', clear_on_submit=True):
            button = st.form_submit_button('Save Updated Categories')

            c1, c2, c3 = st.columns(3)
            c1.write('**Seller**')
            c2.write('**Bank Category**')
            c3.write('**Category**')
            key = 0
            for idx, row in unknown.head(10).iterrows():
                c1, c2, c3 = st.columns(3)
                c1.write(row['seller'])
                c2.write(row['bank-category'])
                row['updated_category'] = c3.selectbox(
                    label='Category',
                    options=CATEGORIES,
                    key=key,
                    label_visibility='collapsed',
                )
                st.markdown('---')
                key += 1

                updated_transactions.append(
                    UnknownTransaction(
                        row['seller'],
                        row['bank-category'],
                        row['updated_category']
                    )
                )

        if button:
            for i in updated_transactions:
                if i.new_category is not None:
                    write_transaction_category_to_db(
                        i.seller,
                        i.new_category
                    )

                    # remove from unknown
                    r = st.session_state.get('report')
                    a = r.data.get('Unknown')
                    a = a[
                        (a['seller'] != i.seller)
                        & (a['bank-category'] != i.bank_category)
                    ]

                    r.data['Unknown'] = a

            st.experimental_rerun()


