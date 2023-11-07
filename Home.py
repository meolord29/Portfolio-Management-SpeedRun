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

import plotly.express as px

import requests
from bs4 import BeautifulSoup

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
    
    with st.container():
    
        st.header(f"Welcome {name}!")
    
    main_col1, main_col2, = st.columns(2)
    
    with st.container():
        with main_col1:
            with st.container():
                r = requests.get('https://finance.yahoo.com/topic/economic-news')
                html = r.text

                # parse the HTML
                soup = BeautifulSoup(html, "html.parser")
                    
        with main_col2:
            st.write("Have 2 buttons - showcase stock related news, and showcase cross industry news")
        
    with st.container():
        authenticator.logout('**Logout**', 'main', key='unique_key')
    
elif authentication_status is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')






