from database.DatabaseHandler import DatabaseHandler
from retrievalUtils.DictHelper import tryDictPath

import requests

class NASDAQ:

    def __init__(self):

        self.HARDLINK = "https://www.nasdaq.com/market-activity/stocks/" # Web Scraping -> Append symbol in lowercase

        self.APILINKS = {
            "Summary" : ("https://api.nasdaq.com/api/quote/","/info?assetclass=stocks"),
        }

    def fetchAPIRequest(self,Symbol,InfoType):

        APIComponents = self.APILINKS[InfoType]

        url = ("{}{}{}".format(
            APIComponents[0],
            Symbol.upper(),
            APIComponents[1]
            )
        )

        headers = {
            'User-Agent': 'Definitely-NOT-Python' #Required since default requests User-Agent is blocked by NASDAQ
        }

        fetchResult = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if fetchResult.status_code == 200:
            fetchResult = fetchResult.json()
        else:
            print("Problem occured with fetch - status code: ", fetchResult.status_code)
            return

        return self._formatFetchToDicts(fetchResult)

    def _formatFetchToDicts(self,fetchResult):

        StockValues,DateValues,AssetValues,SourceValues = DatabaseHandler.getBlankDicts()
        
        lastPrice = tryDictPath(fetchResult,("data","primaryData","lastSalePrice"))
        if lastPrice != None:
            lastPrice = lastPrice.replace("$","")

        dayhigh = None
        daylow = None
        dayRange = tryDictPath(fetchResult,("data","keyStats","dayrange","value"))

        if dayRange != None and dayRange != "NA":
            daylow = dayRange.split(" - ")[0]
            dayhigh = dayRange.split(" - ")[1]

        volume = tryDictPath(fetchResult,("data","primaryData","volume"))
        if volume != None:
            volume = volume.replace(",","")

        StockValues["LastPrice"] = lastPrice
        StockValues["DayHigh"] = dayhigh
        StockValues["DayLow"] = daylow
        StockValues["Volume"] = volume
        tempDate = tryDictPath(fetchResult,("data","primaryData","lastTradeTimestamp"))
        time = None
        day = None
        month = None
        year = None
        date = None

        if tempDate != None:

            if tempDate.find("AM ET")!= -1 or tempDate.find("PM ET") != -1:
                tempDate = tempDate.replace(" AM ET","")
                tempDate = tempDate.replace(" PM ET","")
                tempDate = tempDate.split(",")
                tempDate[1] = tempDate[1][1:]
                
                time = tempDate[1].split(" ")[1]
                time = time.split(":")
                time = "{:02d}:{:02d}:00".format(int(time[0]),int(time[1]))

                day = "{:02d}".format(int(tempDate[0].split(" ")[1]))
                month = self._monthToNumber(tempDate[0].split(" ")[0])
                year = tempDate[1].split(" ")[0]

                date = "{}-{}-{}".format(year,month,day)

            else:
                tempDate = tempDate.split(",")
                year = tempDate[1].replace(" ","")
                month = self._monthToNumber(tempDate[0].split(" ")[0])
                day = tempDate[0].split(" ")[1]

                date = "{}-{}-{}".format(year,month,day)
    
        DateValues["date"] = date
        DateValues["time"] = time
        DateValues["day"] = day
        DateValues["month"] = month
        DateValues["year"] = year

        AssetValues["symbol"] = tryDictPath(fetchResult, ("data","symbol"))
        AssetValues["name"] = tryDictPath(fetchResult, ("data","companyName"))
        AssetValues["stocktype"] = tryDictPath(fetchResult, ("data","stockType"))

        SourceValues["name"] = "NASDAQ"
        SourceValues["exchange"] = tryDictPath(fetchResult, ("data","exchange"))

        tableDict = {
            "StockValues" : StockValues,
            "DateValues" : DateValues,
            "AssetValues" : AssetValues,
            "SourceValues" : SourceValues
        }

        return tableDict


    @staticmethod
    def _monthToNumber(month):

        months = {
            "JAN" : "01",
            "FEB" : "02",
            "MAR" : "03",
            "APR" : "04",
            "MAY" : "05",
            "JUN" : "06",
            "JUL" : "07",
            "AUG" : "08",
            "SEP" : "09",
            "OCT" : "10",
            "NOV" : "11",
            "DEC" : "12",
        }

        return months[month.upper()]



# fetch = fetch("https://api.nasdaq.com/api/quote/INTC/info?assetclass=stocks", {
#   "headers": {
#     "accept": "application/json, text/plain, */*",
#     "accept-language": "en-US,en;q=0.9",
#     "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-site"
#   },
#   "referrer": "https://www.nasdaq.com/",
#   "referrerPolicy": "strict-origin-when-cross-origin",
#   "body": null,
#   "method": "GET",
#   "mode": "cors",
#   "credentials": "omit"
# });

# fetch("https://api.nasdaq.com/api/quote/INTC/info?assetclass=stocks", {
#   "headers": {
#     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "accept-language": "en-US,en;q=0.9",
#     "cache-control": "max-age=0",
#     "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "document",
#     "sec-fetch-mode": "navigate",
#     "sec-fetch-site": "none",
#     "sec-fetch-user": "?1",
#     "upgrade-insecure-requests": "1"
#   },
#   "referrerPolicy": "strict-origin-when-cross-origin",
#   "body": null,
#   "method": "GET",
#   "mode": "cors",
#   "credentials": "include"
# });

# def dbug(self):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
#     }

#     url = "https://api.nasdaq.com/api/quote/INTC/info?assetclass=stocks"

#     try:
#         r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
#         print(f"Status Code: {r.status_code}")

#         if r.url.startswith("https://"):
#             print("The website has redirected to the secure version (https).")
#         else:
#             print("The website did not redirect to the secure version (https).")

#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")