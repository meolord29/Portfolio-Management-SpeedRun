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
    pf_amt = list(pf_df.loc[st.session_state.username])

    main_col1, main_col2 = st.columns(2)
    with main_col1:
        df3 = pf_df.T.loc[(pf_df != 0).any()]
        st.plotly_chart(px.pie(df3, values=st.session_state.username, names=df3.index, hole=0.4,
                               title='Your Current Stock Allocation'), use_container_width=True)
        st.write(pf_amt)

    with main_col2:
        for i, num in enumerate(pf_df.loc[st.session_state.username]):
            col1, col2 = st.columns(2)
            col1.write(pf_df.columns[i])
            pf_amt[i] = col2.number_input(pf_df.columns[i], 0.0, 1.0, float(num), 0.05,
                                          key=pf_df.columns[i], label_visibility='collapsed')

    if st.session_state.username in pf_df.index:
        st.plotly_chart(px.pie(pf_df.T.loc[(pf_df.T != 0).any(1)], values=st.session_state.username, hole=0.4))
    else:
        st.write('not found')
