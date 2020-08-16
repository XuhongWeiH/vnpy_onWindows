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

def show_chart(df):
    fig = make_subplots(rows=4, cols=1, subplot_titles=["Balance", "Drawdown", "Daily Pnl", "Pnl Distribution"], vertical_spacing=0.06)

    # 第一张：账户净值子图，用折线图来绘制
    fig.add_trace(go.Line(x=df.index, y=df["balance"], name="Balance"), row=1, col=1)

    # 第二张：最大回撤子图，用面积图来绘制
    fig.add_trace(go.Scatter(x=df.index, y=df["drawdown"], fillcolor="red", fill='tozeroy', line={"width": 0.5, "color": "red"}, name="Drawdown"), row=2, col=1)

    # 第三张：每日盈亏子图，用柱状图来绘制
    fig.add_trace(go.Bar(y=df["net_pnl"], name="Daily Pnl"), row=3, col=1)

    # 第四张：盈亏分布子图，用直方图来绘制
    fig.add_trace(go.Histogram(x=df["net_pnl"], nbinsx=100, name="Days"), row=4, col=1)

    # 把图表放大些，默认小了点
    fig.update_layout(height=1000, width=1000)

    # 将绘制完的图表，正式显示出来
    fig.show()

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
    with open("D:/vnpy-2.1.2/vnpy-2.1.2/PARA/future_op_para/" + k, encoding='utf-8') as fr:
        future_para = json.loads(fr.read())
        
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
    # engine.run_backtesting()
    # df = engine.calculate_result()
    # engine.calculate_statistics()
    # engine.show_chart()
    # show_chart(df)

    setting = OptimizationSetting()
    setting.set_target("daily_return")
    setting.add_parameter("entry_window", future_para[1][0][0]['entry_window']-8, future_para[1][0][0]['entry_window']+8, 1)
    setting.add_parameter("exit_window", future_para[1][0][0]['exit_window']-8, future_para[1][0][0]['exit_window']+8, 1)
    setting.add_parameter("atr_window", future_para[1][0][0]['atr_window']-8, future_para[1][0][0]['atr_window']+8, 1)
    setting.add_parameter("fixed_size", 1, 2, 1)
    setting.add_parameter("stop_rate", future_para[1][0][0]['stop_rate']-8, future_para[1][0][0]['stop_rate']+8, 1)
    setting.add_parameter("add_rate", future_para[1][0][0]['add_rate']-8, future_para[1][0][0]['add_rate']+8, 1)

    result = engine.run_ga_optimization(setting)

    write_list_to_json([k, result], k, 'D:/vnpy-2.1.2/vnpy-2.1.2/PARA/future_op_para_refine')#必须绝对路径应为os.chdir
    print('优化结束:' + k)
    sleep(2)
    

# trades = engine.trades
# for value in trades.values():
#     print("时间:",value.datetime,value.direction.value,value.offset.value, "价格：",value.price, "数量：",value.volume)
#     if value.offset.value == "平":
#         print("---------------------------------------------------------")
