from retrievalUtils.NASDAQ import NASDAQ
from retrievalUtils.YahooFinance import YahooFinance
from database.DatabaseHandler import DatabaseHandler

from os import getcwd
from time import sleep


class StockTracker:

    def __init__(self):
        self.DBHandle = DatabaseHandler()
        self.NASDAQHandle = NASDAQ()
        self.YahooHandle = YahooFinance()
        
        self.StockList = self.getStockList()

    def start(self):
        return

    def getStockList(self) -> list:

        filePath = ("{}\\StockTrackerList.txt".format(getcwd()).replace("\\\\","\\"))
        file = open(filePath, "r")

        stockList = []
        for line in file.readlines():
            stockList.append(line.strip())

        file.close()

        return stockList

    def fetchStocks(self,stockList):

        fetchlist = []

        for stock in stockList:
            fetchlist.append(self.NASDAQHandle.fetchAPIRequest(stock,"Summary"))
            fetchlist.append(self.YahooHandle.fetchAPIRequest(stock,"Summary"))

        return fetchlist

    def startScheduler(self):
        while True:
            try:
                tableDicts = self.fetchStocks(self.StockList)
                for tableDict in tableDicts:
                    self.DBHandle.InsertQueries(tableDict)
            except Exception as e:
                print("Error: {}".format(e))
            print("Scheduler Iteration Completed.")
            sleep(300)




    def test(self):    

    # x=self.YahooHandle.fetchAPIRequest("GOOG","Summary")
    # print(x)
    #     tableDicts = self.fetchStocks(self.StockList)
    #     for tableDict in tableDicts:
    #         self.DBHandle.InsertQueries(tableDict)
    #     ------------------------------------------

    #     DBHandle = DatabaseHandler()
    #     NASDAQHandle = NASDAQ()
    #     NASDAQHandle.fetchAPIRequest("intc","Summary")

    #     x = self.DBHandle.SelectQuery("SELECT * FROM StockPrices")
    #     print(x)

    #     x = ["test","test2"]
    #     y = [1,"here"]
    #     DBHandle.InsertQuery("StockPrices",x,y)

    #     queryResult = self.DBHandle.SelectQuery("SELECT * FROM DateDim WHERE date = '2024-05-10' AND time='04:02:00' AND day='10' AND month='05' AND year='2024'")
    #     print(queryResult)
        return


if __name__ == "__main__":
    ST = StockTracker()
    # ST.test()
    ST.startScheduler()


