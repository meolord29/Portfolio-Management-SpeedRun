import pandas as pd
import numpy as np

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import plotly.express as px

import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")


def dl_yh_news(link='https://www.finance.yahoo.com/news'):
    res = requests.get(link)
    soup = BeautifulSoup(res.content, 'html.parser')
    news = []
    for e in soup.select('div:has(>h3>a)'):
        try: # Some may not contain content
            text = e.p.text
        except:
            text = ' '
        if e.a['href'].startswith('https://'):
            link = e.a['href']
        else:
            link = 'http://www.finance.yahoo.com' + e.a['href']

        news.append((e.h3.text, link, text))
    return pd.DataFrame(news, columns=['title', 'link', 'desc'])


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
                #r = requests.get('https://finance.yahoo.com/news')
                #html = r.text
                #mrt-node-Fin-Stream

                # parse the HTML
                #soup = BeautifulSoup(html, "html.parser")
                st.header('Latest Financial and Business News\n')

                yh_news = dl_yh_news()
                for i in range(min(10, len(yh_news))):
                    st.subheader(yh_news.iloc[i]['title'])
                    st.caption(yh_news.iloc[i]['desc'][:200])
                    st.caption('[Read more...](%s)' % yh_news.iloc[i]['link'])
                    st.divider()

                    
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






