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

with open("PARA\Information.json", encoding='utf-8') as fr:
    information_future = json.loads(fr.read())
    information_future = information_future['ITEM']


def write_list_to_json(list_in, json_file_name, json_file_save_path):   
     """    
     将list写入到json文件    
     :param list:    
     :param json_file_name: 写入的json文件名字    
     :param json_file_save_path: json文件存储路径    
     :return:    
     """    
     os.chdir(json_file_save_path)    
     with open(json_file_name, 'w') as  f:        
         json.dump(list_in, f)


for k in information_future.keys():
    print('优化:' + k)
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
    engine.calculate_statistics()
    # engine.show_chart()

    setting = OptimizationSetting()
    setting.set_target("daily_return")
    setting.add_parameter("entry_window", 5, 40, 1)
    setting.add_parameter("exit_window", 5, 40, 1)
    setting.add_parameter("atr_window", 10, 35, 1)
    setting.add_parameter("fixed_size", 1, 2, 1)
    setting.add_parameter("stop_rate", 0.1, 2.5, 0.1)
    setting.add_parameter("add_rate", 0.1, 2.5, 0.1)

    result = engine.run_ga_optimization(setting)

    write_list_to_json([k, result], k, 'PARA/future_op_para')
    print('优化结束:' + k)
    sleep(2)
    

# trades = engine.trades
# for value in trades.values():
#     print("时间:",value.datetime,value.direction.value,value.offset.value, "价格：",value.price, "数量：",value.volume)
#     if value.offset.value == "平":
#         print("---------------------------------------------------------")
