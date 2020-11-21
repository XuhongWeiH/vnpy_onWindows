# encoding: UTF-8

"""
立即下载数据到数据库中，用于手动执行更新操作。
"""


import sys
sys.path.insert(0,'.')
sys.path.insert(0,'..')

from datetime import datetime
from vnpy.trader.utility import load_json, save_json
from dataService import *

SETTING_FILENAME: str = "vt_setting.json"
setting_data = load_json(SETTING_FILENAME)
setting_data["database.database"] = "VnTrader_Db"
save_json(SETTING_FILENAME, setting_data)
#!在F:\vnpy-2.1.2\Data_recorder\config.json中更改JQDATA用户名密码
if __name__ == '__main__':
    # 每日任务下载
    # downloadAllMinuteBar()

    # 按日期补齐数据
    # downloadBarByDate(end_date=datetime(2020, 11, 20), download_mode = 'daily')
    downloadBarByDate(end_date=datetime(2020, 11, 20), download_mode = '1Min')

    # 按合约列表和日期补齐数据
    # downloadSymbolBarByDate(['I8888', 'CU8888'], '2010-01-01')