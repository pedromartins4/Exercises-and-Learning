import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import sys
import numpy as np

print 'Begin'

ls_symbols = ["AAPL", "GLD", "GOOG", "$SPX", "XOM"]
dt_start = dt.datetime(2006, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

c_dataobj = da.DataAccess('Yahoo')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

na_price = d_data['close'].values
# plt.clf()
# plt.plot(ldt_timestamps, na_price)
# plt.legend(ls_symbols)
# plt.ylabel('Adjusted Close')
# plt.xlabel('Date')

na_normalized_price = na_price / na_price[0, :]
plt.clf()
plt.plot(ldt_timestamps, na_normalized_price)
plt.legend(ls_symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.show()

na_rets = na_normalized_price.copy()
tsu.returnize0(na_rets)

cum_daily_ret = na_normalized_price.copy()
cum_daily_ret[1:, :] = cum_daily_ret[0:-1] * (na_rets[1:, :] + 1)
cum_daily_ret[0, :] = np.ones(cum_daily_ret.shape[1])

plt.clf()
plt.plot(ldt_timestamps, cum_daily_ret)
plt.legend(ls_symbols)
plt.ylabel('Cum daily ret')
plt.xlabel('Date')
plt.show()

# print(d_data['close'])
# print(d_data['close'].values)
# print(na_rets)
#       AAPL     GLD    GOOG     $SPX    XOM
# plt.scatter(na_rets_2[:, 3], na_rets_2[:, 4], c='blue')
# plt.legend()

# plt.show()
# print 'dt_timeofday', dt_timeofday

