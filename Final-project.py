# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 10:09:55 2022

@author: lulac
"""

# Library Definitions
import krakenex
from pykrakenapi import KrakenAPI
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd

class DataRetrieval:
    def __post_init__(self, currency, date, name):
        self.currency = currency
        self.date = date
        self.name = name

    def connectKrakenAPI(self):
        try:
            api = krakenex.API('api-key-1668535705986')
            k = KrakenAPI(api)

            data = k.get_asset_info()
            data = pd.DataFrame(data)
        except:
            print("Connection could not be established")
        return k

    def getPairs(self):
        k = self.connectKrakenAPI()
        pairs = k.get_tradable_asset_pairs()
        pairs.head().T
        pairs = pd.DataFrame(pairs)
        return pairs

    def fetchData(self, currency, date, name):
        try:
            d = date.split("-")
            for x in range(len(d)):
                d[x] = int(d[x])
            date_time_start = datetime.date(d[0], d[1], d[2])
            date_x = date_time_start.timetuple()
            date_start = time.mktime(date_x)
        except SyntaxError:
            print("The entered date is not valid, and therefore, the transformation cannot be executed")

        connection = self.connectKrakenAPI()
        data = connection.get_ohlc_data(currency, interval=1440, since=date_start, ascending=True)
        data = data[0]
        data = pd.DataFrame(data)

        file_name = name + '.csv'
        data.to_csv(file_name, header=True, index=False)

        return data

class PlotGraphs:
    def __post_init__(self, data):
        self.data = data

    def plotCurrency(self, data, currency):
        fig, ax = plt.subplots()
        plt.title('ANALYSIS OF ' + currency, fontname='Times New Roman', fontweight='bold')
        plt.ylabel('Price in euros', fontname='Times New Roman', fontweight='bold')
        ax.grid(linestyle='dotted', linewidth=0.6)
        ax.tick_params(axis='x', rotation=60)
        ax.set_facecolor("ivory")

        plt.plot(data['open'], 'teal', label='Open')
        plt.plot(data['close'], 'SteelBlue', label='Close')
        plt.plot(data['high'], 'springgreen', label='High')
        plt.plot(data['low'], 'darkred', label='Low')
        plt.legend(loc='best', facecolor='w', fontsize=9)
        fig.set size_inches(12, 6)
        plt.savefig('currency_info' + currency, dpi=150, bbox_inches='tight')
        return plt.show()

    def plotCurrencyVWAP(self, data, currency):
        fig, ax = plt.subplots()
        plt.title('ANALYSIS OF ' + currency, fontname='Times New Roman', fontweight='bold')
        plt.xlabel("Date")
        plt.ylabel('Price in euros')
        ax.grid(linestyle='dotted', linewidth=0.6)
        ax.tick_params(axis='x', rotation=60)
        ax.set_facecolor("ivory")

        plt.plot(data['close'], 'turquoise', label='Close')
        plt.plot(data['vwap'], 'teal', label='VWAP')
        plt.legend(loc='best', facecolor='w', fontsize=9)
        fig.set_size_inches(12, 6)
        plt.savefig('vwap' + currency, dpi=150, bbox_inches='tight')
        plt.show()

    def candlestick(self, data):
        fig, ax = plt.subplots()

        plt.title('Price Oscillations of ' + currency, fontname='Times New Roman', fontweight='bold')
        ax.grid(linestyle='dotted', linewidth=0.6)
        ax.set_facecolor("ivory")

        width = 1.04
        width2 = 1.05

        up = data[data.close >= data.open]
        down = data[data.close < data.open]

        plt.bar(up.index, up.close - up.open, width, bottom=up.open, color='green')
        plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color='green')
        plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color='green')

        plt.bar(down.index, down.close - down.open, width, bottom=down.open, color='red')
        plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color='red')
        plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color='red')

        plt.xticks(rotation=45, ha='right')
        fig.set_size_inches(12, 6)
        plt.savefig('candlestick' + currency, dpi=150, bbox_inches='tight')
        return plt.show()

# Modify the code to use English variable names and comments
session_count = 20

def simple_moving_average(session_count):
    sma = []
    for i in range(0, len(data['close']) - session_count):
        total = 0
        for j in range(i, i + session_count):
            total = data['close'][j] + total
        sma_value = total / session_count
        sma.append(sma_value)
    return sma

def exponential_moving_average(session_count):
    multiplier = 2 / (session_count + 1)
    ema = []
    length = len(simple_moving_average(session_count))
    for j in range(0, length):
        total = 0
        total = multiplier * simple_moving_average(session_count)[j - 1] + simple_moving_average(session_count)[j - 1] + total
        ema_value = total
        ema.append(ema_value)
    return ema

def relative_strength_index(data, periods=session_count, ema=True):
    close_diff = data['close'].diff()
    up = close_diff.clip(lower=0)
    down = -1 * close_diff.clip(upper=0)

    if ema == True:
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

# Main program
currency = input("Enter the currency:")
date = input("Enter the starting date in the format: year-month-day ")
file_name = input("Name of the CSV file to save the data ")

data_retrieval = DataRetrieval()

pairs = data_retrieval.getPairs()
if currency in list(pairs['altname']):
    currency = currency
else:
    print("The entered currency does not exist")
    currency = input("Enter another currency:")

data = data_retrieval.fetchData(currency, date, file_name)

date_data = data.index
date_data = list(date_data)
data['new_date'] = [d.date() for d in date_data]
data['new_time'] = [d.time() for d in date_data]

data['time'] = data['new_date']
data = data.drop(['new_time'], axis=1)
data = data.drop(['new_date'], axis=1)

session_count = 20

sma_values = simple_moving_average(session_count)
sma_values = sma_values[::-1]

start_date = data['time'][session_count:]
sma_data = pd.DataFrame(sma_values, start_date)

rsi_values = relative_strength_index(data, periods=session_count, ema=True)
rsi_values = rsi_values[::-1]

rsi_data = pd.DataFrame(rsi_values, start_date)

fig, ax = plt.subplots()
plt.title('SIMPLE MOVING AVERAGE FOR ' + currency, fontname='Times New Roman', fontweight='bold')
ax.grid(linestyle='dotted', linewidth=0.6)
ax.tick_params(axis='x', rotation=60)
ax.set_facecolor("ivory")
plt.ylabel('Simple Moving Average', fontname='Times New Roman', fontweight='bold')
plt.plot(sma_data, 'teal', label='SMA')
plt.legend(loc='best', facecolor='w', fontsize=9)
fig.set_size_inches(12, 6)
plt.savefig('sma_' + currency, dpi=150, bbox_inches='tight')

fig, ax = plt.subplots()
plt.title('RSI FOR ' + currency, fontname='Times New Roman', fontweight='bold')
ax.grid(linestyle='dotted', linewidth=0.6)
ax.tick_params(axis='x', rotation=60)
ax.set_facecolor("ivory")
plt.ylabel('RSI Value', fontname='Times New Roman', fontweight='bold')
plt.plot(rsi_data, 'SteelBlue', label='RSI')
plt.legend(loc='best', facecolor='w', fontsize=9)
fig.set_size_inches(12, 6)
plt.savefig('rsi_' + currency, dpi=150, bbox_inches='tight')

# Other graphs
PlotGraphs.plotCurrency(data, currency)
PlotGraphs.plotCurrencyVWAP(data, currency)
PlotGraphs.candlestick(data)
