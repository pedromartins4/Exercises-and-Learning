import sys
import copy
import numpy as np
import datetime as dt

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

'''
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
'''


def find_money_event(ls_symbols, d_data, event_money):
    orders_list = list()

    df_close = d_data['actual_close']

    print 'Finding Events'

    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):

            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

            if f_symprice_today < event_money and f_symprice_yest >= event_money:
                if i + 5 < len(ldt_timestamps):
                    today = ldt_timestamps[i]
                    five_days_ahead = ldt_timestamps[i + 5]

                    orders_list.append((today.year, today.month, today.day, s_sym, 'Buy', '100'))
                    orders_list.append(
                        (five_days_ahead.year, five_days_ahead.month, five_days_ahead.day, s_sym, 'Sell', '100'))

                    df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events, orders_list


def run(start_day_split, end_day_split, symbols):
    dt_start = dt.datetime(int(start_day_split[0]), int(start_day_split[1]), int(start_day_split[2]), 16, 00, 00)
    dt_end = dt.datetime(int(end_day_split[0]), int(end_day_split[1]), int(end_day_split[2]), 16, 00, 00)

    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(symbols)
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events, orders_list = find_money_event(ls_symbols, d_data, 6.0)

    return df_events, d_data, orders_list


if __name__ == '__main__':

    start_day_split = sys.argv[1].split(',')
    end_day_split = sys.argv[2].split(',')
    symbols = sys.argv[3]
    event_file_name = None
    if len(sys.argv) > 4:
        event_file_name = sys.argv[4]

    df_events, d_data, orders_list = run(start_day_split, end_day_split, symbols)

    print orders_list
    print 'Creating orders file'
    with open('orders.csv', 'w') as file:
        for y, m, d, s, o, q in orders_list:
            file.write('%s,%s,%s,%s,%s,%s\n' % (y, m, d, s, o, q))

    if event_file_name is not None:
        print 'Profiling Events'
        ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20, s_filename=event_file_name,
                         b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')
