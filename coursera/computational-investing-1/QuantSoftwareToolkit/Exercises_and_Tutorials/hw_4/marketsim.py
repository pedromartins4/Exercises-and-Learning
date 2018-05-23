import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import pandas as pd
import numpy as np
import sys
import csv


def orders_into_df(orders_file):
    dt_list = list()
    symbol_list = list()
    order_type_list = list()
    volume_list = list()

    # Line example: 2011,1,14,AAPL,Buy,1500
    with open(orders_file, 'r') as file:
        for line in file:
            line = line.strip()
            line_split = line.split(',')
            dt_list.append(dt.datetime(int(line_split[0]), int(line_split[1]), int(line_split[2]), 16, 00, 00))
            symbol_list.append(line_split[3])
            order_type_list.append(line_split[4])
            volume_list.append(line_split[5])

    data = {'datetime': dt_list, 'symbol': symbol_list, 'ordertype': order_type_list, 'volume': volume_list}

    df_orders = pd.DataFrame(data)

    df_orders = df_orders.sort_values(by=['datetime'])
    df_orders = df_orders.reset_index(drop=True)

    symbol_list = list(set(df_orders['symbol']))

    return df_orders, symbol_list


def fetchNYSEData(dt_start, dt_end, ls_symbols):
    dt_timeofday = dt.timedelta(hours=16)

    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    na_price = d_data['close'].values

    return na_price, ldt_timestamps


def marketsim(initial_cash, df_orders, symbols):
    dt_start = df_orders.datetime[0]
    dt_end = df_orders.datetime[len(df_orders) - 1]

    close_prices, ldt_timestamps = fetchNYSEData(dt_start, dt_end, symbols)

    n_days = len(ldt_timestamps)

    # holdings
    df_holdings = pd.DataFrame(0, columns=symbols, index=ldt_timestamps)

    # cash/day
    df_cash = pd.DataFrame(0, columns=['cash_in_hand'], index=ldt_timestamps)

    # value/day
    df_values = pd.DataFrame(0, columns=['portfolio_value'], index=ldt_timestamps)

    index = 0

    for trading_day_index in range(n_days):
        if trading_day_index != 0:
            df_cash.cash_in_hand.ix[trading_day_index] = df_cash.cash_in_hand.ix[trading_day_index - 1]
        else:
            df_cash.cash_in_hand.ix[trading_day_index] = initial_cash

        for order_date in df_orders.datetime:
            if order_date == ldt_timestamps[trading_day_index]:
                s_aux = df_orders.symbol.ix[index]
                stock_symbol = symbols.index(s_aux)
                n_shares = df_orders.volume.ix[index]
                day_price = close_prices[trading_day_index, stock_symbol]
                if df_orders.ordertype.ix[index] == 'Buy':
                    df_cash.cash_in_hand.ix[trading_day_index] = float(df_cash.cash_in_hand.ix[trading_day_index]) - (
                            float(day_price) * float(n_shares))
                    df_holdings[s_aux].ix[0] += int(n_shares)
                elif df_orders.ordertype.ix[index] == 'Sell':
                    df_cash.cash_in_hand.ix[trading_day_index] = float(df_cash.cash_in_hand.ix[trading_day_index]) + (
                            float(day_price) * float(n_shares))
                    df_holdings[s_aux].ix[0] -= int(n_shares)
                index += 1

        portfolio_value = 0

        for symbol in symbols:
            day_price = close_prices[trading_day_index, symbols.index(symbol)]
            portfolio_value += df_holdings[symbol].ix[0] * day_price

        df_values.portfolio_value.ix[trading_day_index] = portfolio_value + df_cash.cash_in_hand.ix[trading_day_index]

    df_values.index = ldt_timestamps
    return df_holdings, df_values, df_cash


def values_to_csv(values_file, df_values):
    with open(values_file, 'w') as file:
        writer = csv.writer(file)

        for index in range(len(df_values)):
            writer.writerow([df_values.index[index].year, df_values.index[index].month, df_values.index[index].day,
                             int(round(df_values.portfolio_value.ix[index], 0))])


def analyze(df_values):
    symbols = ['$SPX']

    dt_start = df_values.index[0]
    dt_end = df_values.index[len(df_values) - 1]

    df_spx_close, ldt_timestamps = fetchNYSEData(dt_start, dt_end, symbols)

    n_days = len(ldt_timestamps)
    dailyrets = np.zeros((n_days, 2))
    cumrets = np.zeros((n_days, 2))

    first_day_prices = [df_spx_close[0, 0], df_values.portfolio_value.ix[0]]

    for i in range(n_days):
        if i != 0:
            dailyrets[i, 0] = ((df_spx_close[i, 0] / df_spx_close[i - 1, 0]) - 1)
            dailyrets[i, 1] = ((df_values.portfolio_value.ix[i] / df_values.portfolio_value.ix[i - 1]) - 1)

            cumrets[i, 0] = (df_spx_close[i, 0] / first_day_prices[0])
            cumrets[i, 1] = (df_values.portfolio_value.ix[i] / first_day_prices[1])

    avg_SPX_daily_rets = np.average(dailyrets[:, 0])
    avg_fund_daily_rets = np.average(dailyrets[:, 1])

    std_dev_SPX = np.std(dailyrets[:, 0])
    std_dev_fund = np.std(dailyrets[:, 1])

    spx_ret = cumrets[-1, 0]
    fund_ret = cumrets[-1, 1]

    k = 252
    sharpe_SPX = np.sqrt(k) * (avg_SPX_daily_rets / std_dev_SPX)
    sharpe_fund = np.sqrt(k) * (avg_fund_daily_rets / std_dev_fund)

    res = {'dt_end': dt_end, 'df_values': df_values, 'ldt_timestamps': ldt_timestamps,
           'sharpe_fund': sharpe_fund,
           'sharpe_SPX': sharpe_SPX, 'fund_ret': fund_ret, 'spx_ret': spx_ret,
           'std_dev_fund': std_dev_fund, 'std_dev_SPX': std_dev_SPX, 'avg_fund_daily_rets': avg_fund_daily_rets,
           'avg_SPX_daily_rets': avg_SPX_daily_rets}

    return res


def print_analyze(res):
    print 'Final value: {0},{1},{2},{3}'.format(res['dt_end'].year,
                                                res['dt_end'].month,
                                                res['dt_end'].day,
                                                res['df_values'].portfolio_value.ix[-1])

    print 'Details of the Performance of the portfolio'
    print ''
    print 'Data Range :', res['ldt_timestamps'][0], ' to ', res['ldt_timestamps'][-1]
    print ''
    print 'Sharpe Ratio of Fund :', res['sharpe_fund']
    print 'Sharpe Ratio of S&P :', res['sharpe_SPX']
    print ''
    print 'Total Return of Fund :', res['fund_ret']
    print 'Total Return of S&P :', res['spx_ret']
    print ''
    print 'Standard Deviation of Fund :', res['std_dev_fund']
    print 'Standard Deviation of S&P :', res['std_dev_SPX']
    print ''
    print 'Average Daily Return of Fund :', res['avg_fund_daily_rets']
    print 'Average Daily Return of S&P :', res['avg_SPX_daily_rets']


def run(initial_cash, orders_file, values_file=None):
    df_orders, symbols = orders_into_df(orders_file)

    df_holdings, value_frame, cash = marketsim(initial_cash, df_orders, symbols)

    if values_file is not None:
        values_to_csv(values_file, value_frame)

    res = analyze(value_frame)
    return res


if __name__ == '__main__':
    initial_cash = sys.argv[1]
    orders_file = sys.argv[2]
    values_filename = sys.argv[3]

    res = run(initial_cash, orders_file, None)
    print_analyze(res)
