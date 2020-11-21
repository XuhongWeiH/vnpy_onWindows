import math
import numpy

class CapitalManagementModel():
    def __init__(self):
        self.cash = 0
        self.hold = {}
        #hold = {'ru2001':{'方向':'多','持仓量':2, '买价':5000,'今收':6213, '止损价':5300}     
        self.hold_value = 0
        

    def UpdateHold(self, cash):
        self.cash = cash

        self.total_cap = self.cash

    def CoreEquityMethod(self, equity):
        new_equity = self.cash*equity
        return new_equity

    def TotalEquityMethod(self, equity):
        new_equity = self.total_cap*equity
        return new_equity

    def ReducedTotalEquityMethod(self, equity):
        #hold = {'ru2001':{'方向':'多','持仓量':2, '买价':5000,'今收':6213, '止损价':5300}  
        add_hold_value = 0
        for k in self.hold.keys():
            tmp = self.hold[k]
            if tmp['方向'] == "多":
                add_hold_value += (tmp['持仓量']*tmp['持仓单位']*(tmp['止损价']-tmp['买价']))
            if tmp['方向'] == "空":
                add_hold_value += (tmp['持仓量']*tmp['持仓单位']*(tmp['买价']-tmp['止损价']))
        new_equity = (add_hold_value+ self.cash)*equity
        return new_equity

    def ATR_order_model(self, new_equity,  yi_shou_he_yue_dan_wei, \
                        safe_daily_ATR, now_price, order_ratio = 0.14):
        # equity_ratio = min( equity_ratio, max(0, 0.1 - 0.02*len(self.hold) ) )
        safe_daily_ATR = max(safe_daily_ATR, 0.01)
        order_value = math.floor( new_equity / (yi_shou_he_yue_dan_wei * safe_daily_ATR) )
        order_value_max = math.floor( new_equity/2/ (yi_shou_he_yue_dan_wei * now_price * order_ratio) )
        return min(order_value, order_value_max)

    def stop_R_ratio_model(self, new_equity, equity_ratio, yi_shou_he_yue_dan_wei, \
                           build_price, stop_price, min_loss, order_ratio = 0.14):
        equity_ratio = min( equity_ratio, max(0, 0.1 - 0.02*len(self.hold) ) )
        min_loss = max(min_loss, 0.01)
        order_value = math.floor( new_equity * equity_ratio / \
                        (yi_shou_he_yue_dan_wei * abs(build_price - stop_price)) )
        order_value_max1 = math.floor( new_equity * equity_ratio / \
                        (yi_shou_he_yue_dan_wei * min_loss*5) )
        order_value_max2 = math.floor( new_equity  / \
                        (yi_shou_he_yue_dan_wei * build_price * order_ratio) )
        return min(order_value,order_value_max1,order_value_max2 )

    def adjust_toucun_ratio(self, equity, hold_equity_ratio):
        hold_decrease_change = {}
        single_equity = equity * hold_equity_ratio
        for k in self.hold.keys():
            tmp = self.hold[k]
            if tmp['方向'] == "多":
                risk_value = (tmp['持仓单位']*(tmp['今收']-tmp['止损价']))
                hold_num_max = single_equity // risk_value
                if tmp['持仓量'] > hold_num_max:
                    hold_decrease_change[k] = tmp['持仓量'] - single_equity // risk_value
                else:
                    hold_decrease_change[k] = 0
            if tmp['方向'] == "空":
                risk_value = (tmp['持仓单位']*(tmp['止损价']-tmp['今收']))
                hold_num_max = single_equity // risk_value
                if tmp['持仓量'] > hold_num_max:
                    hold_decrease_change[k] = tmp['持仓量'] - single_equity // risk_value
                else:
                    hold_decrease_change[k] = 0

        return hold_decrease_change
            


    
        



if __name__ == '__main__':
    hold = {'ru2001':{'方向':'多','持仓量':2, '持仓单位':10,'买价':5000,'今收':6213, '止损价':5500, '保证金比例':0.18},\
    'ru2002':{'方向':'空','持仓量':3, '持仓单位':10, '买价':5000,'今收':5113, '止损价':5200, '保证金比例':0.18},\
    'ru2003':{'方向':'多','持仓量':1, '持仓单位':10, '买价':5000,'今收':4900, '止损价':4800, '保证金比例':0.18} }
    cash = 300000
    cpm = CapitalManagementModel()
    cpm.UpdateHold(cash)
    equity_c = cpm.CoreEquityMethod(0.1)
    equity_t = cpm.TotalEquityMethod(0.1)
    equity_r = cpm.ReducedTotalEquityMethod(0.1)
    equity_a = cpm.ReducedTotalEquityMethod(1)
    order_value_atr = cpm.ATR_order_model(equity_r, equity_ratio=0.02, yi_shou_he_yue_dan_wei = 100, \
                                          daily_ATR = 3, history_min_ATR = 0.25, now_price = 380, order_ratio = 0.14)
    order_value_stopR = cpm.stop_R_ratio_model(new_equity = 50000, equity_ratio = 0.025, \
                                          yi_shou_he_yue_dan_wei = 1, build_price = 111, stop_price = 110, \
                                          min_loss = 0.1, order_ratio = 0.14)
    hold_decrease_change = cpm.adjust_toucun_ratio(equity_a, 0.03)
    print(equity_c, equity_t, equity_r, order_value_atr, order_value_stopR)
    print(hold_decrease_change)
