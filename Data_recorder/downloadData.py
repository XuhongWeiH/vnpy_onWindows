# encoding: UTF-8

"""
立即下载数据到数据库中，用于手动执行更新操作。
"""

from dataService import *
import sys
sys.path.append('.')

from datetime import datetime
from vnpy.trader.utility import load_json, save_json
SETTING_FILENAME: str = "vt_setting.json"
setting_data = load_json(SETTING_FILENAME)
setting_data["database.database"] = "VnTrader_Daily_Db"
save_json(SETTING_FILENAME, setting_data)

if __name__ == '__main__':
    # 每日任务下载
    # downloadAllMinuteBar()

    # 按日期补齐数据
    downloadBarByDate(end_date=datetime(2019, 1, 1))

    # 按合约列表和日期补齐数据
    # downloadSymbolBarByDate(['I8888', 'CU8888'], '2010-01-01')