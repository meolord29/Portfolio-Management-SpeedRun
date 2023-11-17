import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


if 'authentication_status' not in st.session_state:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
if st.session_state.authentication_status:
    pf_df = pd.read_csv('database/datasets/portfolio.csv')
    st.write(st.session_state.username)
    st.write(pf_df.index)
    if st.session_state.username in pf_df.index:
        st.write(pf_df[st.session_state.username])
    else:
        st.write('not found')