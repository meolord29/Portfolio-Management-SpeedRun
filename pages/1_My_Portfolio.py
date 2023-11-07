import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
else:
    
    
    
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
        
                df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
                df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries' # Represent only large countries
                fig = px.pie(df, names='country', title='Equity Allocation by %')
                
                
                plot_spot = st.empty() # holding the spot for the graph
                with plot_spot:
                    st.plotly_chart(fig, use_container_width=True)
                    
        with main_col2:
            st.write("Additional information, search about any particular stock")