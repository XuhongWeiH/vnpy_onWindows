# encoding: UTF-8

from __future__ import print_function
import sys
import json
from datetime import datetime, timedelta
from time import time, sleep
import math

from pymongo import MongoClient, ASCENDING


import sys
sys.path.insert(0,'.')
sys.path.insert(0,'..')
from vnpy.trader.vtTrader.vtObject import VtBarData
from vnpy.trader.vtTrader.app.ctaStrategy.ctaBase import MINUTE_DB_NAME, DAILY_DB_NAME
from tqdm import tqdm
import jqdatasdk
import re

# 加载配置
config = open('Data_recorder\config.json')
setting = json.load(config)

MONGO_HOST = setting['MONGO_HOST']
MONGO_PORT = setting['MONGO_PORT']
JQDATA_USER = setting['JQDATA_USER']
JQDATA_PASSWORD = setting['JQDATA_PASSWORD']

mc = MongoClient(MONGO_HOST, MONGO_PORT)        # Mongo连接
minute_db = mc[MINUTE_DB_NAME]                  # 分钟数据库
daily_db = mc[DAILY_DB_NAME]                    # 日线数据库

#----------------------------------------------------------------------
# 生成日Bar
def generateDailyVtBar(symbol, date, d):
    """生成K线"""
    bar = VtBarData()
    try:
        bar.gatewayName = re.findall(r"^[A-Za-z]*", symbol)[0]
        bar.symbol = symbol
        bar.exchange = symbol.split('.')[-1]

        bar.open_price = float(d['open'])             # OHLC
        bar.close_price = float(d['close'])
        bar.low_price = float(d['low'])
        bar.high_price = float(d['high'])
        bar.low_limit = float(d['low_limit'])
        bar.high_limit = float(d['high_limit'])
        
        bar.factor = float(d['factor'])
        bar.avg = float(d['avg'])
        bar.pre_close = float(d['pre_close'])
        bar.paused = float(d['paused'])
        
        bar.datetime = date                # python的datetime时间对象
        
        bar.volume = int(d['volume'])             # 成交量
        bar.money = float(d['money'])            #交易额
        bar.open_interest = float(d['open_interest'])        # 持仓量  
        bar.interval = '1d'       # K线周期
    except ValueError as e:
        pass
        for k in d.keys():
            if math.isnan(d[k]):
                d[k] = 0
        bar.gatewayName = re.findall(r"^[A-Za-z]*", symbol)[0]
        bar.symbol = symbol
        bar.exchange = symbol.split('.')[-1]

        bar.open_price = float(d['open'])             # OHLC
        bar.close_price = float(d['close'])
        bar.low_price = float(d['low'])
        bar.high_price = float(d['high'])
        bar.low_limit = float(d['low_limit'])
        bar.high_limit = float(d['high_limit'])
        
        bar.factor = float(d['factor'])
        bar.avg = float(d['avg'])
        bar.pre_close = float(d['pre_close'])
        bar.paused = float(d['paused'])
        
        bar.datetime = date                # python的datetime时间对象
        
        bar.volume = int(d['volume'])             # 成交量
        bar.money = float(d['money'])            #交易额
        bar.open_interest = float(d['open_interest'])        # 持仓量  
        bar.interval = '1d'       # K线周期
        print(bar.gatewayName + '修复0')

    return bar

#----------------------------------------------------------------------
# 生成分钟Bar
def generateMinuteVtBar(symbol, time, d):
    """生成K线"""
    bar = VtBarData()
    try:
        bar.gatewayName = re.findall(r"^[A-Za-z]*", symbol)[0]
        bar.symbol = symbol
        bar.exchange = symbol.split('.')[-1]

        bar.open_price = float(d['open'])             # OHLC
        bar.close_price = float(d['close'])
        bar.low_price = float(d['low'])
        bar.high_price = float(d['high'])
        bar.low_limit = float(d['low_limit'])
        bar.high_limit = float(d['high_limit'])
        
        bar.factor = float(d['factor'])
        bar.avg = float(d['avg'])
        bar.pre_close = float(d['pre_close'])
        bar.paused = float(d['paused'])
        
        bar.datetime = time                # python的datetime时间对象
        
        bar.volume = int(d['volume'])             # 成交量
        bar.money = float(d['money'])            #交易额
        bar.open_interest = float(d['open_interest'])        # 持仓量  
        bar.interval = '1d'       # K线周期
    except ValueError as e:
        pass
        for k in d.keys():
            if math.isnan(d[k]):
                d[k] = 0
        bar.gatewayName = re.findall(r"^[A-Za-z]*", symbol)[0]
        bar.symbol = symbol
        bar.exchange = symbol.split('.')[-1]

        bar.open_price = float(d['open'])             # OHLC
        bar.close_price = float(d['close'])
        bar.low_price = float(d['low'])
        bar.high_price = float(d['high'])
        bar.low_limit = float(d['low_limit'])
        bar.high_limit = float(d['high_limit'])
        
        bar.factor = float(d['factor'])
        bar.avg = float(d['avg'])
        bar.pre_close = float(d['pre_close'])
        bar.paused = float(d['paused'])
        
        bar.datetime = time                # python的datetime时间对象
        
        bar.volume = int(d['volume'])             # 成交量
        bar.money = float(d['money'])            #交易额
        bar.open_interest = float(d['open_interest'])        # 持仓量  
        bar.interval = '1d'       # K线周期
        print(bar.gatewayName + '修复0')
    
    return bar

#----------------------------------------------------------------------
# 单合约日线下载并保存到mongodb
def downDailyBarBySymbol(symbol, info, end_date):
    if info[2] < datetime(2005, 1, 3):
        return #JQ数据库不支持此日期前的合约

    # start = time()

    # cl = daily_db[symbol]
    cl = daily_db['jq_db_daily_bar_data'] #!!!!!!!!!!!!!!!!!!!!!!
    cl.ensure_index([('datetime', ASCENDING),('interval', ASCENDING),('symbol', ASCENDING)], unique=True)  # 添加索引

    daily_df = jqdatasdk.get_price(symbol, \
        start_date=info[2], \
        end_date=min(info[3], end_date), \
        frequency='daily', \
        fields=['open', 'close', 'low', 'high', 'volume', 'money', 'factor', 'high_limit','low_limit', 'avg', 'pre_close', 'paused', 'open_interest'],\
        skip_paused=False, fq='pre', count=None, panel=True, fill_paused=True)


    # 将数据传入到数据队列当中
    for index, row in daily_df.iterrows():
        bar = generateDailyVtBar(symbol, index, row)
        d = bar.__dict__
        flt = {'symbol':bar.symbol, 'datetime': bar.datetime, 'interval': bar.interval}#
        cl.replace_one(flt, d, upsert = True)

#----------------------------------------------------------------------
# 单合约分钟线下载并保存到mongodb
def downMinuteBarBySymbol(symbol, info, end_date):
    if info[2] < datetime(2005, 1, 3):
        return #JQ数据库不支持此日期前的合约

    symbol_name = info['display_name']
    cl = minute_db['jq_db_1Min_bar_data'] #!!!!!!!!!!!!!!!!!!!!!!
    cl.ensure_index([('datetime', ASCENDING),('interval', ASCENDING),('symbol', ASCENDING)], unique=True)  # 添加索引

    
    # 在此时间段内可以获取期货夜盘数据
    start_date = info['start_date'] - timedelta(days = 1)
    print('*' * 50)
    print(u'!!!!合约%s数据下载开始!!!' % (symbol_name))
    print('*' * 50)
    start = time()
    with tqdm(total = (end_date - start_date).days) as pbar:
        while start_date < end_date:
            #请求数据
            minute_df = jqdatasdk.get_price(symbol, \
                start_date=(start_date + timedelta(hours=20, minutes = 30)).strftime("%Y-%m-%d %H:%M:%S"), \
                end_date=(start_date + timedelta(days = 1, hours=20, minutes = 30)).strftime("%Y-%m-%d %H:%M:%S"), \
                frequency='minute', \
                fields=['open', 'close', 'low', 'high', 'volume', 'money', 'factor', 'high_limit','low_limit', 'avg', 'pre_close', 'paused', 'open_interest'],\
                skip_paused=False, fq='pre', count=None, panel=True, fill_paused=True)

            # 将数据传入到数据队列当中
            for index, row in minute_df.iterrows():
                bar = generateMinuteVtBar(symbol_name, index, row)
                d = bar.__dict__
                flt = {'symbol':bar.symbol, 'datetime': bar.datetime, 'interval': bar.interval}
                cl.replace_one(flt, d, True)
            
            pbar.set_description("TimeLeft:%d"%(jqdatasdk.get_query_count()['spare']))
            pbar.update(1)
            start_date = start_date + timedelta(days = 1)
    
    cost = (time() - start)
    pbar.close()

    print('-' * 50)
    print(u'!!!!合约%s数据下载完成，耗时%s秒!!!' % (symbol_name, cost))
    print('-' * 50)

#----------------------------------------------------------------------
# 当日数据下载，定时任务使用
def downloadAllMinuteBar():
    jqdatasdk.auth(JQDATA_USER, JQDATA_PASSWORD)
    """下载所有配置中的合约的分钟线数据"""
    print('-' * 50)
    print(u'开始下载合约分钟线数据')
    print('-' * 50)

    today = datetime.today().date()

    trade_date_list = jqdatasdk.get_trade_days(end_date=today, count=2)

    symbols_df = jqdatasdk.get_all_securities(types=['futures'], date=today)
    
    for index, row in symbols_df.iterrows():
        downMinuteBarBySymbol(index, row, str(today), str(trade_date_list[-2]))

    print('-' * 50)
    print(u'合约分钟线数据下载完成')
    print('-' * 50)
    return

#----------------------------------------------------------------------
# 按日期一次性补全数据
def downloadBarByDate(start_date=None, end_date=datetime.today().date(), download_mode = None):
    jqdatasdk.auth(JQDATA_USER, JQDATA_PASSWORD)#登录账号
    """下载所有配置中的合约数据"""
    if not download_mode:
        print("请设置下载模式")
        return

    if download_mode == 'daily':
        print('-' * 50)
        print(u'开始下载日线合约数据')
        print('-' * 50)

        symbols_df = jqdatasdk.get_all_securities(types=['futures'])

        for index, row in symbols_df.iterrows():
            # 下载合约的日线数据
            start = time()
            #!这个最后要去掉
            # if '8888' not in index:
            #     continue
            #!这个最后要去掉
            if row['start_date'] < datetime(2005, 1, 3):
                get_data_spare = jqdatasdk.get_query_count()['spare']
                print('\r' + row['display_name'] + '--Times left: %d; 现在是:%s, '%(get_data_spare,str(datetime.now()).split('.')[0]), end='', flush=True)
                cost_time = (time() - start) 
                print(u'合约%s日线数据不符合JQData2005年后要求，耗时%.5s秒' % (row['name'], cost_time))
                continue
            else:
                downDailyBarBySymbol(index, row, end_date)
                get_data_spare = jqdatasdk.get_query_count()['spare']
                print('\r' + row['display_name'] + '--Times left: %d; 现在是:%s, '%(get_data_spare,str(datetime.now()).split('.')[0]), end='', flush=True)
                cost_time = (time() - start) 
                print(u'合约%s日线数据下载完成，耗时%.5s秒' % (row['name'], cost_time))
                break   
            while get_data_spare < 1e4:
                sleep(2)
                get_data_spare = jqdatasdk.get_query_count()['spare']
                print('\r' + row['display_name'] + row['name'] + '--Times left: %d ;现在是:%s, '%(get_data_spare,str(datetime.now()).split('.')[0]), end='', flush=True)
        print('-' * 50)
        print(u'合约日线数据下载完成')
        print('-' * 50)
            
    if download_mode == '1Min':
        print('-' * 50)
        print(u'开始下载分钟线合约数据')
        print('-' * 50)
        symbols_df = jqdatasdk.get_all_securities(types=['futures'])

        for index, row in symbols_df.iterrows():
            # 下载合约的日线数据
            start = time()
            #! 这个最后要去掉
            # if '8888' not in index:
            #     continue
            #!这个最后要去掉
            if row['start_date'] < datetime(2005, 1, 3):
                get_data_spare = jqdatasdk.get_query_count()['spare']
                print('\r' + row['display_name'] + '--Times left: %d; 现在是:%s, '%(get_data_spare,str(datetime.now()).split('.')[0]), end='', flush=True)
                cost_time = (time() - start) 
                print(u'合约%s的分钟线数据不符合JQData2005年后要求，耗时%.5s秒' % (row['name'], cost_time))
                continue
            else:
                downMinuteBarBySymbol(index, row, end_date)            
                get_data_spare = jqdatasdk.get_query_count()['spare']
                print('\r' + row['display_name'] + '--Times left: %d; 现在是:%s, '%(get_data_spare,str(datetime.now()).split('.')[0]), end='', flush=True)
                cost_time = (time() - start) 
                print(u'合约%s的分钟线数据下载完成，耗时%.5s秒' % (row['name'], cost_time))
                # break   
            while get_data_spare < 1e4:
                sleep(2)
                get_data_spare = jqdatasdk.get_query_count()['spare']
                print('\r' + row['display_name'] + row['name'] + '--Times left: %d ;现在是:%s, '%(get_data_spare,str(datetime.now()).split('.')[0]), end='', flush=True)
        print('-' * 50)
        print(u'合约分钟线数据下载完成')
        print('-' * 50)
        # 下载合约的分钟线数据
        # downMinuteBarBySymbol(index, row, str(trade_date_list[i]), str(trade_date_list[i-1]))

    return

#----------------------------------------------------------------------
# 合约列表补全数据
def downloadSymbolBarByDate(symbols_list, start_date, end_date=datetime.today().date()):
    jqdatasdk.auth(JQDATA_USER, JQDATA_PASSWORD)
    """下载所有配置中的合约的分钟线数据"""
    print('-' * 50)
    print(u'开始下载合约分钟线数据')
    print('-' * 50)

    symbols_map = {}
    for symbol in symbols_list:
        symbols_map[symbol] = 1

    trade_date_list = jqdatasdk.get_trade_days(start_date=start_date, end_date=end_date)

    i = 0
    for trade_date in trade_date_list:
        if i == 0:
            i = 1
            continue

        symbols_df = jqdatasdk.get_all_securities(types=['futures'], date=trade_date)

        for index, row in symbols_df.iterrows():
            if row['name'] in symbols_map.keys():
                # 下载合约的日线数据
                downDailyBarBySymbol(index, row, str(trade_date_list[i - 1]))
                # 下载合约的分钟线数据
                downMinuteBarBySymbol(index, row, str(trade_date_list[i]), str(trade_date_list[i-1]))

        i += 1

    print('-' * 50)
    print(u'合约分钟线数据下载完成')
    print('-' * 50)
    return
    