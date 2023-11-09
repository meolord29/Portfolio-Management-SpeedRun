import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import plotly.express as px

import requests
from bs4 import BeautifulSoup

from ef_plotly import dl_stock_data, plot_stock

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
                st.subheader('Latest Financial and Business News')
                st.divider()

                yh_news = dl_yh_news()
                for i in range(min(10, len(yh_news))):
                    item = yh_news.iloc[i]
                    st.write(f"**{item['title']}**")
                    st.caption(item['desc'][:item['desc'].find(' ', 200)]+'...')
                    st.caption('[Read more...](%s)' % item['link'])
                    st.write('')
                    
        with main_col2:
            st.write("Have 2 buttons - showcase stock related news, and showcase cross industry news")

            companies = ["MSFT", "AMZN", "META", "BABA", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA",
                         "PFE", "JPM", "SBUX"]
            option = st.selectbox(
                "Specific Stock Related News",
                companies,
                index=None,
                placeholder="Select Stock...",
            )

            if option:
                stock_adj_close = dl_stock_data(option, interval='1m', period='1d')

                with st.container():
                    plot_spot = st.empty()  # holding the spot for the graph
                    with plot_spot:
                        st.plotly_chart(plot_stock(stock_adj_close, option), use_container_width=True)

                stock_news = dl_yh_news(f'https://www.finance.yahoo.com/quote/{option}?p={option}&.tsrc=fin-srch')
                for i in range(min(5, len(yh_news))):
                    item = yh_news.iloc[i]
                    st.write(f"**{item['title']}**")
                    st.caption(item['desc'][:item['desc'].find(' ', 200)] + '[Read more...](%s)' % item['link'])
                    st.write('')
        
    with st.container():
        authenticator.logout('**Logout**', 'main', key='unique_key')
    
elif authentication_status is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')






