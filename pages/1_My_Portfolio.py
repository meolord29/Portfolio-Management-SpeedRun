import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
else:
    pass