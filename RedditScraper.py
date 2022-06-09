import praw
import pandas as pd

import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import pytz


reddit = praw.Reddit(client_id='0ixzVEao1zAXVw', client_secret='CJ9qiOIOkYMDv4D7e6r4II4YGAM', user_agent='NeoQuantReddit')

NUM_MAIN_PAGE_THREADS = 15
SUBREDDITS = ['wallstreetbets', 'RobinHood','stocks','investing','StockMarket']

def getTextFromSubreddits(NUM_MAIN_PAGE_THREADS, SUBREDDITS):#Gets all most seen comments and subcomments on top threads
    df = pd.read_csv("TradeableStonksReddit.csv")
    listOfTickers = df["Ticker"].tolist()
    listOfNames = df["Name"].tolist()
    finalList = [0]*len(listOfNames)
    for subreddit in SUBREDDITS:
        hot_posts = reddit.subreddit(subreddit).hot(limit=NUM_MAIN_PAGE_THREADS)
        for post in hot_posts:
            submission = reddit.submission(id=post.id)
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                text = comment.body.replace("-"," ")
                text0 = text.replace(":"," ")#gets rid of extraneous syntax characters
                text1 = text0.replace(","," ")
                text2 = text1.replace("."," ")
                text3 = text2.replace("/"," ")
                string = text3.split(" ")
                for word in string:
                    if word.isupper() == True and word in listOfTickers:#new instance of ticker found
                        finalList[listOfTickers.index(word)] += 1
    tz_LA = pytz.timezone('America/Los_Angeles') 
    datetime_LA = datetime.now(tz_LA)
    currentTime = datetime_LA.strftime("%d/%m/%Y,%H:%M")
    df[currentTime] = finalList
    df.to_csv('TradeableStonksReddit.csv', index=False)

#listOfRemovedWords = ["Corp.", "Inc.", "Corporation", "The", "Inc", "plc", "Ltd.", "LTD", "Ltd", "Limited", "Incorporated", "N.A.", "Company", "Partners", "LP", "S.A.", "I", "II", "III", "(The)", "Corp", "Co.", "Co", "N.V.", "Holdings"]
def makeFileOfTradableStockTickersAndNames():#only need to call once to make the
    #full pandas dataframe of all the stock tickers and names of tradable stocks on the NYSE as of June 14th 2020
    FinalList = []
    f = [s.rstrip() for s in open("nasdaqlisted.txt").readlines()]
    for line in f[1:]:
        line0 = line.split("-")[0]
        line1 = line0.split("|")
        if len(line1) > 2:
            f.remove(line)
        else:
            line2 = line0.split(",")[0]
            line3 = line2.split("|")[1]#line3 is pretempered name
            line4 = line3.split(" ")
            for word in line4:
                if word in listOfRemovedWords:
                    line4.remove(word)
            line5 = ""
            for word in line4:
                line5 += str(word) + " "
            line6 = line5[:-1].strip()
            line7 = line6.split(".")[0]

            finalLine = []
            finalLine.append(line2.split("|")[0])
            finalLine.append(line7)
            add = True
            for line in FinalList:
                if line[1] == finalLine[1]:
                    add = False
            if add == True:
                FinalList.append(finalLine)

    finalListTickers = []
    finalListNames = []
    for line in FinalList:
        finalListTickers.append(line[0])
        finalListNames.append(line[1])
    data = {"Ticker": finalListTickers,
            "Name": finalListNames}

    TradableStonks = pd.DataFrame(data)
    TradableStonks.to_csv('TradeableStonksReddit.csv', index=False)

def showResults(columnName):
    df = pd.read_csv("TradeableStonksReddit.csv")
    listOfNames = df["Name"].tolist()
    listOfInstances = df[columnName].tolist()
    finalDict = {}
    for i in range(len(listOfInstances)):
        if listOfInstances[i] != 0:
            finalDict[listOfNames[i]] = listOfInstances[i]
    sortedDict = sorted(finalDict.items(), key=lambda x: x[1], reverse=True)
    for i in sortedDict:
        print(i[0], i[1])



#getTextFromSubreddits(NUM_MAIN_PAGE_THREADS,SUBREDDITS)
#makeFileOfTradableStockTickersAndNames()
#showResults("15/06/2020,12:23")





