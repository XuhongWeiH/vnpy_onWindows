import tushare as ts
ts.set_token('7d1d06d8fe0fbbb4438ca233903049c51e7dd7bc43248b591fa0f63f')
pro = ts.pro_api()

df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
df