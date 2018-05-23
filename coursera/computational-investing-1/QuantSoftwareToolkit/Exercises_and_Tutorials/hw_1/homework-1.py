import sys

# sys.path.insert(0, '../')
# print(sys.path)

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

"""
Characterizes portolio in 1-year window with:
* Standard deviation of daily returns (risk)
* Average dailt return
* Sharpe Ratio
* Cumulaive returns

Finds best allocation of portolio by sharpe optimization. 
"""


def do_plot(timestamps, values, symbols, y_legend):
    plt.clf()
    plt.plot(timestamps, values)
    plt.legend(symbols)
    plt.ylabel(y_legend)
    plt.xlabel('Date')
    plt.show()


def simulate(startdate, enddate, symbols, allocations):
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startdate, enddate, timeofday)

    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['close']
    ldf_data = c_dataobj.get_data(timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    prices = d_data['close'].values
    normalized_prices = (prices / prices[0, :])
    # do_plot(timestamps, normalized_prices, symbols, 'Normalized close')
    portfolio_value = np.dot(normalized_prices, np.array(allocations).reshape(4, 1))

    daily_rets_portfolio = portfolio_value.copy()
    tsu.returnize0(daily_rets_portfolio)
    avgDailyReturn = np.mean(daily_rets_portfolio)
    sqStdDev = np.std(daily_rets_portfolio)
    k = 252
    sharpeRatio = (k ** (1 / 2.0)) * (avgDailyReturn / sqStdDev)
    cum_return = portfolio_value[portfolio_value.shape[0] - 1][0]

    return sqStdDev, avgDailyReturn, sharpeRatio, cum_return


def print_simulate(startdate, enddate, symbols, allocations):
    vol, daily_ret, sharpeRatio, cum_return = simulate(startdate, enddate, symbols, allocations)
    print('Start Date:', startdate.strftime("%B %-d, %Y"))  # The - removes the trailing 0
    print('End Date:', enddate.strftime("%B %-d, %Y"))
    print('Symbols:', symbols)
    print('Optimal Allocations:', allocations)
    print('Sharpe Ratio:', sharpeRatio)
    print('Volatility (stdev of daily returns):', vol)
    print('Average Daily Return:', daily_ret)
    print('Cumulative Return:', cum_return)


def best_allocation(startdate, enddate, symbols):
    max_sharp = -1
    best_allocation = list()
    for e1 in np.arange(0.0, 1.0, 0.1):
        for e2 in np.arange(0.0, 1.0, 0.1):
            for e3 in np.arange(0.0, 1.0, 0.1):
                for e4 in np.arange(0.0, 1.0, 0.1):
                    if (e1 + e2 + e3 + e4) == 1:
                        vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, symbols, [e1, e2, e3, e4])
                        print('Trying', [e1, e2, e3, e4], 'sharpe:', sharpe)
                        if sharpe > max_sharp:
                            max_sharp = sharpe
                            best_allocation = [e1, e2, e3, e4]

    print('Best allocation:')
    print_simulate(startdate, enddate, symbols, best_allocation)


if __name__ == '__main__':
    startdate = dt.datetime(2010, 1, 1)
    enddate = dt.datetime(2010, 12, 31)
    symbols = ['C', 'GS', 'IBM', 'HNZ']
    allocations = [0.25, 0.25, 0.25, 0.25]

    # print_simulate(startdate, enddate, symbols, allocations)
    best_allocation(startdate, enddate, symbols)
