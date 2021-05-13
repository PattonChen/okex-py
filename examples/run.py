
import okex.v5.account_api as account
import okex.v5.market_api as market
import okex.v5.trade_api as trade
from okex.v5.ccytype import CcyType
from okex.exceptions import OkexRequestException
import json
import datetime
import time
import traceback

import numpy as np
import requests
from tenacity import retry, stop_after_attempt

import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd


if __name__ == '__main__':

    with open('api.json', 'r', encoding='utf-8') as f:
        obj = json.loads(f.read())
    api_key = obj['api_key']
    secret_key = obj['secret_key']
    passphrase = obj['passphrase']

    is_test = True
    accountAPI = account.AccountAPI(api_key, secret_key, passphrase, False, test=is_test)
    marketAPI = market.MarketAPI(api_key, secret_key, passphrase, False, test=is_test)
    tradeAPI = trade.TradeAPI(api_key, secret_key, passphrase, False, test=is_test)

    # env
    cerebro = bt.Cerebro()

    # Create a Data Feed

    dataframe = marketAPI.candles('ETH-USDT')
    dataframe = dataframe.rename(
        columns={
            'ts':'datetime',
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'vol': 'volume'})
    dataframe = dataframe.set_index("datetime", drop=True)
    dataframe = dataframe.drop(columns=['volCcy'])
    dataframe = dataframe.replace([np.inf, -np.inf], np.nan).dropna()
    print(dataframe)
    data = bt.feeds.PandasData(dataname=dataframe)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)


    cerebro.broker.setcash(100000.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot(style='bar')