import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import matplotlib.dates as mpl_dates
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from ta import add_all_ta_features
from mplfinance.original_flavor import candlestick_ohlc
import trendln
import matplotlib.gridspec as gs

levels = []


def isSupport(df,i):
    support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] \
        and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

    return support

def isResistance(df,i):
    resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] \
        and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2] 

    return resistance

def isFarFromLevel(l, s):
    return np.sum([abs(l-x) < s  for x in levels]) == 0

def get_coordinates(tup, time_series):
    
    points = tup[0]
    values = tup[1]
    
    x=[]
    y=[]
    for i in points:
        x.append(time_series.index[i])
        y.append(i*values[0]+values[1])
    return x, y
   
def get_coordinates_tuples(trend, time_series):
    buffer = []
    ris = []
    i = 0
    for t in trend:
        if i>=3:
            break
        x, y = get_coordinates(t, time_series)
        if isFarFromLine(np.sum(np.array(t[0])), buffer):
            ris.append((x, y))
            i = i+1
    return ris
        
def isFarFromLine(el, buffer):
    for i in buffer:
        if abs(el - i)/el * 100 < 15:
            return False
    buffer.append(el)
    return True


class taAnalysis:
    
    def __init__(self, asset, start_date, start_plot_date, end_date = dt.date.today() ,end_plot_date = dt.date.today()):
        self.asset = asset
        self.start_plot_date = start_plot_date
        self.end_plot_date = end_plot_date
        self.end_date = end_date
        self.start_date = start_date
        self.levels = []
        
    def download_data(self):
        downloaded_data = yf.download(self.asset, start=self.start_date, end=self.end_date)
        df = downloaded_data.copy()
        df['Date'] = pd.to_datetime(df.index)
        df['Date'] = df['Date'].apply(mpl_dates.date2num)
        df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df['Ma21'] = df['Close'].rolling(21).mean()
        df['Ma50'] = df['Close'].rolling(50).mean()
        df['Ma200'] = df['Close'].rolling(200).mean()
        df['Volume_mean'] = df['Volume'].rolling(30).mean()
        df.dropna(inplace=True)
        df = add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Close", volume="Volume")
        self.df = df
        
    def get_data(self):
        return self.df
    
    def set_levels(self):
        s =  np.mean(self.df['High'] - self.df['Low'])*2 
        for i in range(2,self.df.shape[0]-2):
            if isSupport(self.df,i):
                l = self.df['Low'][i]
        
                if isFarFromLevel(l, s):
                    levels.append((i,l))
        
            elif isResistance(self.df,i):
                l = self.df['High'][i]
        
                if isFarFromLevel(l, s):
                    levels.append((i,l))
        
    def plot_all(self):
        # Filtro i dati da visualizzare
        df_filtered = self.df[self.start_plot_date: self.end_plot_date].copy()
        ohlc = df_filtered[['Date', 'Open', 'High', 'Low', 'Close']].copy()
    
        fig = plt.figure(figsize=(25,20))
        gs = fig.add_gridspec(100, 1)
        
        fig.suptitle("{0} - da {1} a {2}".format(self.asset, self.start_plot_date, self.end_plot_date))
        fig.patch.set_facecolor('white')
        
        # Organizzo i subplot
        price_ax = fig.add_subplot(gs[0: 60, 0])
        volume_ax = fig.add_subplot(gs[65:73, 0])
        rsi_ax = fig.add_subplot(gs[77:87, 0])
        adx_ax = fig.add_subplot(gs[91:99, 0])
        
        # Imposto i titoli dei subplot
        price_ax.set_title('Candlestick plot')
        volume_ax.set_title('Volumi')
        rsi_ax.set_title('Rsi')
        adx_ax.set_title('Adx')
        
        
        # price_ax
        price_ax.set_xlabel('Date')
        price_ax.set_ylabel('Asset price')
        price_ax.set_facecolor((0.2,0.2,0.2))
        price_ax.yaxis.grid(False)
        price_ax.xaxis.grid(True)
        for axis in ['top','bottom','left','right']:
            price_ax.spines[axis].set_linewidth(0.5)
        
        candlestick_ohlc(price_ax, zip(mdates.date2num(ohlc.index.to_pydatetime()),
                         ohlc['Open'], ohlc['High'], ohlc['Low'], ohlc['Close']),
                         width=0.6, colorup='green', colordown='red', alpha=0.8)
        yLabels = []
        for level in levels:
            price_ax.axhline(level[1],xmin=0, xmax=1, linestyle='dotted', color = "turquoise", linewidth = 1)
            yLabels.append(round(level[1], 0))
        price_ax.set_yticks(np.array(yLabels))
        
        price_ax.plot(df_filtered['Ma21'], color = 'cyan', linewidth = 1.2, label="MA21 -> {0:.2f}".format(df_filtered['Ma21'].iloc[-1]))
        price_ax.plot(df_filtered['Ma50'], color = 'violet', linewidth = 1.2, label="MA50 -> {0:.2f}".format(df_filtered['Ma50'].iloc[-1]))
        price_ax.plot(df_filtered['Ma200'], color = 'crimson', linewidth = 1.2, label="MA200 -> {0:.2f}".format(df_filtered['Ma200'].iloc[-1]))
        price_ax.legend(loc='upper left')
        
        # Gestione delle trendline
        (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(df_filtered['Close'], accuracy=8)
        
        mint = get_coordinates_tuples(mintrend, df_filtered['Close'])
        maxt = get_coordinates_tuples(maxtrend, df_filtered['Close'])
        for m in mint:
            price_ax.plot(m[0], m[1], color='lime', linestyle = 'dotted', linewidth=1.5)
        for m in maxt:
            price_ax.plot(m[0], m[1], color='gold', linestyle = 'dotted', linewidth=1.5)
        
         
        # volume_ax
        volume_ax.bar(df_filtered.index, df_filtered['Volume'])
        volume_ax.plot(df_filtered['Volume_mean'], color='crimson')
        
        # rsi
        rsi_ax.set_ylim(0, 100)
        rsi_ax.plot(df_filtered['momentum_rsi'], label = "Rsi line -> {0:.2f}".format(self.df['momentum_rsi'].iloc[-1]))
        rsi_ax.axhspan(0, 30, facecolor = 'green', alpha = 0.3)
        rsi_ax.axhspan(70, 100, facecolor = 'red', alpha = 0.3)
        rsi_ax.axhline(y=70, color='red', linestyle = '-.')
        rsi_ax.axhline(y=30, color='green', linestyle = '-.')
        
        # adx
        adx_ax.set_ylim(0, 100)
        adx_ax.plot(df_filtered['trend_adx'], label = "ADX line -> {0:.2f}".format(df_filtered['trend_adx'].iloc[-1]))
        adx_ax.axhspan(0, 15, facecolor = 'green', alpha = 0.3)
        adx_ax.axhline(y=15, color='green', linestyle = '-.')
    
        #plt.savefig('./{0}-from-{1}-to-{2}.png'.format(self.asset, self.start_plot_date, self.end_plot_date), 
        #            dpi=300)
        return fig
    
if __name__ == "__main__":
    ta = taAnalysis("btc-usd", "2020-01-01", "2020-01-01")
    ta.download_data()
    ta.set_levels()
    df = ta.get_data()
    fig = ta.plot_all()
    fig.show()
    
        