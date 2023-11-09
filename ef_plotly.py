import plotly.graph_objects as go
import plotly.express as px
import warnings
from pypfopt import exceptions
import numpy as np
from datetime import date
import yfinance as yf


def dl_stock_data(tickers, period=None, interval='1d', start="2021-01-01", end=date.today(), col='Adj Close'):
    if period:
        stock_data = yf.download(tickers, period=period, interval=interval)
    else:
        stock_data = yf.download(tickers, interval=interval, start=start, end=end)
    if col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
        stock_data = stock_data[col]
    else:
        raise NameError('Invalid Column Name')
    return stock_data


def plot_stock(stock_data, name):
    fig_stock = px.line(stock_data, title=f'Stock Data for {name}')
    fig_stock.update_layout(showlegend=False, yaxis_title='US$')
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


def plot_ef(ef,  ef_param_range=None, points=100):
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
