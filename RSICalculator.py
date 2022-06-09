from Robinhood import Robinhood
import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import numpy as np
import pandas as pd
from os import listdir

robinhood_client = Robinhood()
robinhood_client.login(username='nzemtzov@g.hmc.edu', password='NeoQuantReloaded')

def getPercentMoveForDay(ticker,d,data):#note that day must be in form YYYY-MM-DD and quote data must be from RH historicals by day like l = robinhood_client.get_historical_quotes("BCDA", 'day','year')['results'][0]['historicals']
    for i in range(len(data)):
        if data[i]["begins_at"][:10] == d:
            return round((float(data[i]["close_price"])-float(data[i-1]["close_price"]))*100/float(data[i-1]["close_price"]),2)

def getRSIdefault(ticker,Date,data):#finds the RSI for a stock after the close on the specified day
    historicalQuote = data
    listOfDaysRSI = listOfDays[listOfDays.index(str(Date))-13:listOfDays.index(str(Date))+1]#date back here
    movesForLastDays = []
    for i in range(14):
        movesForLastDays.append(getPercentMoveForDay(ticker, listOfDaysRSI[i], historicalQuote))
    #at this point i have the list of all the moves over the last 14 days part 1:

    tempG = []
    tempL = []
    for value in movesForLastDays:
        if value > 0:
            tempG.append(value)
        else:
            tempL.append(value)
    averageGain = sum(tempG)/14
    averageLoss = abs(sum(tempL))/14
    RSI = 100 - (100/(1+(averageGain/averageLoss)))
    return RSI

def getOversold(day,numberOfStocks):
    finalDict = {}
    for ticker in allTickers:
        df = pd.read_csv("BackTesting/MomentumTestingData/" + ticker + ".csv")
        values = df["RSI"].tolist()
        index = df["Date"].tolist()
        i = index.index(day)
        if values[i] != 100 and values[i] != 0:
            finalDict.update({ticker:values[i]})
    
    finalTickers = []
    for i in range(numberOfStocks):
        finalTickers.append(min(finalDict,key=finalDict.get))
        del finalDict[min(finalDict,key=finalDict.get)]

    moves = []
    for ticker in finalTickers:
        df = pd.read_csv("BackTesting/MomentumTestingData/" + ticker + ".csv")
        index = df["Date"].tolist()
        i = index.index(day)
        moves.append(df["PercentChange"].tolist()[i+1])

    return finalTickers, moves




'''def getDeltaRSI(ticker,Date):
    RSItoday = getRSIdefault(ticker,Date)
    RSIyesterday = getRSIdefault(ticker,Date - timedelta(days = 1))
    print(RSItoday)
    print(RSIyesterday)
    return RSItoday - RSIyesterday

def getRSIofRSI(ticker,Date):
    listOfDaysRSI = listOfDays[listOfDays.index(str(Date))-14:listOfDays.index(str(Date))]#date back here'''

#def getEMAdefault(ticker,Date):
#    listOfDaysEMA = listOfDays[listOfDays.index(str(Date))-14:listOfDays.index(str(Date))]#date back here
'''def fourier():
    dx = 0.001
    L = np.pi
    x = L*np.arrange(-1+dx,1+dx,dx)
    n = len(x)
    nquart = int(np.floor(n/4))

    f = np.zeros_like(x)
    f[nquart:2*nquart] = (4/n)*np.arrange(1,nquart+1)'''



listOfDays = []
quote = robinhood_client.get_historical_quotes("SPY", 'day','year')['results'][0]['historicals']
filenames = listdir("BackTesting/MomentumTestingData")
allTickers = sorted([filename.split(".")[0] for filename in filenames])[1:]
for i in quote:
    listOfDays.append(i["begins_at"][:10])

backTest = []
for day in listOfDays[15:-2]:
    picks, nextDayMoves = getOversold(day,10)
    backTest.append(sum(nextDayMoves)/len(nextDayMoves))
    
print(sum(backTest)/len(backTest))







#add RSI
'''
filenames = listdir("BackTesting/MomentumTestingData")
allTickers = sorted([filename.split(".")[0] for filename in filenames])[1:]
for ticker in allTickers:
    try:
        q = robinhood_client.get_historical_quotes(ticker, 'day','year')['results'][0]['historicals']
        df = pd.read_csv("BackTesting/MomentumTestingData/" + ticker + ".csv")
        temp = ["NaN"]*14
        for i in range(len(listOfDays[14:])):
            try:
                temp.append(round(getRSIdefault(ticker, listOfDays[listOfDays.index("2019-07-23")+i], q),2))
            except:
                temp.append(100)
        df["RSI"] = temp
        df.to_csv("BackTesting/MomentumTestingData/" + ticker + ".csv",index=False)
        print(allTickers.index(ticker))
    except:
        print(ticker)
'''


#want RSI of RSI, want EMA, want MACD, then do forier series on it