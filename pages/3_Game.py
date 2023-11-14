import streamlit as st
from datetime import timedelta

from pypfopt import risk_models, expected_returns, EfficientFrontier
from utilities import *


def test_ef(year=2011):
    companies = ["MSFT", "AMZN", "TSLA", "AAPL", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA",
                 "PFE", "JPM"]
    # stock_data = yf.download(companies, start="2020-6-01", end=date.today())
    # stock_data = stock_data["Adj Close"]
    stock_data = dl_stock_data(companies, start=date(year, 1, 1), end=date(year + 1, 1, 1))
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
    return px.imshow(cor_df, title='Stocks Correlation', color_continuous_scale=['green', 'yellow', 'red'])


def plot_portfolio(amounts):
    cols = ['Cash', 'Stocks', 'Bonds']
    df2 = pd.DataFrame(zip(cols, amounts, [1, 1, 1]), columns=['Categories', 'prop', 'st'])

    fig = px.histogram(df2, x='prop', y='st', orientation='h', color='Categories', height=200, barnorm="percent",
                       text_auto=True, color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(orientation='h', x=0.1),
        legend_title=None
    )
    return fig


if not st.session_state.authentication_status or 'authentication_status' not in st.session_state:
    st.info('Please Login from the Home page and try again.')
    st.stop()

else:

    # Initialisation
    sample_portfolio = [3000, 5000, 2000]
    companies = ["MSFT", "AMZN", "TSLA", "AAPL", "GE", "GOOG", "AMD", "WMT", "BAC", "GM", "T", "UAA", "MA", "PFE",
                 "JPM", "SBUX"]
    if 'year' not in st.session_state:
        st.session_state.year = 2011
    current_year = st.session_state.year

    with st.spinner('Loading Data...'):
        ef, cov_matrix = test_ef(current_year)
        ef_data = ef.deepcopy()
        ef_data.max_sharpe()
        metrics = ef_data.portfolio_performance()
        weights = ef_data.clean_weights()
        df_weights = get_weights(ef.deepcopy())

    with st.container():
        stock_col1, stock_col2 = st.columns(2)

        with stock_col1:
            year_col1, year_col2, year_col3 = st.columns(3)

            year_col1.metric('Year', current_year)
            if year_col2.button('Go to Previous Year', type='primary'):
                st.session_state.year = current_year-1
            if year_col3.button('Go to Next Year', type='primary'):
                st.session_state.year = current_year+1

            option = st.selectbox(
                "Show Stock Information:",
                companies,
                index=None,
                placeholder="Select Stock...",
            )

            # Show Stock Charts

            col1, col2 = st.columns(2)

            if option:

                with col1:
                    graph_period = st.radio('Choose Graph Duration:', ['Full Year', 'Month'])
                with col2:
                    try:
                        if graph_period == 'Month':
                            m = st.slider('Select Month:', 1, 12)
                            stock_adj_close = dl_stock_data(option, start=date(current_year, m, 1),
                                                            end=date(current_year, m + 1, 1))
                        elif graph_period == 'Full Year':
                            stock_adj_close = dl_stock_data(option, start=date(current_year, 1, 1),
                                                            end=date(current_year + 1, 1, 1))

                        with stock_col2:
                            plot_spot = st.empty()  # holding the spot for the graph
                            with plot_spot:
                                st.plotly_chart(plot_stock(stock_adj_close, option, height=400, hover_data='NEWS!'),
                                                use_container_width=True)
                    except Exception:
                        pass

            st.header(f"Portfolio Analysis for Year {current_year}")

    main_col1, main_col2, = st.columns(2)

    with st.container():
        with main_col1:
            with st.container():
                fig2 = plot_correlation(cov_matrix)
                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig2, use_container_width=True)

            with st.container():
                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(plot_ef_with_random(ef.deepcopy()), use_container_width=True)

        with main_col2:
            with st.container():
                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(plot_portfolio(sample_portfolio), use_container_width=True)

            with st.container():
                expected_return_col, expected_risk_col, = st.columns(2)
                with expected_return_col:
                    st.metric(label="Expected Annual Return", value=f"{round(metrics[0] * 100, 2)}%")

                with expected_risk_col:
                    st.metric(label='Annual Volatility', value=f"{round(metrics[1] * 100, 2)}%")

            with st.container():
                total_invested_col, ESG_risk_col, = st.columns(2)
                with total_invested_col:
                    st.metric(label='Total Amount Invested', value=str(sum(sample_portfolio)))

                with ESG_risk_col:
                    # Use this to load real data, using dummy to save scraping time
                    try:
                        st.metric(label='Weighted ESG Risk Score', value=str(round(weighted_esg(weights), 2)))
                    except:
                        st.metric(label='Weighted ESG Risk Score', value='NA')

            with st.container():
                fig = px.pie(df_weights, values='Weight', names=df_weights.index, title='Optimized Stock Allocation')

                plot_spot = st.empty()  # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig, use_container_width=True)

    st.experimental_rerun()
