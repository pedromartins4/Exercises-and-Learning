import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import numpy as np
import copy

"""
Finds an event where equity price dropped 5% or more but market (S&P)
increased by 2% or more 
"""


def tutorial9_event(symbols_list, data):
    close_data = data['actual_close']
    market_close = close_data['SPY']

    # Creating an empty dataframe
    df_events = copy.deepcopy(close_data)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = close_data.index

    for s_sym in symbols_list:  # for each symbol
        for i in range(1, len(ldt_timestamps)):  # for each day
            # Calculating the returns for this timestamp
            f_symprice_today = close_data[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = close_data[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = market_close.ix[ldt_timestamps[i]]
            f_marketprice_yest = market_close.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events, data


def homework2_event(symbols_list, data):
    close_data = data['actual_close']

    df_events = copy.deepcopy(close_data)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = close_data.index

    for s_sym in symbols_list:  # for each symbol
        for i in range(1, len(ldt_timestamps)):  # for each day
            # Calculating the returns for this timestamp
            f_symprice_today = close_data[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = close_data[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if price dropped $5 from yesterday
            if f_symprice_today < 10 and f_symprice_yest >= 10:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events, data


def find_event(startdate, enddate, code, event_func, study_name):
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startdate, enddate, timeofday)

    c_dataobj = da.DataAccess('Yahoo')  # , cachestalltime=0)
    symbols_list = c_dataobj.get_symbols_from_list(code)
    symbols_list.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(timestamps, symbols_list, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events, data = event_func(symbols_list, d_data)

    print "Creating Study"
    ep.eventprofiler(df_events, data, i_lookback=20, i_lookforward=20,
                     s_filename=study_name + '.pdf', b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')


if __name__ == '__main__':
    startdate = dt.datetime(2008, 1, 1)
    enddate = dt.datetime(2009, 12, 31)

    find_event(startdate, enddate, 'sp5002012', homework2_event, 'test_sp5002012')
