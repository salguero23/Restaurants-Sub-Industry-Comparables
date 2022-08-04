import os
import time
import pandas as pd
import yfinance as yf
import numpy as np
# from tqdm import tqdm


# Fundtion to clean folders to actual ticker value
def clean_tickers(str):
    x = str.replace('-','/')
    return x

# Function to calculate beta
def beta(ticker):
    tseries = yf.download(['^GSPC',ticker],period='5y',interval='1mo')['Adj Close']
    tseries.ffill(inplace=True)
    tseries = np.log1p(tseries.pct_change())

    covariance = tseries.cov().loc[ticker,'^GSPC']
    variance = tseries.var().loc['^GSPC']
    beta = covariance / variance

    return beta


indices = [folder for folder in os.listdir() if '.' not in folder]
indices = list(map(clean_tickers,indices))
# columns = ['Enterpirse Value','Free Cash Flow','Financing']
data = pd.DataFrame(index=indices)



for ticker in indices:
    try:
        equity = yf.Ticker(ticker)

        try:
            # valuation and beta for clustering
            marketcap = equity.get_info()['marketCap']
            data.loc[ticker,'Market Cap'] = marketcap            
            
            enterprisevalue = equity.get_info()['enterpriseValue']
            data.loc[ticker,'Enterprise Value'] = enterprisevalue            
        except:
            print(f'Could not locate valuation for {ticker}.')

        try:
            # balance sheet data
            assets = equity.balancesheet.loc['Total Assets'][0]
            data.loc[ticker,'Assets'] = assets

            inventory = equity.balancesheet.loc['Inventory'][0]
            data.loc[ticker,'Inventory'] = inventory
        except:
            print(f'Could not locate balance sheet data for {ticker}.')

        try:
            # cash flow statement
            freeCashFlow = (equity.cashflow.loc['Total Cash From Operating Activities'] + equity.cashflow.loc['Capital Expenditures'])[0]
            data.loc[ticker,'Free Cash Flow'] = freeCashFlow

            financing = equity.cashflow.loc['Total Cash From Financing Activities'][0]
            data.loc[ticker,'Financing'] = financing
        except:
            print(f'Could not locate cash flow data for {ticker}.')

        try:
            # ratios and beta
            margin = (equity.financials.loc['Gross Profit'] / equity.financials.loc['Total Revenue'])[0]
            data.loc[ticker,'Gross Margin'] = margin

            BETA = beta(ticker)
            data.loc[ticker,'Beta'] = BETA
        except:
            print(f'Could not locate ratios and beta for {ticker}.')
        
        time.sleep(1)
    except:
        print(f"Couldn't  connect to {ticker}")


# Convert to millions
data.iloc[:,:-2] /= 1000000
print(data.head())
data.to_csv('cluster.csv')