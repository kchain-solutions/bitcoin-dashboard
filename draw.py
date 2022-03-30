import matplotlib.pyplot as plt
import pandas as pd

def draw_vs_btc(btcDf, other_asset, other_asset_name):
    joinDf = other_asset.join(btcDf['Close'])
    joinDf.dropna(inplace=True)
    fig, ax1 = plt.subplots(figsize=(16,7))
    
    color = 'tab:orange'
    ax1.set_xlabel('Date')
    ax1.set_ylabel(other_asset_name, color=color)
    ax1.plot(joinDf.index, joinDf['Value'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:grey'
    ax2.set_ylabel('btc-usd', color=color)  # we already handled the x-label with ax1
    ax2.plot(joinDf.index, joinDf['Close'], color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.show()
    