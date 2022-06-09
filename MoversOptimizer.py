import pandas as pd

import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import pytz

CategoryOfInterest = "OverSold"
firstDate = date(2020, 4, 27)#change this whenever updating
lastDate = date(2020, 6, 24)
listOfDays = []
for i in range(int(str(lastDate-firstDate).split(" ")[0])+1):
    listOfDays.append(str(firstDate + timedelta(days = i)))

winningDays = 0
days = 0
OverallWinnings = []
RestrictionWinnings = []
for f in listOfDays:
    try:
        OverallMove = []#round(float([s.rstrip() for s in open("DailyMoversData/" + f + CategoryOfInterest + ".txt").readlines()][-1][13:23]),2) dont use this cuz there is actually significant variation
        RestrictionMove = []
        df = pd.read_csv("MoversTrainingData/"+ f + ".csv")
        df = df.dropna()
        for index,row in df.iterrows():
            if row["Index"] == CategoryOfInterest:
                OverallMove.append(row["target"])
                if row["Volume"] > 100000:
                    if row["Owners"] > 200:
                        #if row["PercentMoveToday"] < -10:
                        RestrictionMove.append(row["target"])
                            #if row["DaysOnIndex"] == 1: #based on days on index
                            #    RestrictionMove.append(row["target"])
        print(OverallMove)
        print(RestrictionMove)
        print(sum(OverallMove)/len(OverallMove))
        print(sum(RestrictionMove)/len(RestrictionMove))
        if RestrictionMove > OverallMove:
            winningDays = winningDays + 1
        days = days + 1
        OverallWinnings.append(sum(OverallMove)/len(OverallMove))
        RestrictionWinnings.append(sum(RestrictionMove)/len(RestrictionMove))
    except:
        pass
print(str(winningDays) + "/" + str(days))
print(sum(OverallWinnings))
print(sum(RestrictionWinnings))
print(winningDays/days)#looking for greater than 0.5

#so the best strategies are volume > 100000, owners > 200, which will yield higher average gains but less total
#the more required owners, the better the overall performance but worse better days
'''
#createTheOverallCSV
for day in listOfDays:
    try:
        df = pd.read_csv("MoversNNTrainingData/" + day + ".csv")
        main_df = main_df.append(df.dropna())
    except:
        print(day)
main_df.drop("Ticker",axis="columns",inplace=True)
main_df.Index = main_df.Index.map({"Gainers":1,"Losers":2,"GainersMinusOverBought":3,"OverBought":4,"OverSold":5})
main_df.to_csv("AAAAAA.csv",index=False)
main_df = pd.read_csv("AAAAAA.csv")
inputs = main_df.drop("target",axis="columns")
targets = main_df["target"]
'''