import json
import requests
import pandas as pd
from draw import draw_vs_btc

class OnChain:
    
    def __init__(self,  api_key):
        self.api_key=api_key
        self.download_datasets()
        
    def __call_api (self, url):
        res = requests.get(url,
            params={'a': 'BTC', 'api_key': self.api_key})
        data = res.json()
        df = pd.DataFrame.from_dict(data)
        df['Date'] = pd.to_datetime(df['t'], unit='s', yearfirst=True)
        df['Value'] = df['v'].astype('float')
        df = df[['Value', 'Date']]
        df.set_index('Date', inplace=True)
        return df
    
    def download_datasets(self):
        self.hashrate = self.__call_api('https://api.glassnode.com/v1/metrics/mining/hash_rate_mean')
        #self.balance_001_01 = self.__call_api('https://api.glassnode.com/v1/metrics/entities/supply_balance_001_01') 
        #self.balance_1k_10k = self.__call_api('https://api.glassnode.com/v1/metrics/entities/supply_balance_1k_10k')
        self.exchange_distribution = self.__call_api('https://api.glassnode.com/v1/metrics/distribution/balance_exchanges')
        
    def get_balance_001_01(self):
        return self.wallet_001_01  
    
    def get_balance_1K_10K(self):
        return self.balance_1k_10k
        
    def get_hashrate(self):
        return self.hashrate

    def get_exchange_distribution(self):
        return self.exchange_distribution
        
    def plot_balance_001_01(self, btc_df):
        draw_vs_btc(btc_df, self.balance_001_01, 'Balance 0.01-0.1')
        
    def plot_balance_1K_10K(self, btc_df):
        draw_vs_btc(btc_df, self.balance_1K_10K, 'Balance 1K-10K')
    
    def plot_hashrate(self, btc_df):
        hashrate = self.hashrate.rolling(7).mean()
        hashrate.dropna(inplace=True)
        draw_vs_btc(btc_df, hashrate, 'Hashrate 7Days MA')
    
    def plot_exchange_distribution(self, btc_df):
        draw_vs_btc(btc_df, self.exchange_distribution, 'Exchanges distribution')
    

    

    