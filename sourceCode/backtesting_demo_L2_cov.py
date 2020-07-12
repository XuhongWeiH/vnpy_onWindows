import sys
sys.path.append('.')
import os
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.base import BacktestingMode
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy_improve import (
    TurtleSignalStrategyImprove
)
from datetime import datetime
import json
from time import time, sleep
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import sys, os
import math
import numpy as np

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

with open("PARA\Information.json", encoding='utf-8') as fr:
    information_future = json.loads(fr.read())
    information_future = information_future['ITEM']

with open("D:/vnpy-2.1.2/vnpy-2.1.2/PARA/trade_type/trade_list.json", encoding='utf-8') as fr:
    trade_list = json.loads(fr.read())
    trade_list = trade_list['tradeable']

with open("D:/vnpy-2.1.2/vnpy-2.1.2/PARA/trade_balance/result.json", encoding='utf-8') as fr:
    trade_result_list = json.loads(fr.read())

def write_list_to_json(list_in, json_file_name, json_file_save_path):   
    """    
    将list写入到json文件    
    :param list:    
    :param json_file_name: 写入的json文件名字    
    :param json_file_save_path: json文件存储路径    
    :return:    
    """    
    path = os.getcwd()
    os.chdir(json_file_save_path)    
    with open(json_file_name, 'w') as  f:        
        json.dump(list_in, f)
    os.chdir(path)  

result:dict = {}
data_close_price = pd.DataFrame()
for k in trade_list:

    print('测试:' + k)  
    blockPrint()#关闭output   
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=k,
        interval="1d",
        start=datetime(2000, 1, 4),
        end=datetime(2020, 6, 8),
        rate=0.5/10000,
        slippage=5,
        size=information_future[k]['size_line'],
        pricetick=information_future[k]['pricetick_line'],
        capital=1_000_000,
        mode=BacktestingMode.BAR
    )
    engine.add_strategy(TurtleSignalStrategyImprove, {})
    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()

    enablePrint()#打开output 
    if len(df['close_price']) > 1300:
        data_close_price[k] = df['close_price']
    else:
        print(k + '因为时间太短没有记录在案')

data_close_price.dropna()
data_close_price_norm_minmax=data_close_price.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
cov_mx = data_close_price_norm_minmax.cov()
cov_mx.to_csv(path_or_buf='D:/vnpy-2.1.2/vnpy-2.1.2/PARA/trade_balance/cov_mx.csv')
# trades = engine.trades
# for value in trades.values():
#     print("时间:",value.datetime,value.direction.value,value.offset.value, "价格：",value.price, "数量：",value.volume)
#     if value.offset.value == "平":
#         print("---------------------------------------------------------")
