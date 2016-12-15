import pandas as pd
import numpy as np
import math
import random
import os
import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime
from datetime import timedelta

Adj_Close = "Adj Close"
High = "High"
Low = "Low"
Close = "Close"
Open = "Open"
Volume = "Volume"
Date = "Date"
Money_Flow_Volume = "Money Flow Volume"

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
# Get Moving Average o mentioned size default 14 and add to data if True
def MA (data, window =14, measures = None, add_to_data = False ):
    measures = get_measures(data, measures)
    indicator = data[measures].rolling(window).mean()
    indicator = alter_column_names("MA", indicator,measures,window )
    return add_or_not(data,indicator,add_to_data,label=measures[0])

# Get Chaikin Money Flow
def CMF (data, window=14, measures = None, add_to_data = False):
    label = "CMF" + str (window)
    money_flow_multiplier = ((data[Close]-data[Low])-(data[High]))/(data[High]-data[Low])
    money_flow_volume = money_flow_multiplier * data[Volume]
    new_data = data.copy()
    new_data[Money_Flow_Volume] = money_flow_volume
    Chaikin_Money_Flow = (new_data[Money_Flow_Volume].rolling(window).sum())/(new_data[Volume].rolling(window).sum())
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

def run():
    # Run function which is called from main.
    print symbol_to_path('AMZN')
    df = get_data("AMZN", pd.date_range('2009-1-1','2014-1-1'))
    print "Data Read"
    #print df
    #df =  MA(df, window =14, add_to_data=True)
    #plot_data(df, measure=[Adj_Close,'MA14_Adj Close'])
    # CMF(df,add_to_data=True)
    # print df
    # plot_data(df, measure="CMF14")
    MFI (df, add_to_data= True)
    plot_data(df, measure= ["Adj Close","MFI14"])



if __name__ == '__main__':
    run()
