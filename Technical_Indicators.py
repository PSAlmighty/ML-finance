__author__ = "Hitesh Gulati"

import pandas as pd
import numpy as np
import math
import random
import os
import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import statsmodels.api as sm
import talib

Adj_Close = "Adj Close"
High = "High"
Low = "Low"
Close = "Close"
Open = "Open"
Volume = "Volume"
Date = "Date"
Uptrend = "Uptrend"
Downtrend = "Downtrend"
Notrend = "Notrend"
Buy = "Buy"
Sell = "Sell"
Hold = "Hold"
Strong_Volume = "Strong Volume"
Weak_Volume = "Weak Volume"
Trend_Points1 = '1'
Trend_Points2 = '2'
Trend_Points3 = '3'
Trend_Points4 = '4'
Trend_Points5 = '5'
list_of_stocks_filename = "summary_file.csv"

def symbol_to_path (symbol, data_dir = 'data'):
    return  os.path.join ( data_dir, '{}.csv'.format(symbol))

# Get data of single stock by passing symbol and dates from data directory
def get_data (symbol, dates):
    df = pd.DataFrame(index=dates)
    df_temp = pd.read_csv (symbol_to_path(symbol),index_col=Date, parse_dates=True, na_values=['nan'])
    df = df.join(df_temp)
    df =df.dropna()
    return df
# Get Adj Close data of list of stocks and combin as one data renaming Adj CLose to Ticker value
def get_close_data (symbols, dates):
    df = pd.DataFrame(index=dates)
    for symbol in symbols:
        df_temp = pd.read_csv (symbol_to_path(symbol),index_col=Date, parse_dates=True, usecols=[Date,Adj_Close], na_values=['nan'])
        df_temp = df_temp.rename(columns={Date: symbol})
        df = df.join(df_temp)
        df =df.dropna()
    return df
# Plot O,H,L,C,AC values or individual values if mentioned
def plot_data(data, title = 'Stock Prices', measure = None):
    if measure is None:
        measure = data.columns.values.tolist()
        measure.remove(Volume)
    ax = data[measure].plot(title=title,fontsize = 12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Prices")
    plt.show()
# Get list of measures to be used as per given standards
def get_measures (data, measures):
    if measures is "All":
        measures = data.columns.values.tolist()
    elif isinstance(measures,basestring):
        measures = [measures]
    elif measures is None:
        measures = [Adj_Close]
    return measures
# alter column names accoring to measure calculated
def alter_column_names (label, data, measures, window):
    new_column_names = {}
    for measure in measures:
        new_column_names[measure] = str(label) + str(window) + "_" + measure
    data = data.rename(columns=new_column_names)
    return data
# return indicator seprately or added to set as requirment
def add_or_not (data, indicator, add_to_data, label="New Value"):
    if add_to_data is False:
        return indicator
    elif add_to_data is True:
        return add_indicator(data,indicator,label)

# Join data set with indicator
def add_indicator (data, indicator, label = "New Value"):
    if indicator is pd.DataFrame:
        return data.join(indicator)
    else:
        data[label] = indicator
# Get Moving Average of mentioned size default 14 and add to data if True
def MA (data, window =14, measures = None, add_to_data = False ):
    measures = get_measures(data, measures)
    indicator = data[measures].rolling(window).mean()
    indicator = alter_column_names("MA", indicator,measures,window )
    return add_or_not(data,indicator,add_to_data,label=measures[0])

# Get Chaikin Money Flow
def CMF (data, window=14, measures = None, add_to_data = False):
    label = "CMF" + str (window)
    money_flow_multiplier = ((data[Close]-data[Low])-(data[High]-data[Close]))/(data[High]-data[Low])
    money_flow_volume = money_flow_multiplier * data[Volume]
    new_data = data.copy()
    new_data["Money Flow Volume"] = money_flow_volume
    Chaikin_Money_Flow = (new_data["Money Flow Volume"].rolling(window).sum())/(new_data[Volume].rolling(window).sum())
    return add_or_not(data,Chaikin_Money_Flow,add_to_data,label=label)

# Money Flow Index
def MFI(data, window=14, measures = None, add_to_data = False):
    label = "MFI" + str (window)
    typical_price = (data[High] + data [Low] + data [Close])/3
    raw_money_flow = typical_price * data[Volume]
    new_data = data.copy()
    new_data["Typical Price"] = typical_price
    new_data ["Raw Money Flow"] = raw_money_flow
    new_data ["PosMF"] = raw_money_flow
    new_data ["NegMF"] = raw_money_flow * 1
    #print new_data
    i=1
    date = new_data.index [i]

    while i < len(new_data):
        previous_date = new_data.index [i-1]
        if new_data.ix[date,["Typical Price"]][0] >= new_data.ix[previous_date,["Typical Price"]][0]:
            new_data.ix[date,["NegMF"]]  = 0
        else:
            new_data.ix[date, ["PosMF"]] = 0
        if i < len(new_data)-1:
            date = new_data.index[i+1]
        i += 1
    money_flow_ratio = new_data["PosMF"].rolling(window).sum()/new_data["NegMF"].rolling(window).sum()
    new_data["Money Flow Ratio"] =  money_flow_ratio
    money_flow_index = 100 - (100/(1+money_flow_ratio))
    new_data["Money Flow Index"]= money_flow_index
    return add_or_not(data,money_flow_index,add_to_data,label= label)
# Accumulaion/Distribution Line
def ADL (data, window=1, measures = None, add_to_data = False):
    label = "ADL" + str(window)
    money_flow_multiplier = ((data[Close] - data[Low]) - (data[High] - data[Close])) / (data[High] - data[Low])
    money_flow_volume = money_flow_multiplier * data[Volume]
    adl = money_flow_volume.copy()
    i = window
    while i < len(adl):
        adl [i] = money_flow_volume[i] + adl[i-window]
        i += 1
    #print adl
    return add_or_not(data,adl,add_to_data,label = label)

#Average True Range
def ATR (data, window=14, measures = None, add_to_data = False):
    label = "ATR" + str(window)
    HminusL = data[High] - data [Low]
    HminusCp = abs(data[High] - data[Close].shift(1))
    LminusCp = abs(data[Low]-data[Close].shift(1))
    true_range = HminusL
    i = 1
    while i < len(true_range):
        true_range[i] = max (HminusL[i],HminusCp[i],LminusCp[i])
        i += 1
    i = window
    adr = true_range.rolling(window).mean()
    while i< len(adr):
        adr[i] = (adr[i-1]*(window-1) + true_range[i])/window
        i += 1
    return add_or_not(data,adr,add_to_data,label = label)

def absolute_sum (data):
    absolute_data = np.absolute(data)
    return absolute_data.sum()

#Hodrick-Prescott Filter. Returns the trend Uptrend, Downtrend or Notrend
def HP_trend_agent (data, window =14, measures = Adj_Close, add_to_data = False):
    label = "HPtrend_agent" + str(window)
    lamb = 5000
    cycle_value, trend_value = sm.tsa.filters.hpfilter(data[Adj_Close],lamb)
    trend_value_firstdiff = trend_value - trend_value.shift(1)
    trend_string = [Downtrend for x in range(len(trend_value))]
    trend = np.array(trend_string)
    i = window
    trend_variation = trend_value_firstdiff.rolling(window).std() / trend_value_firstdiff.rolling(window).mean()
    trend_sum = trend_value_firstdiff.rolling(window).sum()
    trend_abs_sum = trend_value_firstdiff.rolling(window).apply(absolute_sum)
    while i < len (trend):
        if trend_variation[i] <= .05:
            if  trend_sum[i] == trend_abs_sum[i]:
                trend[i]= Uptrend
            elif trend_sum[i] == -trend_abs_sum[i]:
                trend[i]= Downtrend
        else:
            trend[i] = Notrend
        i += 1
    return add_or_not(data,trend,add_to_data=add_to_data, label =label)

#Stochastic Agent. Returns Buy, Sell or Hold.
def stochastic_agent (data, window =5, measures = Adj_Close, add_to_data = False):
    label = "stochastic_agent" + str(window)
    slowk, slowd = talib.STOCH (data[High].values, data[Low].values, data[Close].values,fastk_period=window)
    stochastic_string = [Hold for x in range(len(data))]
    stochastic_signal = np.array(stochastic_string)
    i = window
    while i < len(stochastic_signal):
        if slowk[i-1] < slowd[i-1] and slowd[i-1] < 20:
            if slowd[i] < slowk[i] and slowk[i] < 20:
                stochastic_signal[i] = Buy
        elif slowk[i-1] > slowd[i-1] and slowd[i-1] > 80:
            if slowd[i] > slowk[i] and slowk[i] > 80:
                stochastic_signal[i]= Sell
        i += 1
    return add_or_not(data,stochastic_signal,add_to_data=add_to_data,label=label)
    # return add_or_not(data,stochastic_agent,add_to_data=add_to_data, label =label)



#Moving Average Crossover Agent. Returns Buy, Sell or Hold.
def MAC_agent (data, window =14, measures = Adj_Close, add_to_data = False):
    label = "MAC_agent" + str(window)
    short_window = window
    long_window = ((window/7)/2)*35
    short_moving_average = data[measures].rolling(short_window).mean()
    long_moving_average = data[measures].rolling(long_window).mean()
    MAC_string = [Hold for x in range(len(data))]
    MAC_signal = np.array(MAC_string)
    i = long_window
    while i < len(MAC_signal):
        if short_moving_average[i-1] < long_moving_average[i-1]:
            if short_moving_average[i] > long_moving_average[i]:
                MAC_signal[i] = Buy
        elif short_moving_average[i-1] > long_moving_average[i-1]:
            if short_moving_average[i] < long_moving_average [i]:
                MAC_signal[i] = Sell
        i += 1
    return add_or_not(data,MAC_signal,add_to_data=add_to_data, label = label)

#Volume Agent. Returns Strong Volume or Weak Volume
def volume_agent (data, window =14, measures = Volume, add_to_data = False):
    label = "volume_agent" + str(window)
    long_window = window
    short_window = (long_window /7)+1
    short_moving_average = data[measures].rolling(short_window).mean()
    long_moving_average = data[measures].rolling(long_window).mean()
    volume_string = [Strong_Volume for x in range(len(data))]
    volume_signal = np.array(volume_string)
    i = long_window
    while i < len(volume_signal):
        if long_moving_average[i] > short_moving_average[i]:
            volume_signal[i] = Weak_Volume
        i += 1
    return add_or_not(data,volume_signal,add_to_data=add_to_data,label=label)

def ADX_agent (data, window =14, measures = Adj_Close, add_to_data = False):
    label = "ADX_agent" + str(window)
    ADX = talib.ADX(data[High].values,data[Low].values,data[Low].values,timeperiod=window)
    trend_string = [Trend_Points1 for x in range(len(data))]
    trend_signal = np.array(trend_string)
    i = window
    while i < len(trend_signal):
        if ADX[i] < 20:
            trend_signal[i] = Trend_Points1
        elif ADX[i] <30:
            trend_signal[i] = Trend_Points2
        elif ADX[i] < 40:
            trend_signal[i] = Trend_Points3
        elif ADX[i] < 50:
            trend_signal[i] = Trend_Points4
        elif ADX[i] < 100:
            trend_signal[i] = Trend_Points5
        i += 1
    return add_or_not(data,trend_signal,add_to_data=add_to_data,label=label)
# Candlestick agent. Returns Buy, Sell or Hold.
def Candlestick_agent (data, window =14, measures = Adj_Close, add_to_data = False):
    label = "Candlestick_agent"
    indicators = {}
    indicators['sum'] = 0
    indicators['hammer']= talib.CDLHAMMER(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['engulfing'] = talib.CDLENGULFING(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['hangingman'] = talib.CDLHANGINGMAN(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['threewhitesoldiers'] = talib.CDL3WHITESOLDIERS(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['threeblackcrows'] = talib.CDL3BLACKCROWS(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['threeinside'] = talib.CDL3INSIDE(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['eveningstar'] = talib.CDLEVENINGSTAR(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['morningstar'] = talib.CDLMORNINGSTAR(data[Open].values,data[High].values,data[Low].values,data[Close].values)
    indicators['threeoutside'] = talib.CDL3OUTSIDE(data[Open].values,data[High].values,data[Low].values,data[Close].values)

    for value in indicators:
        indicators['sum'] += indicators[value]
    CDL_string = [Hold for x in range(len(data))]
    CDL_signal = np.array(CDL_string)
    i =0
    while i < len(CDL_signal):
        if indicators['sum'][i] > 0:
            CDL_signal[i] = Buy
        elif indicators['sum'][i] < 0:
            CDL_signal[i] = Sell
        i += 1
    return add_or_not(data,CDL_signal,add_to_data=add_to_data,label=label)

def make_indicator_files ():
    summary_file_name = "data/" + list_of_stocks_filename
    ticker_file = pd.read_csv(summary_file_name)
    for i in range(0,len(ticker_file)):
        company_name = ticker_file['Company_Name'][i]
        company_ticker = ticker_file['Ticker'][i]
        symbol = company_ticker
        df = get_data(symbol, pd.date_range('2006-1-1', '2014-1-1'))
        print "Data Read for: ", company_name , " - ", company_ticker
        HP_trend_agent(df, add_to_data=True)
        MAC_agent(df, add_to_data=True)
        stochastic_agent(df, add_to_data=True)
        volume_agent(df, add_to_data=True)
        ADX_agent(df, add_to_data=True)
        Candlestick_agent(df, add_to_data=True)
        print "Indicators made for: ", company_name, " - ", company_ticker
        columns = df.columns.values.tolist()
        # columns.insert(0, 'Date')
        df.to_csv(symbol_to_path("i_"+symbol),index_label="Date")
        print "File made: i_",symbol
    print "Done!"

def run():
    # Run function which is called from main.
    # symbol = 'BBW'
    # print symbol_to_path(symbol)
    # df = get_data(symbol, pd.date_range('2012-1-1', '2012-04-1'))
    # print "Data Read"
    #print df
    #df =  MA(df, window =14, add_to_data=True)
    #plot_data(df, measure=[Adj_Close,'MA14_Adj Close'])
    #CMF(df,add_to_data=True,window=20)
    #print df
    # plot_data(df, measure="CMF14")
    #MFI (df, add_to_data= True)
    #plot_data(df, measure= ["Adj Close","MFI14"])
    #ADL(df,add_to_data=True)
    #print df
    # ATR(df,add_to_data=True)
    # plot_data(df,measure="ATR14")
    # summary_file_name = "data/summary_file.csv"
    # ticker_file = pd.read_csv(summary_file_name)
    # for i in range(0,len(ticker_file)):
    #     company_name = ticker_file['Company_Name'][i]
    #     company_ticker = ticker_file['Ticker'][i]
    #     symbol = company_ticker
    #     df = get_data(symbol, pd.date_range('2006-1-1', '2012-11-1'))
    #     print "Data Read for: ", company_name , " - ", company_ticker
    #     trend = trend_agent(df)
    # print "Done!"
    # print HP_trend_agent(df,add_to_data=True)
    # print df.head()
    # print df.tail()
    # volume_agent(df,14,add_to_data=True)
    # print df
    # HP_trend_agent(df,add_to_data=True)
    # MAC_agent(df,add_to_data=True)
    # stochastic_agent(df,add_to_data=True)
    # volume_agent(df,add_to_data=True)
    # ADX_agent(df,add_to_data=True)
    # Candlestick_agent(df,add_to_data=True)
    # columns = df.columns.values.tolist()
    # columns.insert(0,'Date')
    # print columns
    make_indicator_files()

if __name__ == '__main__':
    run()
