import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import warnings
from pypfopt import exceptions
import numpy as np
from datetime import date
import yfinance as yf
import requests
from bs4 import BeautifulSoup


def dl_stock_data(tickers, period=None, interval='1d', start="2021-01-01", end=date.today(), col='Adj Close'):
    """
    Scrape stock(s) data from Yahoo Finance

    :param tickers: Stocks in Yahoo Finance format
    :param period:
    :param interval:
    :param start: Start Date
    :param end: End Date
    :param col: Data Column(s)
    :return: Stock Data DataFrame
    """
    if period:
        stock_data = yf.download(tickers, period=period, interval=interval)
    else:
        stock_data = yf.download(tickers, interval=interval, start=start, end=end)
    if stock_data.empty:
        raise Exception('Empty Dataframe')
    if col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
        stock_data = stock_data[col]
    else:
        raise NameError('Invalid Column Name')
    return stock_data


def get_indices_now(indices=('^IXIC', '^NYA', '^GSPC')):
    """
    Scrape indices data from Yahoo Finance

    :param indices: Indices in Yahoo Finance Format
    :return: Latest Indices Data, Percentage Change
    """
    # ytd_data = dl_stock_data(indices, period='2d')
    indices_data = dl_stock_data(indices, period='2d')
    chg = {}
    for i in indices_data.columns:
        chg[i] = (round((indices_data[i][-1] - indices_data[i][-2]) / indices_data[i][-2] * 100, 2))
    return indices_data.iloc[-1].round(2), chg


def get_esg_score(ticker):
    """
    Scrape ESG risk score of specific ticker from Yahoo Finance

    :param ticker: Ticker on Yahoo Finance
    :return: ESH Risk Score, Level of Risk
    """
    link = f'https://www.finance.yahoo.com/quote/{ticker}/sustainability?p={ticker}'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30', }
    res = requests.get(link, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')

    score = soup.find('div', {'class': 'Fz(36px) Fw(600) D(ib) Mend(5px)'}).text
    risk = soup.find('div', {'class': 'Fz(s) Fw(500) smartphone_Pstart(4px)'}).text
    return score, risk


def weighted_esg(weights):
    """
    Get weighted ESG risk score according to stock weights

    :param weights: DataFrame of Weights
    :return: Weighted ESG Risk Score
    """
    df1 = pd.DataFrame(weights, index=['Weight'])
    df1 = df1.T
    df1 = df1[df1['Weight'] != 0]  # Remove 0 values
    sum = 0
    for index, row in df1.iterrows():
        score, _ = get_esg_score(index)
        sum += float(score) * row['Weight']
    return sum


def get_weights(input_ef):
    """
    Get weights of stocks from optimised Efficient Frontier

    :param input_ef: Efficient Frontier
    :return: DataFrame
    """
    ef1 = input_ef.deepcopy()
    ef1.max_sharpe()
    weights = ef1.clean_weights()
    df1 = pd.DataFrame(weights, index=['Weight'])
    df1 = df1.T
    df1 = df1[df1['Weight'] != 0]  # Remove 0 values
    return df1


def plot_stock(stock_data, name, height=None, hover_data=None):
    """
    Plot line charts from specific stock data.

    :param stock_data: in Pandas Dataframe
    :param name: Stock Ticker Name
    :param height: Chart Height
    :param hover_data: Tooltip when hovering on specific point of chart
    :return: Plotly Line Chart
    """

    if stock_data.iloc[-1] > stock_data.iloc[0]:
        line_color = 'green'
    else:
        line_color = 'red'
    fig_stock = px.line(stock_data, title=f'Stock Data for {name}', height=height)
    if hover_data:
        fig_stock.update_traces(hovertemplate='<b>Date: %{x}<br>Price: $%{y}</b><br><br>'+hover_data+'<extra></extra>')
    fig_stock.update_traces(line_color=line_color)
    fig_stock.update_layout(showlegend=False, yaxis_title='US$')
    fig_stock.update_xaxes(showspikes=True, spikecolor="grey", spikesnap="cursor", spikemode="across")
    fig_stock.update_yaxes(showspikes=True, spikecolor="grey", spikesnap="data", spikethickness=1)
    fig_stock.update_layout(spikedistance=1000, hoverdistance=100)
    return fig_stock


def _ef_default_returns_range(ef, points):
    """
    Helper function to generate a range of returns from the GMV returns to
    the maximum (constrained) returns
    """
    ef_minvol = ef.deepcopy()
    ef_maxret = ef.deepcopy()

    ef_minvol.min_volatility()
    min_ret = ef_minvol.portfolio_performance()[0]
    max_ret = ef_maxret._max_return()
    return np.linspace(min_ret, max_ret - 0.0001, points)


def plot_ef(ef, ef_param_range=None, points=100):
    """
    Helper function to plot the efficient frontier from an EfficientFrontier object
    """
    mus, sigmas = [], []

    if ef_param_range is None:
        ef_param_range = _ef_default_returns_range(ef, points)

    # Create a portfolio for each value of ef_param_range
    for param_value in ef_param_range:
        try:
            ef.efficient_return(param_value)
        except exceptions.OptimizationError:
            continue
        except ValueError:
            warnings.warn(
                "Could not construct portfolio for parameter value {:.3f}".format(
                    param_value
                )
            )

        ret, sigma, _ = ef.portfolio_performance()
        mus.append(ret)
        sigmas.append(sigma)

    return go.Scatter(x=sigmas, y=mus, mode='lines', name='Efficient Frontier')
