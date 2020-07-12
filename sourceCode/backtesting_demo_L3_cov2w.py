import json
import math
import os
import sys
from datetime import datetime
from time import sleep, time

sys.path.append('.')
import matplotlib.pyplot as plt  # 绘图
import numpy as np
import pandas as pd
import plotly.graph_objects as go
#最优化投资组合的推导是一个约束最优化问题
import scipy.optimize as sco
import scipy.stats as scs  # 科学计算
from plotly.subplots import make_subplots

import statsmodels.api as sm  # 统计运算
from vnpy.app.cta_strategy.backtesting import (BacktestingEngine,
                                               OptimizationSetting)
from vnpy.app.cta_strategy.base import BacktestingMode
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy_improve import \
    TurtleSignalStrategyImprove


with open("D:/vnpy-2.1.2/vnpy-2.1.2/PARA/trade_type/trade_list.json", encoding='utf-8') as fr:
    trade_list = json.loads(fr.read())
    trade_list = trade_list['tradeable']

with open("D:/vnpy-2.1.2/vnpy-2.1.2/PARA/trade_balance/result.json", encoding='utf-8') as fr:
    trade_result_list = json.loads(fr.read())

cov_mx =pd.read_csv(filepath_or_buffer='D:/vnpy-2.1.2/vnpy-2.1.2/PARA/trade_balance/cov_mx.csv',index_col=0)

returns_E = pd.DataFrame(index = trade_list, columns = ['exp'])
returns_v = cov_mx
returns_R = pd.DataFrame(index = trade_list, columns = ['res'])
for k in trade_list:
    returns_E.loc[k] = trade_result_list[k]['annual_return']



def statistics(weights):
    weights = np.array(weights)
    port_returns = np.sum(returns_E['exp']*weights)
    port_variance = np.sqrt(np.dot(weights.T, np.dot(returns_v, weights)))
    return np.array([port_returns, port_variance, port_returns/port_variance])
#最小化夏普指数的负值
def min_sharpe(weights):
    return -statistics(weights)[2]
def min_variance(weights):
    return statistics(weights)[1]

noa = len(trade_list)
weights = np.random.random(noa)
weights /= np.sum(weights)

#约束是所有参数(权重)的总和为1。这可以用minimize函数的约定表达如下
cons = ({'type':'eq', 'fun':lambda x: np.sum(x)-1})
#我们还将参数值(权重)限制在0和1之间。这些值以多个元组组成的一个元组形式提供给最小化函数
bnds = tuple((0,1) for x in range(noa))
#优化函数调用中忽略的唯一输入是起始参数列表(对权重的初始猜测)。我们简单的使用平均分布。

opts = sco.minimize(min_sharpe, noa*[1./noa,], method = 'SLSQP', bounds = bnds, constraints = cons)
# returns_R['res'] = opts['x'].round(3)
# statistics(opts['x']).round(3)
optv = sco.minimize(min_variance, noa*[1./noa,],method = 'SLSQP', bounds = bnds, constraints = cons)

#在不同目标收益率水平（target_returns）循环时，最小化的一个约束条件会变化。
target_returns = np.linspace(0.0,50,100)
target_variance = []
for tar in target_returns:
    cons = ({'type':'eq','fun':lambda x:statistics(x)[0]-tar},{'type':'eq','fun':lambda x:np.sum(x)-1})
    res = sco.minimize(min_variance, noa*[1./noa,],method = 'SLSQP', bounds = bnds, constraints = cons)
    target_variance.append(res['fun'])
target_variance = np.array(target_variance)

returns_R['res'] = res['x'].round(3)
statistics(res['x']).round(3)

port_returns = []
port_variance = []
for p in range(4000):
    weights = np.random.random(noa)
    weights /=np.sum(weights)
    port_returns.append(np.sum(returns_E['exp']*weights))
    port_variance.append(np.sqrt(np.dot(weights.T, np.dot(returns_v, weights))))
port_returns = np.array(port_returns)
port_variance = np.array(port_variance)
#无风险利率设定为4%
risk_free = 0.03
plt.figure(figsize = (8,4))
plt.scatter(port_variance, port_returns, c=(port_returns-risk_free)/port_variance, marker = 'o')
plt.grid(True)
plt.xlabel('excepted volatility')
plt.ylabel('expected return')
plt.colorbar(label = 'Sharpe ratio')
plt.show()

plt.figure(figsize = (8,4))
#圆圈：蒙特卡洛随机产生的组合分布
plt.scatter(port_variance, port_returns, c = port_returns/port_variance,marker = 'o')
#叉号：有效前沿
plt.scatter(target_variance,target_returns, c = target_returns/target_variance, marker = 'x')
#红星：标记最高sharpe组合
plt.plot(statistics(opts['x'])[1], statistics(opts['x'])[0], 'r*', markersize = 6.0)
#黄星：标记最小方差组合
plt.plot(statistics(optv['x'])[1], statistics(optv['x'])[0], 'y*', markersize = 6.0)
plt.grid(True)
plt.xlabel('expected volatility')
plt.ylabel('expected return')
plt.colorbar(label = 'Sharpe ratio')
plt.show()




