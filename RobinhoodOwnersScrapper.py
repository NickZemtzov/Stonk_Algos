import requests
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import aiohttp
import asyncio
import ssl
#How to BS: https://stackoverflow.com/questions/12451997/beautifulsoup-gettext-from-between-p-not-picking-up-subsequent-paragraphs

def getNumOwners(text):#the bit that may have to change as robinhood website changes
    whitelist = ['span']
    body = [t for t in text.find_all(text=True) if t.parent.name in whitelist]
    return body[3]

async def fetch(session, url):
    async with session.get(url, ssl=ssl.SSLContext()) as response:
        return await response.text()

async def fetch_all(urls, loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        results = await asyncio.gather(*[fetch(session, url) for url in urls], return_exceptions=True)
        return results

#make list of urls to use
df = pd.read_csv("TradeableStonksReddit.csv")
tlds = df["Ticker"].tolist()
url_list = ['http://robinhood.com/stocks/{}'.format(x) for x in tlds]
#runs the stufff
loop = asyncio.get_event_loop()
urls = url_list
htmls = loop.run_until_complete(fetch_all(urls, loop))

#gets the number of owners and says its zero if url isn't found
finalList = []
for html in htmls:
    try:
        soup = BeautifulSoup(html, "html.parser")
        finalList.append(getNumOwners(soup))
    except:
        finalList.append(0)

#final processing
for idx, item in enumerate(finalList):
    if item == ".":
        finalList[idx] = 0

