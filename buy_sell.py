import numpy as np
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import date
plt.style.use('fivethirtyeight')
yf.pdr_override()
import streamlit as st

st.title('Buy And Sell Signals')

sidebar=st.sidebar
sidebar.header('Input Space')

with st.container():

  stock=sidebar.text_input("Enter Stock Ticker")
  date=sidebar.date_input('Enter Start Date')
  button=sidebar.button('submit')
  
  if button:  
    


 
    stocksymbols=stock
    startdate = date
    end_date = date.today()
    print(end_date)
    def getMyPortfolio(stocks = stocksymbols ,start = startdate , end = end_date):
        data = web.get_data_yahoo(stocks , start = start ,end= end )
        return data 

    data = getMyPortfolio(stocksymbols)
    data.head()

    
    data['SMA 5'] = ta.sma(data['Close'],5)
    data['SMA 20'] = ta.sma(data['Close'],20)
#SMA BUY SELL
#Function for buy and sell signal
    def buy_sell(data):
        signalBuy = []
        signalSell = []
        position = False 

        for i in range(len(data)):
            if data['SMA 5'][i] > data['SMA 20'][i]:
                if position == False :
                    signalBuy.append(data['Adj Close'][i])
                    signalSell.append(np.nan)
                    position = True
                else:
                    signalBuy.append(np.nan)
                    signalSell.append(np.nan)
            elif data['SMA 5'][i] < data['SMA 20'][i]:
                if position == True:
                    signalBuy.append(np.nan)
                    signalSell.append(data['Adj Close'][i])
                    position = False
                else:
                    signalBuy.append(np.nan)
                    signalSell.append(np.nan)
            else:
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        return pd.Series([signalBuy, signalSell])


    data['Buy_Signal_price'], data['Sell_Signal_price'] = buy_sell(data)
    data.tail()

    st.markdown('Simple Moving Average')
    fig, ax = plt.subplots(figsize=(14,8))
    ax.plot(data['Adj Close'] , label = stocksymbols[0] ,linewidth=0.5, color='blue', alpha = 0.9)
    ax.plot(data['SMA 5'], label = 'SMA5', alpha = 0.85)
    ax.plot(data['SMA 20'], label = 'SMA20' , alpha = 0.85)
    ax.scatter(data.index , data['Buy_Signal_price'] , label = 'Buy' , marker = '^', color = 'green',alpha =1 )
    ax.scatter(data.index , data['Sell_Signal_price'] , label = 'Sell' , marker = 'v', color = 'red',alpha =1 )
    ax.set_title(stocksymbols[0] + " Price History with buy and sell signals",fontsize=10, backgroundcolor='blue', color='white')
    ax.set_xlabel(f'{startdate} - {end_date}' ,fontsize=18)
    ax.set_ylabel('Close Price INR (₨)' , fontsize=18)
    legend = ax.legend()
    ax.grid()
    plt.tight_layout()
    plt.show()
    st.pyplot(fig)
      

    macd = ta.macd(data['Close'])
    macd.head()


    data = pd.concat([data, macd], axis=1).reindex(data.index)
    data.head()


    def MACD_Strategy(df, risk):
        MACD_Buy=[]
        MACD_Sell=[]
        position=False

        for i in range(0, len(df)):
            if df['MACD_12_26_9'][i] > df['MACDs_12_26_9'][i] :
                MACD_Sell.append(np.nan)
                if position ==False:
                    MACD_Buy.append(df['Adj Close'][i])
                    position=True
                else:
                    MACD_Buy.append(np.nan)
            elif df['MACD_12_26_9'][i] < df['MACDs_12_26_9'][i] :
                MACD_Buy.append(np.nan)
                if position == True:
                    MACD_Sell.append(df['Adj Close'][i])
                    position=False
                else:
                    MACD_Sell.append(np.nan)
            elif position == True and df['Adj Close'][i] < MACD_Buy[-1] * (1 - risk):
                MACD_Sell.append(df["Adj Close"][i])
                MACD_Buy.append(np.nan)
                position = False
            elif position == True and df['Adj Close'][i] < df['Adj Close'][i - 1] * (1 - risk):
                MACD_Sell.append(df["Adj Close"][i])
                MACD_Buy.append(np.nan)
                position = False
            else:
                MACD_Buy.append(np.nan)
                MACD_Sell.append(np.nan)

        data['MACD_Buy_Signal_price'] = MACD_Buy
        data['MACD_Sell_Signal_price'] = MACD_Sell


    MACD_strategy = MACD_Strategy(data, 0.025)
    MACD_strategy

    def MACD_color(data):
        MACD_color = []
        for i in range(0, len(data)):
            if data['MACDh_12_26_9'][i] > data['MACDh_12_26_9'][i - 1]:
                MACD_color.append(True)
            else:
                MACD_color.append(False)
        return MACD_color

    data['positive'] = MACD_color(data)
    data.head()

    st.markdown('Moving Average Convergence And Divergence')
    plt.rcParams.update({'font.size': 10})
    fig, ax1 = plt.subplots(figsize=(14,8))
    fig.suptitle(stocksymbols[0], fontsize=10, backgroundcolor='blue', color='white')
    ax1 = plt.subplot2grid((14, 8), (0, 0), rowspan=8, colspan=14)
    ax2 = plt.subplot2grid((14, 12), (10, 0), rowspan=6, colspan=14)
    ax1.set_ylabel('Price in ₨')
    ax1.plot('Adj Close',data=data, label='Close Price', linewidth=0.5, color='blue')
    ax1.scatter(data.index, data['MACD_Buy_Signal_price'], color='green', marker='^', alpha=1)
    ax1.scatter(data.index, data['MACD_Sell_Signal_price'], color='red', marker='v', alpha=1)
    ax1.legend()
    ax1.grid()
    ax1.set_xlabel('Date', fontsize=8)

    ax2.set_ylabel('MACD', fontsize=8)
    ax2.plot('MACD_12_26_9', data=data, label='MACD', linewidth=0.5, color='blue')
    ax2.plot('MACDs_12_26_9', data=data, label='signal', linewidth=0.5, color='red')
    ax2.bar(data.index,'MACDh_12_26_9', data=data, label='Volume', color=data.positive.map({True: 'g', False: 'r'}),width=1,alpha=0.8)
    ax2.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    ax2.grid()
    plt.show()
    st.pyplot(fig)


    def bb_strategy(data):
        bbBuy = []
        bbSell = []
        position = False
        bb = ta.bbands(data['Adj Close'], length=20,std=2)
        data = pd.concat([data, bb], axis=1).reindex(data.index)

        for i in range(len(data)):
            if data['Adj Close'][i] < data['BBL_20_2.0'][i]:
                if position == False :
                    bbBuy.append(data['Adj Close'][i])
                    bbSell.append(np.nan)
                    position = True
                else:
                    bbBuy.append(np.nan)
                    bbSell.append(np.nan)
            elif data['Adj Close'][i] > data['BBU_20_2.0'][i]:
                if position == True:
                    bbBuy.append(np.nan)
                    bbSell.append(data['Adj Close'][i])
                    position = False #To indicate that I actually went there
                else:
                    bbBuy.append(np.nan)
                    bbSell.append(np.nan)
            else :
                bbBuy.append(np.nan)
                bbSell.append(np.nan)

        data['bb_Buy_Signal_price'] = bbBuy
        data['bb_Sell_Signal_price'] = bbSell

        return data


#storing the function
    data = bb_strategy(data)
    data.head()

#plot
    st.markdown('Bollinger Bands')
    fig, ax1 = plt.subplots(figsize=(14,8))
    fig.suptitle(stocksymbols[0], fontsize=10, backgroundcolor='blue', color='white')
    ax1 = plt.subplot2grid((14, 8), (0, 0), rowspan=8, colspan=14)
    ax2 = plt.subplot2grid((14, 12), (10, 0), rowspan=6, colspan=14)
    ax1.set_ylabel('Price in ₨')
    ax1.plot(data['Adj Close'],label='Close Price', linewidth=0.5, color='blue')
    ax1.scatter(data.index, data['bb_Buy_Signal_price'], color='green', marker='^', alpha=1)
    ax1.scatter(data.index, data['bb_Sell_Signal_price'], color='red', marker='v', alpha=1)
    ax1.legend()
    ax1.grid()
    ax1.set_xlabel('Date', fontsize=8)

    ax2.plot(data['BBM_20_2.0'], label='Middle', color='blue', alpha=0.35) #middle band
    ax2.plot(data['BBU_20_2.0'], label='Upper', color='green', alpha=0.35) #Upper band
    ax2.plot(data['BBL_20_2.0'], label='Lower', color='red', alpha=0.35) #lower band
    ax2.fill_between(data.index, data['BBL_20_2.0'], data['BBU_20_2.0'], alpha=0.1)
    ax2.legend(loc='upper left')
    ax2.grid()
    plt.show()
    st.pyplot(fig)



    



    rsi=ta.rsi(data['Close'])
    data['rsi']=rsi
    data.head()

    
    def rsi(data):
        Buy = []
        Sell = []
        position = False
    

        for i in range(len(data)):
            if data['rsi'][i] < 30:
                if position == False :
                    Buy.append(data['Adj Close'][i])
                    Sell.append(np.nan)
                    position = True
                else:
                    Buy.append(np.nan)
                    Sell.append(np.nan)
            elif data['rsi'][i] > 70:
                if position == True:
                    Buy.append(np.nan)
                    Sell.append(data['Adj Close'][i])
                    position = False #To indicate that I actually went there
                else:
                    Buy.append(np.nan)
                    Sell.append(np.nan)
            else :
                Buy.append(np.nan)
                Sell.append(np.nan)
        return pd.Series([Buy, Sell])

    
    data['Buy_rsi'], data['Sell_rsi'] = rsi(data)
    data.tail()

    st.markdown('RSI Buy Sell Signal')

    fig, ax = plt.subplots(figsize=(14,8))
    ax.plot(data['Adj Close'] , label = stocksymbols[0] ,linewidth=0.5, color='blue', alpha = 0.9)
    # ax.plot(data['SMA 5'], label = 'SMA5', alpha = 0.85)
    # ax.plot(data['SMA 20'], label = 'SMA20' , alpha = 0.85)
    ax.scatter(data.index , data['Buy_rsi'] , label = 'Buy' , marker = '^', color = 'green',alpha =1 )
    ax.scatter(data.index , data['Sell_rsi'] , label = 'Sell' , marker = 'v', color = 'red',alpha =1 )
    ax.set_title(stocksymbols[0] + " RSI with buy and sell signals",fontsize=10, backgroundcolor='blue', color='white')
    ax.set_xlabel(f'{startdate} - {end_date}' ,fontsize=18)
    ax.set_ylabel('Adj Close' , fontsize=18)
    legend = ax.legend()
    ax.grid()
    plt.tight_layout()
    plt.show()
    st.pyplot(fig)
   


    stoch = data.ta.stoch(high='High', low='Low', close='Close')
    data=pd.concat([data,stoch],axis=1)
    data.head()

    def Osc(data):
        Buy = []
        Sell = []
        position = False 

        for i in range(len(data)):
            if data['STOCHk_14_3_3'][i] <20 and data['STOCHd_14_3_3'][i]<20:
                if position == False :
                    Buy.append(data['Adj Close'][i])
                    Sell.append(np.nan)
                    position = True
                else:
                    Buy.append(np.nan)
                    Sell.append(np.nan)
            elif data['STOCHk_14_3_3'][i] >80 and data['STOCHd_14_3_3'][i] >80:
                if position == True:
                    Buy.append(np.nan)
                    Sell.append(data['Adj Close'][i])
                    position = False
                else:
                    Buy.append(np.nan)
                    Sell.append(np.nan)
            else:
                Buy.append(np.nan)
                Sell.append(np.nan)
        return pd.Series([Buy, Sell])

    data['Buy_osc'],data['Sell_osc']=Osc(data)

    st.markdown('Stocastic Osciollator Buy Sell Signal')
    fig, ax = plt.subplots(figsize=(14,8))
    ax.plot(data['Adj Close'] , label = stocksymbols[0] ,linewidth=0.5, color='blue', alpha = 0.9)
    # ax.plot(data['SMA 5'], label = 'SMA5', alpha = 0.85)
    # ax.plot(data['SMA 20'], label = 'SMA20' , alpha = 0.85)
    ax.scatter(data.index , data['Buy_osc'] , label = 'Buy' , marker = '^', color = 'green',alpha =1 )
    ax.scatter(data.index , data['Sell_osc'] , label = 'Sell' , marker = 'v', color = 'red',alpha =1 )
    ax.set_title(stocksymbols[0] + " osc with buy and sell signals",fontsize=10, backgroundcolor='blue', color='white')
    ax.set_xlabel(f'{startdate} - {end_date}' ,fontsize=18)
    ax.set_ylabel('Adj Close' , fontsize=18)
    legend = ax.legend()
    ax.grid()
    plt.tight_layout()
    st.pyplot(fig)
    



    w=pd.DataFrame(data['Buy_Signal_price'].dropna())
    w.reset_index(inplace=True)
    x=pd.DataFrame(data['Sell_Signal_price']).dropna()
    x.reset_index(inplace=True)

    a=[]
    if w['Date'].iloc[-1]>x['Date'].iloc[-1]:
        a.append('Buy')
    else:
        a.append('Sell')


    w=pd.DataFrame(data['MACD_Buy_Signal_price'].dropna())
    w.reset_index(inplace=True)
    x=pd.DataFrame(data['MACD_Sell_Signal_price']).dropna()
    x.reset_index(inplace=True)


    if w['Date'].iloc[-1]>x['Date'].iloc[-1]:
        a.append('Buy')
    else:
        a.append('Sell')


    w=pd.DataFrame(data['bb_Buy_Signal_price'].dropna())
    w.reset_index(inplace=True)
    x=pd.DataFrame(data['bb_Sell_Signal_price']).dropna()
    x.reset_index(inplace=True)


    if w['Date'].iloc[-1]>x['Date'].iloc[-1]:
        a.append('Buy')
    else:
        a.append('Sell')

    
    w=pd.DataFrame(data['Buy_rsi'].dropna())
    w.reset_index(inplace=True)
    x=pd.DataFrame(data['Sell_rsi']).dropna()
    x.reset_index(inplace=True)


    if w['Date'].iloc[-1]>x['Date'].iloc[-1]:
        a.append('Buy')
    else:
        a.append('Sell')


    w=pd.DataFrame(data['Buy_osc'].dropna())
    w.reset_index(inplace=True)
    x=pd.DataFrame(data['Sell_osc']).dropna()
    x.reset_index(inplace=True)


    if w['Date'].iloc[-1]>x['Date'].iloc[-1]:
        a.append('Buy')
    else:
        a.append('Sell')


    b=['SMA(5x20)','MACD','BB','RSI','SO']


    df=pd.DataFrame(a,b)
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Strategy',0:'Signal'},inplace=True)
    df.set_index('Strategy',inplace=True)


    st.dataframe(df)


    









