import streamlit as st


def show_transactions(name):
    if name == 'All':
        st.dataframe(report.get_all_transactions(), use_container_width=True)
    else:
        st.dataframe(report.data[name], use_container_width=True)


st.title("Manage Pre-Budgeted Expenses")

report = st.session_state.get('report')

if report is None:
    st.error("No Report Available")
    st.info("Run a report on the Overview page")

else:
    try:
        all_transactions = report.get_all_transactions()
    except:
        all_transactions = None

    if all_transactions is None or all_transactions.empty:
        st.info('No Transactions in this Report')
    else:
        category = st.selectbox(
            "Select Transaction Category to Show:",
            ['All'] + [i for i in report.data.keys()],
            key='transactions_to_show',
        )

        with st.container():
            show_transactions(category)






