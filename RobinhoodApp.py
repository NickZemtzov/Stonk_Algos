#note that whenever u install packages, u have to use "python3.8 -m pip install X" and to run use python3.8 X
#note all the files have the percentage at bottom. This is performance of the listed stocks the day after it says in the file name
#Also note that 2FA needs to be off to run this program
#note that when using daily data from robinhood, close is the last traded price for the trading day(not the previous trading day)
#NOTE: The robinhood api used for this is now out of date. New models must use robin-stocks
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random
import pandas as pd

from Robinhood import Robinhood

import requests
import urllib.request
from bs4 import BeautifulSoup

import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import pytz

import discord
from discord.ext import commands

def findTopMovers(inputUrl,robinhood_client):  #parse the top gainers page
    url = inputUrl
    response = requests.get(url)
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
    
def makeFileOfTopMovers(robinhood_client):
    topGainers = findTopMovers('https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/',robinhood_client)
    topLosers = findTopMovers('https://www.tradingview.com/markets/stocks-usa/market-movers-losers/',robinhood_client)
    topOverBought = findTopMovers('https://www.tradingview.com/markets/stocks-usa/market-movers-overbought/',robinhood_client)
    topOverSold = findTopMovers('https://www.tradingview.com/markets/stocks-usa/market-movers-oversold/',robinhood_client)
    f = open("DailyMoversData/" + str(date.today()) + "Gainers.txt","w+")
    for item in topGainers:
        f.write(item)
        f.write('\n')
    f.close()
    f = open("DailyMoversData/" + str(date.today()) + "Losers.txt","w+")
    for item in topLosers:
        f.write(item)
        f.write('\n')
    f.close()
    f = open("DailyMoversData/" + str(date.today()) + "OverBought.txt","w+")
    for item in topOverBought:
        f.write(item)
        f.write('\n')
    f.close()
    f = open("DailyMoversData/" + str(date.today()) + "OverSold.txt","w+")
    for item in topOverSold:
        f.write(item)
        f.write('\n')
    f.close()
    f = open("DailyMoversData/" + str(date.today()) + "GainersMinusOverBought.txt","w+")
    for item in topGainers:
        if item not in topOverBought:
            f.write(item)
            f.write('\n')
    f.close()

def addResultToLastDaysMovers(fileName, robinhood_client):
    percentageGainOfYesterdaysMovers = []
    f = [s.rstrip() for s in open(fileName).readlines()]
    numberOfStocks=0
    finalListToWriteToFile = []
    print(f)
    for ticker in f:
        try:
            numberOfStocks+=1
            stock_quote = robinhood_client.quote_data(ticker)
            openPrice = float(stock_quote["previous_close"])
            closePrice = float(stock_quote["last_trade_price"])
            percentChange = 100*(closePrice-openPrice)/openPrice
            percentageGainOfYesterdaysMovers.append(percentChange)
            print(ticker)
            finalListToWriteToFile.append(ticker)
        except:
            print()
    a=open(fileName,"w")
    for item in range(len(percentageGainOfYesterdaysMovers)):
        a.write(str(finalListToWriteToFile[item]))
        a.write(":")
        a.write(str(round(percentageGainOfYesterdaysMovers[item],2)))
        a.write("\n")
    a.write("Total%Change: " + str(sum(percentageGainOfYesterdaysMovers)/numberOfStocks))
    a.close()

def redRedRobin(robinhood_client, today, fileName):#redRedRobin(robinhood_client, today, "OverSold.txt")
    portfolio = robinhood_client.portfolios()
    freeCash = float(portfolio['equity']) #note for cash available youd subtract the invested equity from the total equity but everything should be sold at this point so just total equity works
    stocksFile = [s.rstrip() for s in open(str(today) + fileName,"r").readlines()]
    #select only afordable stocks
    for ticker in stocksFile:
        print(ticker)
        stock_quote = robinhood_client.quote_data(ticker)
        if float(stock_quote["last_trade_price"]) > freeCash/4:
            stocksFile.remove(ticker)
    #Randomly select 4 numbers
    RandomList=[]
    while len(RandomList)<4:
        r=random.randint(0,len(stocksFile))
        if r not in RandomList: RandomList.append(r)
    #select 4 stocks
    RandomStockTickers = []
    for i in RandomList:
        RandomStockTickers.append(stocksFile[i])
    #calculate shares possible to buy and money left over after buying
    sharesToBuy = []
    predictedCashAfterwards = freeCash
    for ticker in RandomStockTickers:
        stock_quote = robinhood_client.quote_data(ticker)
        sharesToBuy.append(int((freeCash/4)/float(stock_quote["last_trade_price"])))
        predictedCashAfterwards = predictedCashAfterwards - (int((freeCash/4)/float(stock_quote["last_trade_price"])) * float(stock_quote["last_trade_price"]))
    #buy an optimal share with leftover money
    finalStock = stocksFile[0]
    for ticker in stocksFile:
        stock_quote = robinhood_client.quote_data(ticker)
        finalStock_quote = robinhood_client.quote_data(finalStock)
        if float(stock_quote["last_trade_price"]) > float(finalStock_quote["last_trade_price"]) and float(stock_quote["last_trade_price"]) < predictedCashAfterwards:
            finalStock = ticker
    #ensure that it's not over the remaining money amount
    if float(finalStock_quote["last_trade_price"]) < predictedCashAfterwards:
        RandomStockTickers.append(finalStock)
        sharesToBuy.append(1)
        predictedCashAfterwards = predictedCashAfterwards - (int((freeCash/4)/float(finalStock_quote["last_trade_price"])) * float(finalStock_quote["last_trade_price"]))
    print(RandomStockTickers)
    print(sharesToBuy)
    print(predictedCashAfterwards)
    #buy and make a file of transactions
    f = open(str(today) + "StocksBought.txt","w+")
    correspondingSharesToBuyEntry = 0
    unbuyableStocks = 0
    for ticker in RandomStockTickers:
        stock_instrument = robinhood_client.instruments(ticker)[0]
        stock_quote = robinhood_client.quote_data(ticker)
        try:
            #buy_order = robinhood_client.place_market_buy_order(stock_instrument['url'], ticker, 'GFD', stock_quote['last_trade_price'], sharesToBuy[correspondingSharesToBuyEntry])
            print("bought " + sharesToBuy[correspondingSharesToBuyEntry] + " shares of " + ticker)
            f.write(ticker + ":" + str(sharesToBuy[correspondingSharesToBuyEntry]))
            f.write('\n')
            correspondingSharesToBuyEntry = correspondingSharesToBuyEntry + 1
        except:
            pass
    f.close()
     #if one of the chosen stocks isn't buyable, instead increase the amount of the first tradable stock bought
    if unbuyableStocks > 0:
        f = [s.rstrip() for s in open(str(today) + "StocksBought.txt","r").readlines()]
        reliableStock = f[0].split(':')[0]
        shares = f[0].split(':')[1]
        i = 0
        stock_instrument = robinhood_client.instruments(reliableStock)[0]
        stock_quote = robinhood_client.quote_data(reliableStock)
        while i < unbuyableStocks:
            #buy_order = robinhood_client.place_market_buy_order(stock_instrument['url'], reliableStock, 'GFD', stock_quote['last_trade_price'], shares)
            print("bought " + shares + " shares of " + reliableStock)
            i = i + 1
        f.close()

def getNumOwners(ticker):#the bit that may have to change as robinhood website changes
    url = "http://robinhood.com/stocks/" + ticker
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(response.text, "html.parser")
    whitelist = ['span']
    body = [t for t in soup.find_all(text=True) if t.parent.name in whitelist]
    result = 0
    print(body[0:10])
    try:
        result = int(body[0].replace(",",""))
    except:
        try:
            result = int(body[1].replace(",",""))
        except:
            try:
                result = int(body[2].replace(",",""))
            except:
                try:
                    result = int(body[3].replace(",",""))
                except:
                    pass
    return result

def displayChart(today):#must be executed after afterhours
    firstDate = date(2020, 4, 27)
    listOfDays = []
    for i in robinhood_client.get_historical_quotes("AAPL", 'day','year')['results'][0]['historicals']:
        listOfDays.append(i["begins_at"][:10])
    listOfDays = listOfDays[listOfDays.index(str(firstDate)):]
    listOfDays = listOfDays[:-1]#should have all the days that have recorded files

    SPYHistorical = robinhood_client.get_historical_quotes("SPY", 'day','year')['results'][0]['historicals']
    temp = 0
    for j in range(len(SPYHistorical)):
        if SPYHistorical[j]["begins_at"][:10] == str(firstDate):
            temp = j
    SPYHistorical = SPYHistorical[temp:]#spy only starts at firstDate as well

    listOfGainerMoves = [0]
    listOfLoserMoves = [0]
    listOfGainerMinusOverBoughtMoves = [0]
    listOfOverBoughtMoves = [0]
    listOfOverSoldMoves = [0]
    SPYChange = [0]


    for day in listOfDays:
        g = [s.rstrip() for s in open("DailyMoversData/" + day + "Gainers.txt").readlines()]
        l = [s.rstrip() for s in open("DailyMoversData/" + day + "Losers.txt").readlines()]
        gm = [s.rstrip() for s in open("DailyMoversData/" + day + "GainersMinusOverBought.txt").readlines()]
        ob = [s.rstrip() for s in open("DailyMoversData/" + day + "OverBought.txt").readlines()]
        os = [s.rstrip() for s in open("DailyMoversData/" + day + "OverSold.txt").readlines()]
        
        listOfGainerMoves.append(round(float(listOfGainerMoves[-1]) + float(g[-1][14:])+float(g[-1][14:])*float(listOfGainerMoves[-1]/100),2))
        listOfLoserMoves.append(round(float(listOfLoserMoves[-1]) + float(l[-1][14:])+float(l[-1][14:])*float(listOfLoserMoves[-1]/100),2))
        listOfGainerMinusOverBoughtMoves.append(round(float(listOfGainerMinusOverBoughtMoves[-1]) + float(gm[-1][14:])+float(gm[-1][14:])*float(listOfGainerMinusOverBoughtMoves[-1]/100),2))
        listOfOverBoughtMoves.append(round(float(listOfOverBoughtMoves[-1]) + float(ob[-1][14:])+float(ob[-1][14:])*float(listOfOverBoughtMoves[-1]/100),2))
        listOfOverSoldMoves.append(round(float(listOfOverSoldMoves[-1]) + float(os[-1][14:])+float(os[-1][14:])*float(listOfOverSoldMoves[-1]/100),2))
        

        for i in range(len(SPYHistorical)):
            if SPYHistorical[i]["begins_at"][:10] == day:
                SPYChange.append(round((float(SPYHistorical[i+1]["close_price"])-float(SPYHistorical[0]["close_price"]))*100/float(SPYHistorical[0]["close_price"]),2))
    domain = []
    for i in range(len(listOfDays)+1):
        domain.append(i)

    plt.plot(domain, listOfGainerMoves, color="red", linewidth=3, label="Gainers")
    plt.plot(domain, listOfOverBoughtMoves, color="blue", linewidth=3, label="OverBought")
    plt.plot(domain, listOfGainerMinusOverBoughtMoves, color="purple", linewidth=3, label="GainersWithoutOverbought")
    plt.plot(domain, listOfLoserMoves, color="orange", linewidth=3, label="Losers")
    plt.plot(domain, listOfOverSoldMoves, color="green", linewidth=3, label="OverSold")
    plt.plot(domain, SPYChange, color = 'black', linewidth = 5, label="Nasdaq")
    plt.legend(loc='upper left', frameon=False)
    plt.show()

def prepareStockPicks(today):
    stocksFile = [s.rstrip() for s in open("DailyMoversData/" + str(today) + "OverSold.txt","r").readlines()]
    print(stocksFile)
    removed = []
    for stock in stocksFile:
        try:
            print(stock)
            data = robinhood_client.get_historical_quotes(stock, 'day','week')['results'][0]['historicals']
            volumes = []
            for i in data[:-1]:
                volumes.append(int(i['volume']))
            print("volume = " + str(sum(volumes)/len(volumes)))
            
            owners = getNumOwners(stock)
            print("Owners: " + str(owners))

            if sum(volumes)/len(volumes) < 100000 or owners < 200:
                removed.append(stock)
                print("removed")
            print()
        except:
            removed.append(stock)
            print("removed")
            print()
    for stock in removed:
        stocksFile.remove(stock)
                
    if not stocksFile:
        stocksFile.append("Do not buy anything today")
    print(stocksFile)
    return stocksFile

def useDiscord(listOfStocks):
    client = commands.Bot(command_prefix = ".")

    @client.event
    async def on_ready():
        print("Bot is ready")
        channel = client.get_channel(703751230056562792)
        finalString = ""
        for item in listOfStocks:
            finalString += item + "\n"
        await channel.send(finalString)
    
    #@client.command()
    #async def ping(ctx):
    #    await ctx.send("Pong")
    
    @client.command()
    async def s(ctx):
        await ctx.bot.logout()
    client.run("NzIyNzIyMTI5NjE0NzMzMzg0.XunNgQ.hDaFGc3pzDCzYBJUNVc9-Stlmrc")

def findLastTradingDay(today):
    last10DaysList = []
    for i in range(10):
        last10DaysList.append(today - timedelta(days = i))
    for day in last10DaysList:
        try:
            f = open("DailyMoversData/" + str(day) + "OverSold.txt","r")
            return day
        except:
            pass

def sellPortfolio():
    for ticker in CurrentlyHeld.keys():
        try:
            stock_instrument = robinhood_client.instruments(ticker)[0]
            order = robinhood_client.place_limit_sell_order(stock_instrument['url'], ticker, 'GTC', float(robinhood_client.quote_data(ticker)['last_trade_price']), CurrentlyHeld[ticker])
        except:
            ErrorsToSend.append("Failed to submit limit sell for " + ticker + ".")
        time.sleep(2)
        try:
            ActiveOrderIDs.append(order.json()['id'])
        except:
            ErrorsToSend.append("Failed To add limit sell order code to list of codes for " + ticker + ".")

def cancelLimitOrders():
    for order in ActiveOrderIDs:
        try:
            cancel_order = robinhood_client.cancel_order(order)
            time.sleep(2)
            print("sold " + ticker + " as market")
        except:
            print("sold " + ticker + " as limit")

def sellPortfolioMarket(TodaysRecs):
    for ticker in CurrentlyHeld.keys():
        Sell = True
        for ticker2 in TodaysRecs:
            if ticker == ticker2:
                Sell = False
        if Sell == True:
            try:
                stock_instrument = robinhood_client.instruments(ticker)[0]
                sell_order = robinhood_client.place_market_sell_order(stock_instrument['url'], ticker, 'GFD', CurrentlyHeld[ticker])
                CurrentlyHeld.pop(ticker)
            except:
                ErrorsToSend.append("Failed to sell " + ticker + ". Sell manually.")

def CalculateOrders(stocks):
    finalDict = {}
    portfolio = robinhood_client.portfolios()
    freeCash = float(portfolio['equity']) - float(portfolio["market_value"])

    ownedStocks = CurrentlyHeld.keys()
    buyingStocks = []
    for stock in stocks:
        Buy = True
        for s in ownedStocks:
            if s == stock:
                Buy = False
        if Buy == True:
            buyingStocks.append(stock)

    cashPerStock = freeCash/len(stocks)
    for ticker in buyingStocks:
        price = robinhood_client.quote_data(ticker)['last_trade_price']
        shares = int(cashPerStock/float(price))
    finalDict.append({ticker:shares})
    return finalDict

def BuyMarket(orders):
    for order in orders:
        try:
            stock_instrument = robinhood_client.instruments(order)[0]
            sell_order = robinhood_client.place_market_buy_order(stock_instrument['url'], ticker, 'GFD', orders[order])
        except:
            ErrorsToSend.append("Failed to buy " + ticker + ". Buy manually.")



#MAIN
robinhood_client = Robinhood()
robinhood_client.login(username='nzemtzov@g.hmc.edu', password='onetobilinayear')
tz_LA = pytz.timezone('America/Los_Angeles') 
datetime_LA = datetime.now(tz_LA)
weekday = datetime_LA.weekday()
today = date.today() 
yesterday = today - timedelta(days = 1)
if weekday == 0:
    yesterday = today - timedelta(days = 3)
currentTime = datetime_LA.strftime("%H:%M")






#Example retrieving data from robinhood
#print(robinhood_client.get_historical_quotes('MSFT', 'day','week')['results'][0]['historicals'])
#this is current price minus price 5 years ago divided by price 5 years ago (percent change)
#print(((float(robinhood_client.quote_data('MSFT')['last_trade_price'])-float(robinhood_client.get_historical_quotes('MSFT', 'week','year')['results'][0]['historicals'][0]['close_price']))/float(robinhood_client.get_historical_quotes('MSFT', 'week','year')['results'][0]['historicals'][0]['close_price']))*100)
#gets row at that index
#print(main_df.iloc[6])
# If you want to drop a ticker
#main_df.drop(main_df.loc[main_df["Ticker"]==ticker].index.values)


#displayChart(today)
makeFileOfTopMovers(robinhood_client)
#addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "Gainers.txt", robinhood_client)
#addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "Losers.txt", robinhood_client)
#addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "OverBought.txt", robinhood_client)
#addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "OverSold.txt", robinhood_client)
#addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "GainersMinusOverBought.txt", robinhood_client)
#s = prepareStockPicks(today)
#useDiscord(s)

#stock_instrument = robinhood_client.instruments('HTZ')[0]
#order = robinhood_client.place_limit_buy_order(stock_instrument['url'], 'HTZ', 'GTC', 4.1, 1) #limit price of $4.10, one share
#order_id = order.json()['id']
#time.sleep(60)
#print(robinhood_client.portfolios())
#temp = robinhood_client.quote_data('TSLA')['last_trade_price'], robinhood_client.quote_data('NVDA')['last_trade_price']
#print(temp)
ActiveOrderIDs = []
ErrorsToSend = []
stocksToBuy = []
'''
MarketIsOpen = True
CurrentlyHeld = {"AUY":5} #THIS NEEDS TO BE RESET EVERY TIME THE ALGO IS STARTED. It should be the current holdings.
for i in CurrentlyHeld:
    print(CurrentlyHeld[i])



while True:
    #setup
    tz_LA = pytz.timezone('America/Los_Angeles') 
    datetime_LA = datetime.now(tz_LA)
    weekday = datetime_LA.weekday()
    today = date.today()
    yesterday = findLastTradingDay(today)
    currentTime = datetime_LA.strftime("%H:%M")

    #check to see if the market is open by seeing if the market changes value over a period of 5 min. starts at 1230 and takes >5min
    if str(currentTime[0]) + str(currentTime[1]) + str(currentTime[3]) + str(currentTime[4]) == "1230":
        print(str(currentTime[0]) + str(currentTime[1]) + str(currentTime[3]) + str(currentTime[0]))
        temp = robinhood_client.quote_data('TSLA')['last_trade_price'], robinhood_client.quote_data('NVDA')['last_trade_price']
        time.sleep(300)
        temp2 = robinhood_client.quote_data('TSLA')['last_trade_price'], robinhood_client.quote_data('NVDA')['last_trade_price']
        if temp != temp2:
            MarketIsOpen = True
            #ErrorsToSend = []
        else:
            MarketIsOpen = False
        print(MarketIsOpen)

    #Calculate then sell what isn't still a buy
    if str(currentTime[0]) == "1" and str(currentTime[1]) == "2" and str(currentTime[3]) == "4" and str(currentTime[4]) == "0" and MarketIsOpen == True:
        print("Starting...")
    #calculate the main stuff
        makeFileOfTopMovers(robinhood_client)
        addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "Gainers.txt", robinhood_client)
        addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "Losers.txt", robinhood_client)
        addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "OverBought.txt", robinhood_client)
        addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "OverSold.txt", robinhood_client)
        addResultToLastDaysMovers("DailyMoversData/" + str(yesterday) + "GainersMinusOverBought.txt", robinhood_client)
        stocksToBuy = prepareStockPicks(today)

        print("Selling...")
        sellPortfolioMarket(stocksToBuy)
        
    #Calculated restricted set then buy
    if str(currentTime[0]) == "1" and str(currentTime[1]) == "2" and str(currentTime[3]) == "5" and str(currentTime[4]) == "0" and MarketIsOpen == True:
        orders = CalculateOrders(stocksToBuy)
        BuyMarket(orders)

        useDiscord(ErrorsToSend)
        useDiscord(stocksToBuy)
        ErrorsToSend = []
        stocksToBuy = []

        time.sleep(1000)
    time.sleep(10)
    print(CurrentlyHeld)

#make sure you also give error messages if it stops working for some reason'''