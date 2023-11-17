import pandas as pd

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import requests
from bs4 import BeautifulSoup

from utilities import dl_stock_data, plot_stock, get_indices_now

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")


def dl_yh_news(link='https://www.finance.yahoo.com/news'):
    res = requests.get(link)
    soup = BeautifulSoup(res.content, 'html.parser')
    news = []
    for e in soup.select('div:has(>h3>a)'):
        try:  # Some may not contain content
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


authenticator = st_authenticator()
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.session_state.authentication_status = True

    with st.container():

        st.header(f"Welcome {name}!")

    main_col1, main_col2, = st.columns(2)

    with st.container():
        with main_col1:
            with st.container():

                index_list, chg_list = get_indices_now()

                col1, col2, col3 = st.columns(3)
                col1.metric("NASDAQ Composite", str(index_list['^IXIC']), f"{chg_list['^IXIC']}%")
                col2.metric("NYSE Composite", str(index_list['^NYA']), f"{chg_list['^NYA']}%")
                col3.metric("S&P 500", str(index_list['^GSPC']), f"{chg_list['^GSPC']}%")

            with st.container():
                # r = requests.get('https://finance.yahoo.com/news')
                # html = r.text
                # mrt-node-Fin-Stream

                # parse the HTML
                # soup = BeautifulSoup(html, "html.parser")
                st.subheader('Latest Financial and Business News')
                st.divider()

                yh_news = dl_yh_news()
                for i in range(min(10, len(yh_news))):
                    item = yh_news.iloc[i]
                    st.write(f"**{item['title']}**")
                    st.caption(item['desc'][:item['desc'].find(' ', 200)] + '... [Read more](%s)' % item['link'])
                    st.write('')

        with main_col2:

            companies = ['AAPL', 'NVDA', 'BRK-B', 'JPM', 'LLY', 'ABT', 'CVX', 'SO', 'TMUS', 'VZ', 'NEE', 'SRE', 'ABNB',
                        'HLT', 'RS', 'LEU', 'UPS', 'FDX', 'NXST', 'CHTR', 'NVO', 'PFE', 'BLDR', 'PDD']
            option = st.selectbox(
                "Specific Stock Info:",
                companies,
                index=None,
                placeholder="Select Stock...",
            )

            col1, col2, col3 = st.columns(3)

            if option:
                col1.button('1 Day')
                stock_adj_close = dl_stock_data(option, interval='1m', period='1d')
                # stock = dl_stock_data(option, period='2d')
                if col2.button('1 Month'):
                    stock_adj_close = dl_stock_data(option, interval='1d', period='1mo')
                    # stock = dl_stock_data(option, interval='1mo', period='2mo')
                if col3.button('1 Year'):
                    stock_adj_close = dl_stock_data(option, interval='1d', period='1y')
                    # stock = dl_stock_data(option, interval='1y', period='2y')

                # chg = round((stock[-1] - stock[-2]) / stock[-2] * 100, 2)
                chg = round((stock_adj_close[-1] - stock_adj_close[0]) / stock_adj_close[0] * 100, 2)
                st.metric(option, 'US$' + str(round(stock_adj_close[-1], 2)), f"{chg}%")

                with st.container():
                    plot_spot = st.empty()  # holding the spot for the graph
                    with plot_spot:
                        st.plotly_chart(plot_stock(stock_adj_close, option), use_container_width=True)

                stock_news = dl_yh_news(f'https://www.finance.yahoo.com/quote/{option}?p={option}&.tsrc=fin-srch')
                st.write(f'**{option} Related News:**')

                for i in range(min(5, len(stock_news))):
                    item = stock_news.iloc[i]
                    st.write(f"**{item['title']}**")
                    st.caption(item['desc'][:item['desc'].find(' ', 200)] + '... [Read more](%s)' % item['link'])
                    st.write('')

    with st.container():
        authenticator.logout('**Logout**', 'main', key='unique_key')

elif authentication_status is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')
