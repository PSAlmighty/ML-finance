from yahoo_finance import Share
from pprint import pprint
import pandas as pd
import numpy as np
import pandas_datareader as pdr
import pandas_datareader.data as web
from datetime import datetime

ticker_file_name = "data/nasdaq_retail.csv"
summary_file_name = "data/summary_file.csv"
ticker_file = pd.read_csv(ticker_file_name)
ticker_summary_list = []
# print type(ticker_file)
# print ticker_file.columns.values
#ticker_file.drop('Unnamed: 3', axis=1,inplace=True)
# print ticker_file.columns.values
# print ticker_file
# print len(ticker_file)
start = datetime(2009,1,1)
end = datetime(2014,1,1)
print ticker_file['Company Name'][0]
for i in range(0,len(ticker_file)):
    company_name = ticker_file['Company Name'][i]
    company_ticker = ticker_file['Ticker'][i]
    print company_name, company_ticker
    historical_data = pd.DataFrame()
    try:
        historical_data = web.DataReader(company_ticker,data_source='yahoo',start=start,end=end)
        output_file_name = "data/" + company_ticker + ".csv"
        historical_data.to_csv (output_file_name, sep=',')
        ticker_summary = (company_name, company_ticker, len(historical_data))
        ticker_summary_list.append(ticker_summary)
        print ticker_summary
    except pdr._utils.RemoteDataError:
        print "Data Read Error"

ticker_summary_df = pd.DataFrame(ticker_summary_list, columns=['Company_Name', 'Ticker','Number of Entries'])
ticker_summary_df.to_csv(summary_file_name)
# ibm = pd.DataFrame
# ibm = web.DataReader('BBY',data_source='yahoo',start=start,end=end)
# file_name = 'data/out.csv'
# print ibm
# print type(ibm)
# print len(ibm)
# print ibm.ix[end]
# ibm.to_csv(file_name, sep=',')

# symbols = ['IBM', 'BBY']
# pdr.get_data_yahoo('AAPL')
# ibm = pdr.get_data_yahoo(symbols='IBM', start =datetime(2000,1,1), end = datetime(2000,1,5))
# print ibm
# symbol_file_name = "nasdaq_retail.csv"
# symbol = 'BBY'
# share = Share(symbol)
#
# # print share.get_change()
# # print share.get_dividend_pay_date()
# historical_prices = share.get_historical('2016-12-08', '2016-12-12')
# # print type(historical_prices)
# # print type (historical_prices[0])
# #pprint(historical_prices)
# # pprint(historical_prices[0])
# adict = {}
# bdict = {'a2': 22, 'b2': 23, 'c2': 24}
# # print adict
# # print bdict
# # print type(adict)
# # for item in adict:
# #     print adict[item]
# # aSeries = pd.Series(adict)
# # print aSeries
# # print type(aSeries)
# series = pd.Series (data=historical_prices[0])
# df = pd.DataFrame (data=series)
# print series["Date"]
# print df



