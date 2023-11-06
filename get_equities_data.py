from datetime import datetime
from findatapy.util import SwimPool;
from findatapy.market import Market, MarketDataRequest, MarketDataGenerator
import pandas as pd

import requests
from bs4 import BeautifulSoup

class DataIngester:
    def __init__(self, *args, **kwargs):
        self.md_request: MarketDataRequest
        self.market = Market(market_data_generator=MarketDataGenerator())
        
    def yahoo_set_market_request(
        self, 
        tickers,
        vendor_tickers,
        fields = ["close"], 
        start_date='decade', 
        vendor_fields = ["Close"], 
        freq = 'daily') -> pd.DataFrame: 
        
        
        self.md_request = MarketDataRequest(
            start_date= start_date,  # start date
            data_source="yahoo",  # use Bloomberg as data source
            freq = freq,
            tickers = tickers, #["Apple", "S&P500-ETF"],  # ticker (findatapy)
            fields = fields, #["close"],  # which fields to download
            vendor_tickers = vendor_tickers, # ["aapl", "spy"],  # ticker (Yahoo)
            vendor_fields = vendor_fields, # ["Close"])  # which Bloomberg fields to download)
            )
        
        return self.market.fetch_market(self.md_request)
    
    
    def get_latest_market_cap(self, ticker) -> int:
        URL = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")
        market_cap_string = soup.find("td",attrs={"data-test": "MARKET_CAP-value"}).text
        
        if "T" in market_cap_string:
            market_cap_value = float(market_cap_string[:-1]) * 10**12
            return int(market_cap_value)
            
        if "B" in market_cap_string:
            market_cap_value = float(market_cap_string[:-1]) * 10**9
            return int(market_cap_value)
            
        if "M" in market_cap_string:
            market_cap_value = float(market_cap_string[:-1]) * 10**6
            return int(market_cap_value)
        
        return int(market_cap_string)