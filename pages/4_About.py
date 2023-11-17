import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


if 'authentication_status' not in st.session_state:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
if st.session_state.authentication_status:
    pass