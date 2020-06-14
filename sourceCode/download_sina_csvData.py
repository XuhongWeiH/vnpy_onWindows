from urllib import request
import json
import pandas as pd


def get_data(id):
    url_d = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol='
    url = url_d + id
    req = request.Request(url)
    rsp = request.urlopen(req)
    res = rsp.read()
    res_json = json.loads(res)


    bar_list = []

    res_json.reverse()
    for line in res_json:
        bar = {}
        bar['Datetime'] = line[0]
        bar['Open'] = float(line[1])
        bar['High'] = float(line[2])
        bar['Low'] = float(line[3])
        bar['Close'] = float(line[4])
        bar['Volume'] = int(line[5])
        bar_list.append(bar)

    df = pd.DataFrame(data=bar_list)
    print(df)
    df.to_csv(''.join(['/Users/weixuhong/Documents/DATA/csv/sina/', id, '.csv']), index=None)

if __name__ == '__main__':
    get_data('RU1910')

"""
商品期货
http://stock2.finance.sina.com.cn/f utures/a pi/j son.p h p/ln d exService.g etlnnerFutures
MiniKLineXm?symboI=CODE
例子
http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=M0
5分钟：http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=M0
15分钟：http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine15m?symbol=M0
30分钟：
http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine30m?symbol=M0
60分钟
http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine60m?symbol=M0
日线
http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=M0
http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=M1401


股指期货
5分钟
http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesMiniKLine5m?symbol=IF1306
15
http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesMiniKLine30m?symbol=IF1306
60分钟：http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesMiniKLine60m?symbol=IF1306
日线：http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesDailyKLine?symbol=IF1306
"""