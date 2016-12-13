from yahoo_finance import Share
from pprint import pprint
import pandas as pd
import numpy as np

symbol_file_name = "nasdaq_retail.csv"
symbol = 'AAPL'
share = Share(symbol)

print share.get_change()
print share.get_dividend_pay_date()

print type(share.get_historical('2016-12-01','2016-12-12'))

