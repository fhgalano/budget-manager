import datetime

import streamlit as st
import plotly.express as px
from pandas import DataFrame
from numpy.random import randn

from main import run_report_for_date, load_new_transactions_to_db
from budget_report_generator.report import Report
from budget_report_generator.budget import Budget

my_budget = Budget()


def current_day_report():
    return run_report_for_date(date=datetime.datetime.today())


def custom_date_report(date):
    return run_report_for_date(date=date)


def n2c(num):
    num = round(num, 2)
    return '{form}'.format(
        form='$' + str(abs(num)) if num >= 0 else '-$' + str(abs(num))
    )


def save_state_variable(name):
    if st.session_state.get(name) is None:
        st.session_state[name] = True
    else:
        st.session_state[name] = not st.session_state[name]


def generate_spending_wheel(categories):
    d = {
        'categories': list(categories.keys()),
        'totals': list(categories.values())
    }
    data = DataFrame.from_dict(d)
    data['cost'] = data['totals'].apply(n2c)
    fig = px.pie(
        data,
        values='totals',
        names='categories',
        hole=0.4
    )
    fig.update_traces(textposition='inside',
                      text=data['cost'],
                      textinfo='label+text')
    st.plotly_chart(fig, use_container_width=True)


def display_metrics(
        current_report: Report,
        previous_report: Report
):
    rd, ad, sd = report_deltas(current_report, previous_report)

    with st.expander("Wallet Info", expanded=True):
        c1, c2 = st.columns(2)

        # Row 0
        c1.metric(
            'Remaining Wallet {nice}'.format(
                nice=":sunglasses:" if current_report.wallet_remaining > 0 else ""
            ),
            n2c(current_report.wallet_remaining),
            n2c(rd),
        )
        c2.metric(
            'Wallet Spent / Day', n2c(current_report.wallet_spend_per_day),
            n2c(ad),
            delta_color='inverse'
        )

    with st.expander("Metrics", expanded=False):
        c1, c2, c3 = st.columns(3)

        # Row 1
        c1.metric('Takehome', n2c(my_budget.takehome))
        c2.metric('Total Spent', n2c(current_report.total_spent))
        c3.metric('Total Spent / Day', n2c(current_report.total_spent_per_day))

        # Row 2
        known = current_report.summary['categories']['Known Expenses']
        c1.metric('Pre Budgeted Expense Limit', n2c(my_budget.expected))
        c2.metric('Pre Budgeted Spent', n2c(known))
        c3.metric('Pre Budgeted Spent / Day',
                  n2c(current_report.known_spend_per_day))
        # Row 3
        c1.metric('Monthly Wallet', n2c(my_budget.extra))
        c2.metric('Wallet Spent', n2c(current_report.wallet_spent), n2c(sd),
                  delta_color='off')
        c3.metric('Goal Spend per Day', n2c(my_budget.spend_per_day))

        # Row 4
        c1.metric('Expected Savings', n2c(current_report.expected_savings))
        c2.metric('Current Savings', n2c(current_report.current_savings))


def report_deltas(current_report, previous_report):
    remain_delta = current_report.wallet_remaining \
                   - previous_report.wallet_remaining
    aspd_delta = current_report.wallet_spend_per_day \
                 - previous_report.wallet_spend_per_day
    spend_delta = current_report.wallet_spent - previous_report.wallet_spent

    return remain_delta, aspd_delta, spend_delta


# Start Page Definition
new_data_button = st.button("Load in New Transactions")
if new_data_button:
    load_new_transactions_to_db()

st.title('Budget Overview')
custom_checkbox = st.checkbox(
    'Custom Date',
    value=st.session_state.get('custom', False),
    on_change=save_state_variable,
    args=['custom']
)
if custom_checkbox:
    with st.form(key="Custom Date Report"):
        date = st.date_input(
            'Select Date to get report from',
            value=st.session_state.get('date', datetime.datetime.today())
        )
        report_button = st.form_submit_button('Run Report for Custom Date')

    if report_button:
        report = custom_date_report(date=date)
        prev_date = date - datetime.timedelta(days=1)
        prev_report = custom_date_report(prev_date)

        st.session_state['report'] = report
        st.session_state['previous_report'] = prev_report
        st.session_state['date'] = date

else:
    if st.button('Run Report for Today'):
        report = current_day_report()
        prev_date = datetime.datetime.today() - datetime.timedelta(days=1)
        prev_report = custom_date_report(prev_date)

        st.session_state['report'] = report
        st.session_state['previous_report'] = prev_report
        st.session_state['date'] = datetime.datetime.today()

if ((report := st.session_state.get('report'))
        and (prev_report := st.session_state.get('previous_report'))):
    st.subheader('Report for {}'.format(
        st.session_state.get('date', datetime.datetime.today())
    ))
    generate_spending_wheel(report.summary['categories'])
    display_metrics(report, prev_report)

    unknown = report.data.get('Unknown')

    if report.get_known_transactions()['amount'].sum() > my_budget.expected:
        st.info('Known Expenses higher than expected')
