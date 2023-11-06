import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import quantstats as qs
import streamlit.components.v1 as components

def run_company_analytics_vs_SnP500(company_tag):
        # fetch the daily returns for a stock
        stock = qs.utils.download_returns(company_tag)
        
        
        qs.reports.html(stock, "^GSPC", output=f'./database/temporary_reports/report_{company_tag}.html')
        
        # bootstrap 4 collapse example
        st.header(f"Report for {company_tag} vs S&P500:")

        HtmlFile = open(f'./database/temporary_reports/report_{company_tag}.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        print(source_code)
        components.html(source_code, height=6000)
    
    
    

if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
else:
    
    company_tag = st.text_input('Enter a stock tag:', 'MSFT')
    if st.button("Run analytics and compare to S&P500"):
        run_company_analytics_vs_SnP500(company_tag)
        
    
    