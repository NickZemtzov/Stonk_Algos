from Robinhood import Robinhood
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import requests
import urllib.request
from bs4 import BeautifulSoup
import plotly.express as px
import pandas as pd


def findTopGainers():  #parse the top gainers page
    response = requests.get('https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/')
    text = response.text
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.findAll('tr')
    listOfTickers = []
    for item in body:
        text = item.get_text()
        text = text.split(" ")
        ticker = ""
        for i in range (4,10):
            if text[0][i] != "\n" and text[0][i] != "\t":
                ticker += (text[0][i])
            #test to see if ticker is traded on the hood
        try:
            stock_instrument = robinhood_client.instruments(ticker)[0]
            stock_quote = robinhood_client.quote_data(ticker)
            listOfTickers.append(ticker)
        except:
            pass
    return listOfTickers

def CalculateQuality(ticker):
    l = robinhood_client.get_historical_quotes(ticker, '5minute','day')['results'][0]['historicals']
    data = []
    for i in l:
        data.append(float(i["open_price"]))
    temp = []
    for i in data:
        temp.append((i-min(data))/(max(data)-min(data)))
    data = np.array(temp)
    time = np.array([n for n in range(len(data))]).reshape((-1, 1))
    regressor = LinearRegression()
    regressor.fit(time, data)
    predictions = regressor.predict(time)
    print(ticker)
    print('Mean Squared Error:', metrics.mean_squared_error(data, predictions)*100)
    print(regressor.coef_*100)
    return  regressor.coef_*100, metrics.mean_squared_error(data, predictions)*100

robinhood_client = Robinhood()
robinhood_client.login(username='nzemtzov@g.hmc.edu', password='NeoQuantReloaded')

AllInfo = []
PossibleTickers = findTopGainers()
for ticker in PossibleTickers:
    m, r2 = CalculateQuality(ticker)
    AllInfo.append([ticker,m,r2])


AllM = []
AllR2 = []
Tickers = []
for i in range(len(AllInfo)):
    Tickers.append(AllInfo[i][0])
    AllM.append(AllInfo[i][1][0])
    AllR2.append(AllInfo[i][2])
df = pd.DataFrame(columns=['Ticker', 'm', 'r2'])
df['Ticker'] = Tickers
df["m"] = AllM
df["r2"] = AllR2
print(df.head())
fig = px.scatter(df, x="r2", y="m",hover_data=["Ticker"])
fig.show()

