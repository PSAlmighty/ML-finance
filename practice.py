from yahoo_finance import Share
from pprint import pprint
import pandas as pd
import numpy as np

symbol_file_name = "nasdaq_retail.csv"
symbol = 'BBY'
share = Share(symbol)

print share.get_change()
print share.get_dividend_pay_date()
historical_prices = share.get_historical('2016-12-08', '2016-12-12')
print type(historical_prices)
print type (historical_prices[0])
pprint(historical_prices)
pprint(historical_prices[0])

