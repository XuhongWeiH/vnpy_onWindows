import sys
sys.path.append('.')
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.base import BacktestingMode
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy import (
    TurtleSignalStrategy
)
from datetime import datetime


# engine = BacktestingEngine()
# engine.set_parameters(
#     vt_symbol="IF88.CFFEX",
#     mode=BacktestingMode.TICK,
#     interval="1s",
#     start=datetime(2019, 1, 1),
#     end=datetime(2019, 4, 30),
#     rate=0.3/10000,
#     slippage=0.2,
#     size=300,
#     pricetick=0.2,
#     capital=1_000_000,
# )
# engine.add_strategy(AtrRsiStrategy, {})

engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="IF8888.CCFX",
    interval="1d",
    start=datetime(2005, 1, 4),
    end=datetime(2020, 6, 8),
    rate=0.5/10000,
    slippage=5,
    size=10,
    pricetick=5,
    capital=1_000_000,
    mode=BacktestingMode.BAR
)
engine.add_strategy(TurtleSignalStrategy, {})

engine.load_data()
engine.run_backtesting()
df = engine.calculate_result()
engine.calculate_statistics()
engine.show_chart()

# setting = OptimizationSetting()
# setting.set_target("sharpe_ratio")
# setting.add_parameter("atr_length", 3, 39, 1)
# setting.add_parameter("atr_ma_length", 10, 30, 1)

# engine.run_ga_optimization(setting)

trades = engine.trades
for value in trades.values():
    print("时间:",value.datetime,value.direction.value,value.offset.value, "价格：",value.price, "数量：",value.volume)
    if value.offset.value == "平":
        print("---------------------------------------------------------")
