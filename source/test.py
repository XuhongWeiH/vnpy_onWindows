from jqdatasdk import *
import pandas as pd
from datetime import datetime
import re
auth('13122192187', 'w19940306')
# 查询是否连接成功
is_auth = is_auth()
print(is_auth)

get_query_count()
funture_list = get_all_securities(types=['futures'], date=None)
funture_list.index

# trade_day = get_trade_days(start_date=datetime(2018, 1, 16, 23, 44, 55), end_date=datetime.today(), count=None)
# trade_day = get_all_trade_days()

for symbol in funture_list.index:
    price_data = get_price(symbol, \
        # start_date=funture_list.loc[symbol]['start_date'], \
        end_date=funture_list.loc[symbol]['end_date'], 
        frequency='1d', 
        fields=['open', 'close', 'low', 'high', 'volume', 'money', 'factor', 'high_limit','low_limit', 'avg', 'pre_close', 'paused', 'open_interest'],\
        skip_paused=False, fq='pre', count=4, panel=True, fill_paused=True)


    price_data
    # domain_future = get_dominant_future(re.findall(r"^[A-Za-z]*", symbol))