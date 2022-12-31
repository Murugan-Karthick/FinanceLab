# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 07:52:44 2022

@author: karthick
"""

# importing libraries
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# downloading nifty50 historical data from yfinance
nifty_df = yf.download('^NSEI',start='2010-01-01')

# methods to write text
st.write(""" # Momentum Driven Stock Analysis """)

# loading historical price of all stocks
df = pd.read_feather('data.feather')

# set a date as index
df.set_index('Date',inplace= True)

# typecasting dataframe index into datetime
df.index = pd.to_datetime(df.index)

# removing tickers which are not traded at 2010-01-01
df = df.loc[:,df.iloc[0,:].notnull()]

# copying dataframe for viewing stock movement of top picks
dataframe = df

# calculating monthly price change percentage of stocks
mtl = (df.pct_change() + 1)[1:].resample('M').prod()

# calculating monthly percentage change of nifty50
nifty_mtl = (nifty_df['Adj Close'].pct_change() + 1)[1:].resample('M').prod()

def get_rolling(df,n):
    '''
    method is to apply rolling on dataset based on n.
    '''
    return df.rolling(n).apply(np.prod)

# calculating monthly price change percentage for 12 month, 6 month and 3 month 
# ret_12, ret_6, ret_3 = get_rolling(mtl,12),get_rolling(mtl,6),get_rolling(mtl,3)
ret_12, ret_6, ret_3 = pd.read_feather('ret_12.feather'),pd.read_feather('ret_6.feather'),pd.read_feather('ret_3.feather')

# set a date as index
ret_12.set_index('Date',inplace= True)

# typecasting dataframe index into datetime
ret_12.index = pd.to_datetime(ret_12.index)

# set a date as index
ret_6.set_index('Date',inplace= True)

# typecasting dataframe index into datetime
ret_6.index = pd.to_datetime(ret_6.index)

# set a date as index
ret_3.set_index('Date',inplace= True)

# typecasting dataframe index into datetime
ret_3.index = pd.to_datetime(ret_3.index)

def get_top(date):
    '''
    method to select top 10 stocks
    '''
    top_50 = ret_12.loc[date].nlargest(50).index
    top_30 = ret_6.loc[date,top_50].nlargest(30).index
    top_10 = ret_3.loc[date,top_30].nlargest(10).index
    return top_10

def pf_performance(date):
    '''
    method will calculate the performance of strategy on particular date
    '''
    portfolio = mtl.loc[date:,get_top(date)][1:2]
    return portfolio.mean(axis=1).values[0]

returns = []
# we are taking all the monthly return except current month because it not ended
for date in mtl.index[:-1]:
    returns.append(pf_performance(date))
    
# comparing both nifty50 and strategy performance
st.write("### Performance of Nifty50 and Strategy")
combined = pd.DataFrame([pd.Series(nifty_mtl.cumprod().values.tolist()[:-1], index=mtl.index[:-1],name='Nifty50 Return'),pd.Series(returns,index=mtl.index[:-1],name='Strategy Return').cumprod()]).T
st.line_chart(combined)

query_date = st.selectbox(
    'Choose a Date to Pick Top Stocks:',
    tuple(ret_3.dropna().index.tolist())
    )

# get top stocks for given date
top_stocks = get_top(query_date)
st.write("### Top Stocks For a Date")
st.table(top_stocks)

# performance of top stocks on next month
performance_table = mtl.loc[query_date:,top_stocks][1:2]
st.write("### Performance of Top Stocks for Selected Date")
st.table(performance_table)

for stock in top_stocks.values.tolist():
    st.line_chart(dataframe.loc[query_date:performance_table.index[0],stock])