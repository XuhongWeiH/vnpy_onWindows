import math
from sourceCode.order_management import CapitalManagementModel
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    Direction,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
sys.path.append('.')



class TurtleSignalStrategyImprove(CtaTemplate):
    """"""
    author = "wxh"

    entry_unit = 20
    entry_window = 5
    exit_unit = 20
    exit_window = 5
    tupo_insure_ratio = 0.02

    atr_window_recent = 23
    atr_window_day_avg = 150
    atr_value_recent = 0
    atr_value_day_avg = 0
    atr_safe_ratio = 40
    atr_value_safe = 500

    stop_atr = 0.2
    stop_avg_window = 120
    stop_avg_value = 0
    stop_high_value = 0
    stop_low_value = 0
    stop_high_low_ratio = 0.9
    stop_highlow_value_byrate = 0

    entry_up = 0
    entry_down = 0
    exit_up = 0
    exit_down = 0

    fixed_size = 1.0
    price_mean = 0

    long_entry = 0
    long_entry_trade = np.nan
    short_entry = 0
    short_entry_trade = np.nan
    long_stop = np.nan
    short_stop = np.nan

    parameters = ["entry_unit", "entry_window", "exit_unit", "exit_window", "tupo_insure_ratio",
                  "atr_window_recent", "atr_window_day_avg", "atr_safe_ratio", "stop_atr", "stop_avg_window", 
                  "stop_high_low_ratio"]

    variables = ["atr_value_recent", "atr_value_day_avg", "atr_value_safe", "entry_up", "entry_down", "exit_up",
                 "exit_down", "atr_value", "price_mean", "long_entry", "short_entry", "long_stop", "short_stop",
                 "stop_avg_value", "stop_high_value", "stop_low_value", 'stop_highlow_value_byrate' "fixed_size"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(2 * max((1 + self.entry_window) * self.entry_unit,
                                       (1 + self.exit_window) * self.exit_unit))  # Arr带参数size，初始化缓存多少个bar

        self.atr_window_day_avg = int(min(self.atr_window_day_avg, 1.5 * max(self.entry_window * self.entry_unit,
                                                                             self.exit_window * self.exit_unit)))
        self.setting = setting
        self.capital_total = 0
        self.entry_count = 0
        self.exit_count = 0
        self.entry_signal_array = []
        self.exit_signal_array = []
        self.trade_allow = {'LONG': True, 'SHORT': True}

        self.bar = None
        self.hold_record = {}
        self.histry_ktmp = {}
        self.history_Kline = pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume",\
            'stop_exit_up', 'stop_exit_down', 'long_entry_trade', 'short_entry_trade',
            'entry_up', 'entry_down', 'stop_highlow_value_byrate', 'stop_long_atr', 'stop_short_atr', 'stop_avg_value'])


        self.future_size = None
        self.newday_price = None

        self.cpm = CapitalManagementModel()
        self.future_info = {}
        self.symbol = vt_symbol

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(2 * max(self.entry_window * self.entry_unit,
                              self.exit_window * self.exit_unit))

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.future_info = {
            '持仓单位': self.future_size,
            '今收': self.newday_price,
            '保证金比例': 0.18
        }
        self.cancel_all()
        self.bar = bar
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        if self.hold_record != {}:
            self.hold_record[self.symbol]['今收'] = self.newday_price
        self.entry_up, self.entry_down, self.entry_count, self.entry_signal_array, self.trade_allow = self.am.donchian_long_term(
            self.entry_unit, self.entry_window, self.entry_count, self.entry_signal_array, self.trade_allow)
        self.exit_up, self.exit_down, self.exit_count, self.exit_signal_array, _ = self.am.donchian_long_term(
            self.exit_unit, self.exit_window, self.exit_count, self.exit_signal_array)

        self.entry_up = self.entry_up * (1 + self.tupo_insure_ratio)
        self.entry_down = self.entry_down / (1 - self.tupo_insure_ratio)


        # cover 平空 buy买多 sell平多 short 买空
        if not self.pos:
            self.atr_value_recent = self.am.atr(self.atr_window_recent)
            self.atr_value_day_avg = self.am.atr(self.atr_window_day_avg)
            self.atr_value_safe = self.atr_value_day_avg * \
                self.atr_safe_ratio  # *(sqrt(N)/N),N个品种
            self.stop_avg_value = self.am.sma(self.stop_avg_window)

            # 开仓：
            if self.trade_allow['LONG']:
                self.send_buy_orders(self.entry_up)
                self.stop_high_value = self.am.high[-1]

            if self.trade_allow['SHORT']:
                self.send_short_orders(self.entry_down)
                self.stop_low_value = self.am.low[-1]

        elif self.pos > 0:
            self.stop_high_value = max(self.am.high[-1], self.stop_high_value)
            self.stop_highlow_value_byrate = self.stop_high_value * self.stop_high_low_ratio
            sell_price = max(self.long_stop, self.exit_down, self.stop_highlow_value_byrate, self.stop_avg_value)
            self.sell(sell_price, abs(self.pos), True)
            self.trade2hold(sell_price, direction='多')

        elif self.pos < 0:
            self.stop_low_value = min(self.am.low[-1], self.stop_low_value)
            self.stop_highlow_value_byrate = self.stop_low_value / self.stop_high_low_ratio
            cover_price = min(self.short_stop, self.exit_up, self.stop_highlow_value_byrate, self.stop_avg_value)
            self.cover(cover_price, abs(self.pos), True)
            self.trade2hold(cover_price, direction='空')
        
        self.put_event()

    def trade2hold(self, stop_price, trade=None, direction='没定义'):

        if trade is None:
            if self.hold_record != {}:
                assert(self.hold_record[self.symbol]['方向'] == direction)
                self.hold_record[self.symbol]['止损价'] = stop_price
                return

        new_hold = {'方向': trade.direction.value,
                    '持仓量': trade.volume,
                    '持仓单位': self.future_size,
                    '买价': trade.price,
                    '今收': self.newday_price,
                    '止损价': stop_price,
                    '保证金比例': 0.18}

        hold = {}
        if trade.symbol in self.hold_record.keys():
            if trade.offset.value == '开':
                old_hold = self.hold_record[trade.symbol]
                # assert(old_hold['方向'] == new_hold['方向'])
                hold['方向'] = old_hold['方向']
                hold['持仓量'] = old_hold['持仓量'] + new_hold['持仓量']
                hold['持仓单位'] = old_hold['持仓单位']
                hold['买价'] = round((old_hold['买价'] * old_hold['持仓量'] + new_hold['买价'] * new_hold['持仓量'])
                                   / (old_hold['持仓量'] + new_hold['持仓量']), 2)
                hold['今收'] = new_hold['今收']
                hold['止损价'] = stop_price
                hold['保证金比例'] = new_hold['保证金比例']

                self.capital_total -= new_hold['持仓量'] * \
                    new_hold['买价'] * new_hold['持仓单位'] * new_hold['保证金比例']
            else:
                old_hold = self.hold_record[trade.symbol]
                # assert(old_hold['持仓量'] - new_hold['持仓量'] >= 0)
                if old_hold['方向'] == "多":
                    if new_hold['方向'] == "多":
                        print("方向错误,多空双开")
                    self.capital_total += new_hold['持仓量'] * \
                        new_hold['买价'] * new_hold['持仓单位'] * new_hold['保证金比例']
                    if old_hold['持仓量'] - new_hold['持仓量'] == 0:
                        self.hold_record.pop(trade.symbol)
                        return
                if old_hold['方向'] == "空":
                    if new_hold['方向'] == "空":
                        print("方向错误,多空双开")
                    self.capital_total += new_hold['持仓量'] * \
                        (2 * old_hold['买价'] - new_hold['买价']) * \
                        new_hold['持仓单位'] * new_hold['保证金比例']
                    if old_hold['持仓量'] - new_hold['持仓量'] == 0:
                        self.hold_record.pop(trade.symbol)
                        return

                hold['持仓量'] = old_hold['持仓量'] - new_hold['持仓量']
                hold['持仓单位'] = old_hold['持仓单位']
                hold['买价'] = old_hold['买价']
                hold['今收'] = new_hold['今收']
                hold['止损价'] = stop_price
                hold['保证金比例'] = new_hold['保证金比例']
        else:
            hold = new_hold
            self.capital_total -= new_hold['持仓量'] * \
                new_hold['买价'] * new_hold['持仓单位'] * new_hold['保证金比例']
        self.hold_record[trade.symbol] = hold

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        if trade.direction == Direction.LONG:
            self.trade_allow['LONG'] = False
            self.long_entry_trade = trade.price
            self.short_entry_trade = np.nan
            self.long_stop = self.long_entry_trade - self.stop_atr * self.atr_value_recent
            self.short_stop = np.nan
            sell_price = max(self.long_stop, self.exit_down, self.stop_highlow_value_byrate, self.stop_avg_value)
            self.trade2hold(sell_price, trade=trade)
        else:
            self.trade_allow['SHORT'] = False
            self.short_entry_trade = trade.price
            self.long_entry_trade = np.nan
            self.short_stop = self.short_entry_trade + self.stop_atr * self.atr_value_recent
            self.long_stop = np.nan
            cover_price = min(self.short_stop, self.exit_up, self.stop_highlow_value_byrate, self.stop_avg_value)
            self.trade2hold(cover_price, trade=trade)

        if self.hold_record != {}:
            # print(self.hold_record)
            pass

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass

    def on_chart(self):
        
        if self.history_Kline.empty:
            # for k in self.history_Kline.columns:
            #     if k != 'Date':
            #         self.histry_ktmp[k] = 0
            self.histry_ktmp["Date"] = self.bar.datetime
            self.histry_ktmp["Open"] = self.bar.open_price
            self.histry_ktmp["High"] = self.bar.high_price
            self.histry_ktmp["Low"] = self.bar.low_price
            self.histry_ktmp["Close"] = self.bar.close_price
            self.histry_ktmp["Volume"] = self.bar.volume
        else:
            self.histry_ktmp = {"Date": self.bar.datetime, "Open": self.bar.open_price,
                            "High": self.bar.high_price, "Low": self.bar.low_price, "Close": self.bar.close_price, 
                            "Volume": self.bar.volume}

        if not self.am.inited:
            self.history_Kline = self.history_Kline.append([self.histry_ktmp], ignore_index=True)
            return
        if not self.pos:
            self.stop_highlow_value_byrate = np.nan
            self.long_stop = np.nan
            self.short_stop = np.nan

        self.histry_ktmp['entry_up'] = self.entry_up
        self.histry_ktmp['entry_down'] = self.entry_down
        self.histry_ktmp['stop_exit_up'] = self.exit_up
        self.histry_ktmp['stop_exit_down'] = self.exit_down
        self.histry_ktmp['stop_highlow_value_byrate'] = self.stop_highlow_value_byrate
        self.histry_ktmp['stop_long_atr'] = self.long_stop
        self.histry_ktmp['stop_short_atr'] = self.short_stop
        self.histry_ktmp['stop_avg_value'] = self.stop_avg_value
        self.histry_ktmp['long_entry_trade'] = self.long_entry_trade
        self.histry_ktmp['short_entry_trade'] = self.short_entry_trade

        self.history_Kline = self.history_Kline.append([self.histry_ktmp], ignore_index=True)
        self.long_entry_trade = np.nan
        self.short_entry_trade = np.nan

        self.history_Kline_show = self.history_Kline
        self.history_Kline_show = self.history_Kline_show.set_index(['Date'])

        add_plot = [
        # mpf.make_addplot(self.history_Kline_show.Volume),
        # mpf.make_addplot(self.history_Kline_show.stop_exit_up, color='b'),
        # mpf.make_addplot(self.history_Kline_show.stop_exit_down, color='g'),
        mpf.make_addplot(self.history_Kline_show.entry_up, color='r'),
        mpf.make_addplot(self.history_Kline_show.entry_down, color='c'),
        # mpf.make_addplot(self.history_Kline_show.stop_highlow_value_byrate, color='m'),
        # mpf.make_addplot(self.history_Kline_show.stop_long_atr, color='y'),
        # mpf.make_addplot(self.history_Kline_show.stop_short_atr, color='k'),
        # mpf.make_addplot(self.history_Kline_show.stop_avg_value, color='w'),
        # mpf.make_addplot(self.history_Kline_show['long_entry_trade'], markersize=50, marker='^', color='y'),
        mpf.make_addplot(self.history_Kline_show['short_entry_trade'],  markersize=50, marker='v', color='r')]
        #scatter=True,

        my_color = mpf.make_marketcolors(up='red',#上涨时为红色
                                 down='green',#下跌时为绿色
                                 edge='i',#隐藏k线边缘
                                 volume='in',#成交量用同样的颜色
                                 inherit=True)

        my_style = mpf.make_mpf_style(gridaxis='both',#设置网格
                           gridstyle='-.',
                           y_on_right=False,
                            marketcolors=my_color)
        if len(self.history_Kline_show) > 500: 
            # mpf.plot(self.history_Kline_show, style=my_style, volume=True,addplot=add_plot,#展示成交量副图
            mpf.plot(self.history_Kline_show, style=my_style, volume=False,addplot=add_plot, #展示成交量副图
             type='candle',figratio=(2,1),#设置图片大小
            figscale=1.5)


        

    def send_buy_orders(self, price):
        """"""
        self.long_entry = price
        self.long_stop = self.long_entry - self.stop_atr * self.atr_value_recent
        self.short_stop = np.nan

        self.cpm.UpdateHold(self.capital_total, self.hold_record)
        equity_c = self.cpm.CoreEquityMethod(0.1)
        equity_t = self.cpm.TotalEquityMethod(0.1)
        equity_r = self.cpm.ReducedTotalEquityMethod(0.1)
        equity_a = self.cpm.ReducedTotalEquityMethod(1)
        order_value_atr = self.cpm.ATR_order_model(equity_a, yi_shou_he_yue_dan_wei=self.future_info['持仓单位'],
                                                   safe_daily_ATR=self.atr_value_safe, now_price=self.future_info[
                                                       '今收'],
                                                   order_ratio=self.future_info['保证金比例'])

        hold_decrease_change = self.cpm.adjust_toucun_ratio(equity_a, 0.03)
        # print(equity_c, equity_t, equity_r, order_value_atr, order_value_stopR)
        # print(hold_decrease_change)
        self.fixed_size = order_value_atr
        if self.fixed_size == 0:
            return
        t = self.pos / self.fixed_size

        if t < 1:
            self.buy(price, self.fixed_size, True)

        # if t < 2:
        #     self.buy(price + self.atr_value_day_avg * 0.5 *
        #              self.add_rate / 10, self.fixed_size, True)

        # if t < 3:
        #     self.buy(price + self.atr_value_day_avg *
        #              self.add_rate / 10, self.fixed_size, True)

        # if t < 4:
        #     self.buy(price + self.atr_value_day_avg * 1.5 *
        #              self.add_rate / 10, self.fixed_size, True)

    def send_short_orders(self, price):
        """"""
        self.short_entry = price
        self.short_stop = self.short_entry + self.stop_atr * self.atr_value_recent
        self.long_stop = np.nan

        self.cpm.UpdateHold(self.capital_total, self.hold_record)
        equity_c = self.cpm.CoreEquityMethod(0.1)
        equity_t = self.cpm.TotalEquityMethod(0.1)
        equity_r = self.cpm.ReducedTotalEquityMethod(0.1)
        equity_a = self.cpm.ReducedTotalEquityMethod(1)
        order_value_atr = self.cpm.ATR_order_model(equity_a, yi_shou_he_yue_dan_wei=self.future_info['持仓单位'],
                                                   safe_daily_ATR=self.atr_value_safe, now_price=self.future_info[
                                                       '今收'],
                                                   order_ratio=self.future_info['保证金比例'])

        hold_decrease_change = self.cpm.adjust_toucun_ratio(equity_a, 0.03)
        # print(equity_c, equity_t, equity_r, order_value_atr, order_value_stopR)
        # print(hold_decrease_change)

        self.fixed_size = order_value_atr
        if self.fixed_size == 0:
            return
        t = self.pos / self.fixed_size

        if t > -1:
            self.short(price, self.fixed_size, True)

        # if t > -2:
        #     self.short(price - self.atr_value_day_avg * 0.5 *
        #                self.add_rate / 10, self.fixed_size, True)

        # if t > -3:
        #     self.short(price - self.atr_value_day_avg *
        #                self.add_rate / 10, self.fixed_size, True)

        # if t > -4:
        #     self.short(price - self.atr_value_day_avg * 1.5 *
        #                self.add_rate / 10, self.fixed_size, True)


if __name__ == '__main__':
    pass
