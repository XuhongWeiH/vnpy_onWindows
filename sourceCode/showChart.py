
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np

 

daily = pd.read_csv('D:/vnpy-2.1.2/vnpy-2.1.2/Data_recorder/example/NOV2019.csv', index_col=0, parse_dates=True)
daily.index.name = 'Date'
daily.shape
daily.head(3)
daily.tail(3)

slist = [200]*(len(daily)-3)
[slist.append(np.nan) for i in range(3)]
add_plot = [mpf.make_addplot(daily['Close'].values*5),
            mpf.make_addplot(slist, scatter=True, markersize=200, marker='^', color='y'),
            mpf.make_addplot([3100]*len(daily), scatter=True, markersize=200, marker='v', color='r')
            ]
# plt.autoscale(enable = False)
mpf.plot(daily, addplot=add_plot ,type='candle',volume=True)

# mpf.plot(daily,type='candle',mav=(3,6,9))


# mpf.plot(daily,type='candle')
# plt.show()
