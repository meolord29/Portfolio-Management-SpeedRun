import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import quantstats as qs
import streamlit.components.v1 as components

import tempfile

def run_company_analytics_vs_SnP500(company_tag, temp_dir):
        # fetch the daily returns for a stock
        
        
        #print(temp_dir.name)
        # use temp_dir, and when done:
        #temp_dir.cleanup()

        print('created temporary directory', temp_dir.name)
    
        stock = qs.utils.download_returns(company_tag)
    
    
        qs.reports.html(stock, "^GSPC", output=f'{temp_dir.name}/report_{company_tag}.html')
        
        # bootstrap 4 collapse example
        st.header(f"Report for {company_tag} vs S&P500:")

        HtmlFile = open(f'{temp_dir.name}/report_{company_tag}.html', 'r', encoding='utf-8')
        
        #HtmlFile = open(f'./database/temporary_reports/report_{company_tag}.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        #print(source_code).
        #source_code = report
        components.html(source_code, height=6000)
    
    
    

if not st.session_state.authentication_status:
    st.info('Please Login from the Home page and try again.')
    st.stop()
    
else:
    temp_dir = tempfile.TemporaryDirectory()
    company_tag = st.text_input('Enter a stock tag:', 'MSFT')
    if st.button("Run analytics and compare to S&P500"):
        temp_dir.cleanup()
        run_company_analytics_vs_SnP500(company_tag, temp_dir)
        
        
    
    