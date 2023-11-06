import streamlit as st
import pandas as pd
import numpy as np
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

def st_authenticator():
    with open('database/credentials/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
        file.close()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    return authenticator

authenticator  = st_authenticator()
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.session_state.authentication_status = True
    authenticator.logout('**Logout**', 'main', key='unique_key')
    
    
    st.header(f"Welcome {name}!")
    
    
    with st.container():
        st.write("Main body section will include a dashboard of key portfolio information (assumption, needs to be validated)")

        # You can call any Streamlit command, including custom components:
        st.bar_chart(np.random.randn(50, 3))
    
    
elif authentication_status is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')






