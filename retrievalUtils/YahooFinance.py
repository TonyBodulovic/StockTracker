from database.DatabaseHandler import DatabaseHandler
from retrievalUtils.DictHelper import tryDictPath

import requests
import datetime

class YahooFinance:

    def __init__(self):

        self.APILINKS = {
            "Summary" : {
                "APIComponents":("https://query1.finance.yahoo.com/v8/finance/chart/",""),
                "FormatFunction" : self._formatSummaryToDicts
            },

            "NameQuery" : {
                "APIComponents":("https://query2.finance.yahoo.com/v1/finance/search?q=",""),
                "FormatFunction" : self._formatNameQueryToDict
            }
        }
        return
    
    def fetchAPIRequest(self,Symbol,InfoType):

        APIComponents = self.APILINKS[InfoType]["APIComponents"]

        url = ("{}{}{}".format(
            APIComponents[0],
            Symbol.upper(),
            APIComponents[1]
            )
        )

        headers = {
            'User-Agent': 'Definitely-NOT-Python' #Required since default requests User-Agent is blocked by Yahoo
        }

        fetchResult = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if fetchResult.status_code == 200:
            fetchResult = fetchResult.json()
        else:
            print("Problem occured with fetch - status code: ", fetchResult.status_code)
            return
        return self.APILINKS[InfoType]["FormatFunction"](fetchResult)
    
    def _formatSummaryToDicts(self,fetchResult):
        StockValues,DateValues,AssetValues,SourceValues = DatabaseHandler.getBlankDicts()

        result = tryDictPath(fetchResult,("chart","result"))
        if result == None:
            return
        result = result[0]

        StockValues["LastPrice"] = tryDictPath(result,("meta","regularMarketPrice"))
        StockValues["DayHigh"] = tryDictPath(result,("meta","regularMarketDayHigh"))
        StockValues["DayLow"] = tryDictPath(result,("meta","regularMarketDayLow"))
        StockValues["Volume"] = tryDictPath(result,("meta","regularMarketVolume"))

        tempDateInt = tryDictPath(result,("meta","regularMarketTime"))
        if tempDateInt != None:
            tempDateTime = datetime.datetime.fromtimestamp(tempDateInt)
        
            tempTime = tempDateTime.time()
            time = "{}:{}:{}".format(tempTime.hour,tempTime.minute,tempTime.second)
            day = "{:02d}".format(tempDateTime.day)
            month = "{:02d}".format(tempDateTime.month)
            year = tempDateTime.year
            date = "{}-{}-{}".format(year,month,day)

            DateValues["date"] = date
            DateValues["time"] = time
            DateValues["day"] = day
            DateValues["month"] = month
            DateValues["year"] = year
        
        AssetValues["symbol"] = tryDictPath(result, ("meta","symbol"))
        if AssetValues["symbol"] != None:
            AssetValues["name"] = self.fetchAPIRequest(AssetValues["symbol"],"NameQuery")
        AssetValues["stocktype"] = tryDictPath(result, ("meta","exchangeName"))

        SourceValues["name"] = "YahooFinance"
        SourceValues["exchange"] = tryDictPath(result, ("meta","fullExchangeName"))

        tableDict = {
            "StockValues" : StockValues,
            "DateValues" : DateValues,
            "AssetValues" : AssetValues,
            "SourceValues" : SourceValues
        }

        return tableDict

    def _formatNameQueryToDict(self,fetchResult):
        quotes = tryDictPath(fetchResult,("quotes"))
        if quotes == None:
            return
        quotes = quotes[0]
        longName = tryDictPath(quotes,("longname"))
        return longName