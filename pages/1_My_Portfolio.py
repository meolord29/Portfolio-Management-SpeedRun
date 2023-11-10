import streamlit as st

from pypfopt import risk_models, expected_returns, EfficientFrontier
from utilities import *


def test_ef():
    companies = ["MSFT", "AMZN", "META", "BABA", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA", "PFE",
                 "JPM", "SBUX"]
    stock_data = yf.download(companies, start="2020-6-01", end=date.today())
    stock_data = stock_data["Adj Close"]
    mu2 = expected_returns.mean_historical_return(stock_data)
    cov_matrix2 = risk_models.sample_cov(stock_data)
    temp_ef = EfficientFrontier(mu2, cov_matrix2)
    return temp_ef, cov_matrix2


def plot_ef_with_random(ef, n_samples=5000):
    # fig, ax = plt.subplots()
    ef_max_sharpe = ef.deepcopy()
    ef_min_vol = ef.deepcopy()

    # Generate random portfolios
    w = np.random.dirichlet(np.ones(ef.n_assets), n_samples)
    rets = w.dot(ef.expected_returns)
    stds = np.sqrt(np.diag(w @ ef.cov_matrix @ w.T))
    sharpes = rets / stds

    rd_df = pd.DataFrame(list(zip(stds, rets)), columns=['stds', 'rets'])
    fig_ef = px.scatter(rd_df, x='stds', y='rets', color=sharpes, color_continuous_scale="viridis_r",
                        title="Efficient Frontier with random portfolios")

    # Find the tangency portfolio
    ef_max_sharpe.max_sharpe()
    ret_tangent, std_tangent, _ = ef_max_sharpe.portfolio_performance()
    fig_ef.add_trace(go.Scatter(x=[std_tangent], y=[ret_tangent],
                                marker=dict(size=10, symbol="star", color="Blue"), name="Max Sharpe"))

    # Min Volatility
    ef_min_vol.min_volatility()
    vol_ret, vol_std, _ = ef_min_vol.portfolio_performance()
    fig_ef.add_trace(go.Scatter(x=[vol_std], y=[vol_ret],
                                marker=dict(size=10, symbol="star", color="Green"), name="Min Volatility"))

    # Output
    fig_ef.add_trace(plot_ef(ef))

    fig_ef.update_layout(legend_x=1, legend_y=0)

    return fig_ef


def plot_correlation(df):
    cor_df = risk_models.cov_to_corr(df)
    return px.imshow(cor_df, title='Stocks Correlation', color_continuous_scale=['red','green'])


def plot_portfolio(amounts):
    cols = ['Cash', 'Stocks', 'Bonds']
    df2 = pd.DataFrame(zip(cols, amounts, [1, 1, 1]), columns=['Categories', 'prop', 'st'])

    fig = px.histogram(df2, x='prop', y='st', orientation='h', color='Categories', height=250, barnorm="percent",
                       text_auto=True, color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(orientation='h', x=0.2),
        legend_title=None
    )
    return fig


if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()

else:

    # Initialisation
    sample_portfolio = [3000, 5000, 2000]
    companies = ["MSFT", "AMZN", "META", "BABA", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA", "PFE",
                 "JPM", "SBUX"]

    with st.spinner('Loading Data...'):
        ef, cov_matrix = test_ef()
        ef_data = ef.deepcopy()
        ef_data.max_sharpe()
        metrics = ef_data.portfolio_performance()
        weights = ef_data.clean_weights()
        df_weights = get_weights(ef.deepcopy())

    with st.container():

        with st.container():
            index_list, chg_list = get_indices_now()

            col1, col2, col3 = st.columns(3)
            col1.metric("NASDAQ Composite", str(index_list['^IXIC']), f"{chg_list['^IXIC']}%")
            col2.metric("NYSE Composite", str(index_list['^NYA']), f"{chg_list['^NYA']}%")
            col3.metric("S&P 500", str(index_list['^GSPC']), f"{chg_list['^GSPC']}%")

        st.header(f"My Portfolio")
        plot_spot = st.empty()  # holding the spot for the graph
        with plot_spot:
            st.plotly_chart(plot_portfolio(sample_portfolio))

    main_col1, main_col2, = st.columns(2)

    with st.container():
        with main_col1:

            with st.container():
                expected_return_col, expected_risk_col, = st.columns(2)
                with expected_return_col:
                    st.metric(label="Expected Annual Return", value=f"{round(metrics[0]*100,2)}%")

                with expected_risk_col:
                    st.metric(label='Annual Volatility', value=f"{round(metrics[1]*100,2)}%")

            with st.container():
                total_invested_col, ESG_risk_col, = st.columns(2)
                with total_invested_col:
                    st.metric(label='Total Amount Invested', value=str(sum(sample_portfolio)))

                with ESG_risk_col:
                    st.metric(label='Weighted ESG Risk Score', value=str(round(weighted_esg(weights), 2)))

            with st.container():
                fig = px.pie(df_weights, values='Weight', names=df_weights.index, title='Optimized Stock Allocation')

                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig, use_container_width=True)

            with st.container():
                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(plot_ef_with_random(ef.deepcopy()))

            with st.container():
                fig2 = plot_correlation(cov_matrix)
                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig2, use_container_width=True)

        with main_col2:
            option = st.selectbox(
                "Stock Information:",
                companies,
                index=None,
                placeholder="Select Stock...",
            )

            if option:
                col1, col2, col3 = st.columns(3)

                col1.button('1 Day')
                if col2.button('1 Week'):
                    stock_adj_close = dl_stock_data(option, interval='1h', period='1wk')
                if col3.button('1 Month'):
                    stock_adj_close = dl_stock_data(option, period='1mo')
                else:
                    stock_adj_close = dl_stock_data(option, interval='1m', period='1d')

                # stock_adj_close = dl_stock_data(option)

                with st.container():
                    plot_spot = st.empty()  # holding the spot for the graph
                    with plot_spot:
                        st.plotly_chart(plot_stock(stock_adj_close, option), use_container_width=True)
