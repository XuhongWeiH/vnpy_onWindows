import sys
sys.path.append('.')

from jqdatasdk import *
auth('13122192187', 'w19940306')
# 查询是否连接成功
is_auth = is_auth()
print(is_auth)

from vnpy.trader.utility import load_json, save_json
SETTING_FILENAME: str = "vt_setting.json"
setting_data = load_json(SETTING_FILENAME)
setting_data["database.database"] = "JQ_data"
save_json(SETTING_FILENAME, setting_data)

import multiprocessing
import re
import pandas as pd
from contextlib import closing
from copy import copy
from copy import deepcopy
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, HistoryRequest, Product, TickData
from vnpy.trader.database import init
from vnpy.trader.setting import get_settings
from enum import Enum
from time import sleep
from datetime import datetime, time, timedelta
from logging import INFO

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine
from vnpy.trader.utility import load_json, extract_vt_symbol
from vnpy.trader.database import database_manager

from vnpy.gateway.ctp import CtpGateway
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.trader.event import EVENT_CONTRACT, EVENT_TICK

from vnpy.app.data_recorder.engine import RecorderEngine
from queue import Queue, Empty

EXCHANGE_LIST = [
    Exchange.SHFE,
    Exchange.DCE,
    Exchange.CZCE,
    Exchange.CFFEX,
    Exchange.INE,
]

SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
CTP_SETTING = load_json("connect_ctp.json")


def is_futures(vt_symbol: str) -> bool:
    """
    是否是期货
    """
    return bool(re.match(r"^[a-zA-Z]{1,3}\d{2,4}.[A-Z]+$", vt_symbol))


class RecordMode(Enum):
    BAR = "bar"
    TICK = "tick"


class WholeMarketRecorder(RecorderEngine):
    def __init__(self, main_engine, event_engine, record_modes=[RecordMode.BAR]):
        self.record_modes = record_modes
        super().__init__(main_engine, event_engine)
        
    def load_setting(self):
        pass

    def record_tick(self, tick: TickData):
        """
        抛弃非交易时间校验数据
        """
        tick_time = tick.datetime.time()
        
        task = ("tick", copy(tick))
        self.queue.put(task)

    # def add_bar_recording(self, vt_symbol: str):
    #     """"""
    #     if vt_symbol in self.bar_recordings:
    #         self.write_log(f"已在K线记录列表中：{vt_symbol}")
    #         return

    #     if Exchange.LOCAL.value not in vt_symbol:
    #         contract = self.main_engine.get_contract(vt_symbol)
    #         if not contract:
    #             self.write_log(f"找不到合约：{vt_symbol}")
    #             return

    #         self.bar_recordings[vt_symbol] = {
    #             "symbol": contract.symbol,
    #             "exchange": contract.exchange.value,
    #             "gateway_name": contract.gateway_name
    #         }

    #         self.subscribe(contract)
    #     else:
    #         self.tick_recordings[vt_symbol] = {}

    #     self.save_setting()
    #     self.put_event()

    #     self.write_log(f"添加K线记录成功：{vt_symbol}")
    
    def run(self):
        """"""
        while self.active:
            try:
                task = self.queue.get(timeout=1)
                task_type, data = task

                if RecordMode.TICK in task_type:
                    database_manager.save_tick_data([data])
                elif RecordMode.BAR in task_type:
                    database_manager.save_bar_data([data])

            except Empty:
                continue

            except Exception:
                self.active = False

                info = sys.exc_info()
                event = Event(EVENT_RECORDER_EXCEPTION, info)
                self.event_engine.put(event)

    def record_bar(self, bar: BarData):
        """
        
        """
        bar_time = bar.datetime.time()

        task = ("bar", copy(bar))
        self.queue.put(task)

    def process_contract_event(self, event):
        """"""
        contract = event.data
        vt_symbol = contract.vt_symbol
        # 不录制期权
        if is_futures(vt_symbol):
            if RecordMode.BAR in self.record_modes:
                self.add_bar_recording(vt_symbol)
            if RecordMode.TICK in self.record_modes:
                self.add_tick_recording(vt_symbol)
            self.subscribe(contract)


def run_child():
    """
    Running in the child process.
    """
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)
    main_engine.write_log("主引擎创建成功")

    # 记录引擎

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    main_engine.connect(CTP_SETTING, "CTP")
    main_engine.write_log("连接CTP接口")

    whole_market_recorder = WholeMarketRecorder(main_engine, event_engine)

    main_engine.write_log("开始录制数据")
    oms_engine = main_engine.get_engine("oms")
    while True:
        sleep(1)


def run_parent():
    """
    Running in the parent process.
    """
    print("启动CTA策略守护父进程")

    child_process = None

    while True:
        current_time = datetime.now().time()
        get_data_spare = get_query_count()['spare']
        trading = True
        if get_data_spare <= 1e5:
            print('\r' + 'Times left: ' + str(get_data_spare) + str(current_time).split('.')[0], end='', flush=True)
            trading = False

        # Start child process in trading period
        if trading and child_process is None:
            print("启动数据提取子进程")
            child_process = multiprocessing.Process(target=run_child)
            child_process.start()
            print("数据提取子进程启动成功")

        # 非记录时间则退出数据录制子进程
        if not trading and child_process is not None:
            print("关闭数据提取子进程")
            child_process.terminate()
            child_process.join()
            child_process = None
            print("数据提取子进程关闭成功")
        sys.stdout.flush()
        sleep(5)


if __name__ == "__main__":
    run_parent()