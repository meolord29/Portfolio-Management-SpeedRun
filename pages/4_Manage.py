import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


if 'authentication_status' not in st.session_state:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
if st.session_state.authentication_status:
    pf_df = pd.read_csv('database/datasets/portfolio.csv', index_col=0)
    col1, col2 = st.columns(2)
    with col1:
        for col in pf_df.columns:
            st.write(col)
    with col2:
        for i, num in enumerate(pf_df.loc[st.session_state.username]):
            temp = st.number_input('', 0.0, 1.0, float(num), 0.05, key=pf_df.columns[i], label_visibility='collapsed')

    if st.session_state.username in pf_df.index:
        st.write(pf_df.loc[st.session_state.username])
    else:
        st.write('not found')
