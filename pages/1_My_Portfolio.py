import streamlit as st
import pandas as pd
import numpy as np
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import plotly.express as px

from pypfopt import risk_models, expected_returns, plotting, EfficientFrontier
import matplotlib.pyplot as plt
from datetime import date
import yfinance as yf


def test_ef():
    companies = ["MSFT", "AMZN", "META", "BABA", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA", "PFE", "JPM", "SBUX"]
    stock_data = yf.download(companies, start="2020-6-01", end=date.today())
    stock_data = stock_data["Adj Close"]
    mu2 = expected_returns.mean_historical_return(stock_data)
    cov_matrix2 = risk_models.sample_cov(stock_data)
    temp_ef = EfficientFrontier(mu2, cov_matrix2)
    return temp_ef


def plot_ef_with_random(ef, n_samples=10000):
    fig, ax = plt.subplots()
    ef_max_sharpe = ef.deepcopy()
    ef_min_vol = ef.deepcopy()

    # Find the tangency portfolio
    ef_max_sharpe.max_sharpe()
    ret_tangent, std_tangent, _ = ef_max_sharpe.portfolio_performance()
    ax.scatter(std_tangent, ret_tangent, marker="*", s=100, c="r", label="Max Sharpe")

    # Min Volatility
    ef_min_vol.min_volatility()
    vol_ret, vol_std, _ = ef_min_vol.portfolio_performance()
    ax.scatter(vol_std, vol_ret, marker="*", s=100, c="g", label="Min Volatility")

    # Generate random portfolios
    w = np.random.dirichlet(np.ones(ef.n_assets), n_samples)
    rets = w.dot(ef.expected_returns)
    stds = np.sqrt(np.diag(w @ ef.cov_matrix @ w.T))
    sharpes = rets / stds
    ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")

    # Output
    plotting.plot_efficient_frontier(ef, ax=ax, show_assets=False)
    ax.set_title("Efficient Frontier with random portfolios")
    ax.legend()
    # plt.tight_layout()

    st.pyplot(fig)


def plot_weights(input_ef):
    ef1 = input_ef.deepcopy()
    ef1.max_sharpe()
    weights = ef1.clean_weights()
    df1 = pd.DataFrame(weights, index=['Weight'])
    df1 = df1.T
    df1 = df1[df1['Weight'] != 0]  # Remove 0 values
    return px.pie(df1, values='Weight', names=df1.index, title='Optimized Stock Allocation')


if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
else:
    ef = test_ef()
    
    
    with st.container():
    
        st.header(f"My Portfolio")
    
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
        
                #df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
                #df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries' # Represent only large countries
                #fig = px.pie(df, names='country', title='Equity Allocation by %')
                fig = plot_weights(ef.deepcopy())
                
                plot_spot = st.empty() # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig, use_container_width=True)

            with st.container():
                st.write('Loading Data...')
                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    plot_ef_with_random(ef.deepcopy())
                    
        with main_col2:
            st.write("Additional information, search about any particular stock")