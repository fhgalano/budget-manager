import datetime

import streamlit as st
import plotly.express as px
from pandas import DataFrame
from numpy.random import randn

from main import run_report_for_date, load_new_transactions_to_db
from budget_report_generator.budget import Budget


my_budget = Budget()


def current_day_report():
    return run_report_for_date()


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


def display_metrics(current_report, previous_report):
    print(current_report)
    rd, ad, sd = report_deltas(current_report, previous_report)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric('Expected Monthly Total', n2c(my_budget.extra))
    c1.metric('Spent Total', n2c(current_report['spent']), n2c(sd),
              delta_color='off')
    c1.metric(
        'Remaining Wallet {nice}'.format(
            nice=":sunglasses:" if current_report['remaining'] > 0 else ""
        ),
        n2c(current_report['remaining']), n2c(rd))

    c2.metric('Raw Takehome', n2c(my_budget.takehome))
    c2.metric('Raw Spent Total', current_report['raw_spent'])

    c3.metric('Actual Spend / Day', n2c(current_report['ASPD']), n2c(ad),
              delta_color='inverse')
    c3.metric('Goal Spend per Day', n2c(my_budget.spend_per_day))

    known = current_report['categories']['Known Expenses']
    c4.metric('Pre Budgeted Expense Limit', n2c(my_budget.expected))
    c4.metric('Pre Budgeted Spent', n2c(known))
    c4.metric('Pre Budgeted Rate', n2c(current_report['PBSR']))
    current_report


def report_deltas(current_report, previous_report):
    remain_delta = current_report['remaining'] - previous_report['remaining']
    aspd_delta = current_report['ASPD'] - previous_report['ASPD']
    spend_delta = current_report['spent'] - previous_report['spent']

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
    display_metrics(report.summary, prev_report.summary)

    unknown = report.data.get('Unknown')

    st.write(report.get_known_transactions()['amount'].sum())
    st.write(my_budget.expected)
    st.write(my_budget.extra)

    if report.get_known_transactions()['amount'].sum() > my_budget.expected:
        st.error('Known Expenses higher than expected')


