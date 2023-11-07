import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from pypfopt import risk_models, expected_returns, plotting, EfficientFrontier



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
    plt.tight_layout()

    st.pyplot(fig)


def test_ef():
    companies = ["MSFT", "AMZN", "META", "BABA", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA", "PFE", "JPM", "SBUX"]
    stock_data = yf.download(companies, start="2020-6-01", end=date.today())
    stock_data = stock_data["Adj Close"]
    mu2 = expected_returns.mean_historical_return(stock_data)
    cov_matrix2 = risk_models.sample_cov(stock_data)
    return EfficientFrontier(mu2, cov_matrix2, weight_bounds=(None, None))


if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
else:
    if st.button("Test ef"):
        ef = test_ef()
        plot_ef_with_random(ef)
