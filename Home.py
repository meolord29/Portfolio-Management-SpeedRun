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
                expected_return_col, expected_risk_col, = st.columns(2)
                with expected_return_col:
                    st.write("Expected return 0.5")
                
                with expected_risk_col:
                    st.write("Expected risk %")
                    
            with st.container():
                total_invested_col, ESG_risk_col, = st.columns(2)
                with total_invested_col:
                    st.write("Total amount invested: 10000")
                
                with ESG_risk_col:
                    st.write("Average ESG Risk %")

                
            with st.container():
        
                df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
                df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries' # Represent only large countries
                fig = px.pie(df, names='country', title='Equity Allocation by %')
                
                
                plot_spot = st.empty() # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig, use_container_width=True)
                    
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






