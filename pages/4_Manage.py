import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

if 'authentication_status' not in st.session_state:
    st.info('Please Login from the Home page and try again.')
    st.stop()

if st.session_state.authentication_status:
    pf_df = pd.read_csv('database/datasets/portfolio.csv', index_col=0)
    if st.session_state.username not in pf_df.index:
        st.info('User Portfolio Not Found')
        st.stop()

    if 'pf_df' not in st.session_state:
        st.session_state.pf_df = pf_df
        st.session_state.pf_amt = list(st.session_state.pf_df.loc[st.session_state.username])

    main_col1, main_col2 = st.columns(2)
    with main_col1:
        df3 = st.session_state.pf_df.T.loc[(st.session_state.pf_df != 0).any()]
        st.plotly_chart(px.pie(df3, values=st.session_state.username, names=df3.index, hole=0.4,
                               title='Your Current Stock Allocation'), use_container_width=True)

    with main_col2:
        if st.button("Update Allocation", type='primary', disabled=sum(st.session_state.pf_amt) != 1):
            if sum(st.session_state.pf_amt) == 1:
                st.write('Allocation Updated.')
                st.session_state.pf_df.loc[st.session_state.username] = st.session_state.pf_amt
                # pf_df.to_csv('database/datasets/portfolio.csv')
            else:
                st.write('Stocks allocation does not add up to 100%. Please retry.')
                pf_amt = list(st.session_state.pf_df.loc[st.session_state.username])
            st.rerun()

        for i, num in enumerate(st.session_state.pf_df.loc[st.session_state.username]):
            col1, col2 = st.columns(2)
            col1.write(pf_df.columns[i])
            st.session_state.pf_amt[i] = round(col2.number_input(pf_df.columns[i], 0.0, 1.0, float(num), 0.05,
                                                                 key=pf_df.columns[i], label_visibility='collapsed'), 2)

    main_col1.write(st.session_state.pf_amt)
