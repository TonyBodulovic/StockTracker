import mysql.connector

class DatabaseHandler:
    
    def __init__(self):

        """
        Do NOT remove connection from object -> It will get garbage collected
        Once the connection leaves function scope it's gone...
        It MUST be contained as an object variable
        """
        self.Connection, self.Cursor = self.initializeConnection()
        self.initializeDatabase()
        
    def initializeConnection(self):

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            autocommit=True
        )
        return db, db.cursor(buffered=False)
    
    def endConnection(self):
        self.Cursor.close()
        self.Connection.close()

    def removeDatabase(self):
        self.Cursor.execute("DROP DATABASE IF EXISTS StockFinderDB")

    def initializeDatabase(self):
        self.Cursor.execute("CREATE DATABASE IF NOT EXISTS StockFinderDB")
        self.Cursor.execute("USE StockFinderDB")

        StockPricesColumns = (
            "id INT NOT NULL AUTO_INCREMENT",
            "date_id INT",
            "asset_id INT",
            "source_id INT",
            "LastPrice FLOAT",
            "Volume INT",
            "DayHigh FLOAT",
            "DayLow FLOAT",
            "PRIMARY KEY (id,date_id,asset_id,source_id)"
        )
        DateDimColumns = {
            "id INT NOT NULL AUTO_INCREMENT",
            "date DATE",
            "time TIME",
            "day INT",
            "month INT",
            "year INT",
            "PRIMARY KEY (id)"
        }
        AssetDimColumns = {
            "id INT NOT NULL AUTO_INCREMENT",
            "symbol VARCHAR(255)",
            "name VARCHAR(255)",
            "stocktype VARCHAR(255)",
            "PRIMARY KEY (id)"
        }
        SourceDimColumns = {
            "id INT NOT NULL AUTO_INCREMENT",
            "name VARCHAR(255)",
            "exchange VARCHAR(255)",
            "url VARCHAR(255)",
            "PRIMARY KEY (id)"
        }

        StockPricesTable = self._formatColumnsToTable(StockPricesColumns)
        DateDimTable = self._formatColumnsToTable(DateDimColumns)
        AssetDimTable = self._formatColumnsToTable(AssetDimColumns)
        SourceDimTable = self._formatColumnsToTable(SourceDimColumns)
        

        self.Cursor.execute("CREATE TABLE IF NOT EXISTS StockPrices ({})".format(StockPricesTable))
        self.Cursor.execute("CREATE TABLE IF NOT EXISTS DateDim ({})".format(DateDimTable))
        self.Cursor.execute("CREATE TABLE IF NOT EXISTS AssetDim ({})".format(AssetDimTable))
        self.Cursor.execute("CREATE TABLE IF NOT EXISTS SourceDim ({})".format(SourceDimTable))

    
    def InsertQueries(self,tableDict):

        dateDimRowID = self.InsertQuery("DateDim",tableDict["DateValues"])
        assetDimRowID = self.InsertQuery("AssetDim",tableDict["AssetValues"])
        sourceDimRowID = self.InsertQuery("SourceDim",tableDict["SourceValues"])

        tableDict["StockValues"]["date_id"] = dateDimRowID
        tableDict["StockValues"]["asset_id"] = assetDimRowID
        tableDict["StockValues"]["source_id"] = sourceDimRowID

        self.InsertQuery("StockPrices",tableDict["StockValues"])

    def InsertQuery(self, table: str, valueDict: dict) -> int:
        """
        Inserts a query into a table
        table : name of table
        columns : list of columns
        values : list of values
        -> Indexes of columns and values are linked
        Returns true/false on success/fail
        """
        selectColumns = []
        selectValues = []
        insertColumns = []
        insertValues = []

        for column, value in valueDict.items():
            selectColumns.append(str(column))
            selectValues.append(value)
            if value != None:
                insertColumns.append(str(column))
                insertValues.append(value)

        if table == "AssetDim":
            query = "SELECT id FROM {} WHERE {}".format(table,self._formatConditionsToWhere(["symbol"],[valueDict["symbol"]]))
        else:
            query = "SELECT id FROM {} WHERE {}".format(table,self._formatConditionsToWhere(selectColumns,selectValues))
        queryResult = self.SelectQuery(query)
        if queryResult != []:
            return queryResult[0][0]

        insertColumns = str(tuple(insertColumns)).replace("'","")
        insertValues = str(tuple(insertValues))
        query = "INSERT INTO {} {} VALUES {}".format(table,insertColumns,insertValues)

        try:
            self.Cursor.execute(query)
            return self.Cursor.lastrowid
        except:
            return -1

    
    def SelectQuery(self, query: str) -> list:
        """
        Executes a select query and returns result
        """
        self.Cursor.execute(query)
        queryResultRaw = self.Cursor.fetchall()
        if len(queryResultRaw) < 1:
            return []
        queryResults = []
        for rawResult in queryResultRaw:
            queryResults.append([item for item in rawResult])

        return queryResults
    
    def executeQuery(self,query):
        self.Cursor.execute(query)

    def showCursor(self):
        for x in self.Cursor:
            print(x)

    @staticmethod
    def _formatColumnsToTable(columns):
        outputTable = ""
        for column in columns:
            outputTable += column + ", "
        outputTable = outputTable[:-2]
        return outputTable
    
    @staticmethod
    def _formatConditionsToWhere(columns,values):

        if len(columns) != len(values) or len(columns) < 1:
            return ""
        
        query = DatabaseHandler._formatConditionToString(columns[0],values[0])
        
        if len(columns) == 1:
            return query

        andString = " AND "
        for i in range(1,len(columns)):
            query += andString + DatabaseHandler._formatConditionToString(columns[i],values[i])
        
        return query
    
    @staticmethod
    def _formatConditionToString(variable,value):
        if value == None:
            return "{} IS NULL".format(variable)
        else:
            return "{}=\'{}\'".format(variable,value)
        
    
    @staticmethod
    def getBlankDicts() -> list:
        """
        Returns a tuple containing blank dicts
        (StockValues,DateValues,AssetValues,SourceValues)
        """
        StockValues = {
            "date_id" : None,
            "asset_id" : None,
            "source_id" : None,
            "LastPrice" : None,
            "Volume" : None,
            "DayHigh" : None,
            "DayLow" : None
        }
        DateValues = {
            "date" : None,
            "time" : None,
            "day" : None,
            "month" : None,
            "year" : None
        }
        AssetValues = {
            "symbol" : None,
            "name" : None,
            "stocktype" : None
        }
        SourceValues = {
            "name" : None,
            "exchange" : None,
        }
        return (StockValues,DateValues,AssetValues,SourceValues)