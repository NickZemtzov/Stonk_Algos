import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import pytz

FOLDER = "MoversTrainingData/"
FILES = []
firstDate = date(2020, 4, 27)#change this whenever updating
lastDate = date(2020, 6, 24)
for i in range(int(str(lastDate-firstDate).split(" ")[0])+1):
    FILES.append(str(firstDate + timedelta(days = i)))

def displayOwnersVSTarget(df):#displays all indexes on one graph differentiated by color
    x = np.array(df["Owners"].tolist())
    y = np.array(df["target"].tolist())
    colorMap = np.array(df["Index"].tolist())

    fig, ax = plt.subplots()
    cdict = {"Gainers":'red',"Losers":'orange',"GainersMinusOverBought":'purple',"OverBought":'blue',"OverSold":"green"}
    for g in np.unique(colorMap):
        ix = np.where(colorMap == g)
        ax.scatter(x[ix], y[ix], c=cdict[g], label=g)
    plt.show()

main_df = pd.read_csv(FOLDER + "2020-04-27.csv")
displayOwnersVSTarget(main_df.dropna())
#shuffle the rows then get a number from each equal to the min of each index
'''
for f in FILES:
    try:
        main_df = pd.read_csv(Folder + f + ".csv")
        displayOwnersVSTarget(main_df)
    except:
        pass'''
