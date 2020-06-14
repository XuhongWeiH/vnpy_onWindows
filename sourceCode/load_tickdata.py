import os 
import csv
from datetime import datetime, time

from vnpy.trader.constant import Exchange
from vnpy.trader.database import database_manager
from vnpy.trader.object import TickData


def run_load_csv(root):
    """
    遍历同一文件夹内所有csv文件，并且载入到数据库中
    """
    for file in os.listdir(root): 
        if not file.endswith(".csv"): 
            continue

        absFilePath = '/'.join([root,file])
        print("载入文件：", absFilePath)
        csv_load(absFilePath)

def csv_load(file):
    """
    读取csv文件内容，并写入到数据库中    
    """
    with open(file, "r") as f:
        reader = csv.DictReader(f)

        ticks = []
        start = None
        count = 0

        for item in reader:

            # generate datetime
            dt = datetime.strptime(item['Datetime'], "%Y-%m-%d %H:%M:%S")

            # filter
            if dt.time() > time(15, 1) and dt.time() < time(20, 59):
                continue

            tick = TickData(
                symbol="RU88",
                datetime=dt,
                exchange=Exchange.SHFE,
                last_price=float(item["最新价"]),
                volume=float(item["持仓量"]),
                bid_price_1=float(item["申买价一"]),
                bid_volume_1=float(item["申买量一"]),
                ask_price_1=float(item["申卖价一"]),
                ask_volume_1=float(item["申卖量一"]), 
                gateway_name="DB",       
            )
            ticks.append(tick)

            # do some statistics
            count += 1
            if not start:
                start = tick.datetime

        end = tick.datetime
        database_manager.save_tick_data(ticks)

        print("插入数据", start, "-", end, "总数量：", count)  
        
if __name__ == "__main__":
    run_load_csv("/Users/weixuhong/Documents/DATA/csv/sina")  