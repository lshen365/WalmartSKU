import mysql.connector
from mysql.connector import errorcode

#Finding how much memory it takes https://stackoverflow.com/questions/6474591/how-can-you-determine-how-much-disk-space-a-particular-mysql-table-is-taking-up
class sql:

    def __init__(self):
        try:
            # self.mydb = mysql.connector.connect(user='sql3346026', password='9NjuSrd8Sv',
            #                           host='sql3.freemysqlhosting.net',
            #                           database='sql3346026')
            self.mydb = mysql.connector.connect(user='Leon', password='teacher1',
                                              host='73.181.19.81',
                                              database='SKU')
            print("success")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def add(self,data):
        """
        Inserts into Main Database
        :param data: Sql command
        :type data: String
        :return: None
        :rtype: None
        """
        cursor = self.mydb.cursor()

        sql = "INSERT INTO SKU (SKU, Price,Filter) VALUES (%s, %s, %s)"
        cursor.executemany(sql, data)

        self.mydb.commit()

        print(cursor.rowcount, "record inserted")

    def exist(self,sku,table):
        """
        Checks if an Item exists given the SKU and Table Name
        :param sku: SKU of Walmart's item
        :return:
        If Exist: Cost of item
        If Not Exist: False
        """
        cursor = self.mydb.cursor()
        exist_statement = "SELECT Price FROM {} WHERE SKU='{}'".format(table,sku)
        cursor.execute(exist_statement)
        result = cursor.fetchone()
        cursor.close()
        if result == None:
            return False
        else:
            return True

    def filterByCategory(self,category):
        """
        Returns all known items based off given category
        :param category: Filter Name
        :type category: String
        :return: All rows given the category
        :rtype: Tuple (Sku,Price)
        """
        cursor = self.mydb.cursor()
        query = "SELECT SKU,Price FROM SKU WHERE Filter='{}'".format(category)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def createStoreTable(self,id):
        """
        Creates a new table given  ID
        :param id: Store ID
        :type id: String
        :return: None
        :rtype: None
        """
        cursor = self.mydb.cursor()
        query = "CREATE TABLE Walmart{} (sku VARCHAR(16),price int(11),availability BOOLEAN,location VARCHAR(60))".format(id)
        print("Successfully created a database")
        cursor.execute(query)
        cursor.close()

    def insertStoreEntry(self,store_id,sku,price,exist,location):
        """
        Inserts into store the item, price, availability, and location
        :param store_id: Store Location
        :type store_id: String
        :param sku: Sku Number
        :type sku: String
        :param price: Price of Item
        :type price: Float
        :param exist: Availability of Item
        :type exist: Boolean
        :param location: Where Item is stored
        :type location: String
        :return: None
        :rtype: None
        """
        cursor = self.mydb.cursor()
        query = "INSERT INTO Walmart{} (sku, Price, availability, location) VALUES ('{}',{},{},'{}')".format(store_id,sku,price,exist,location)
        print("Successfully inserted Walmart{} with SKU={} entry".format(store_id,sku))
        cursor.execute(query)
        cursor.close()
        self.mydb.commit()

    def getAvailableKnownInStoreItems(self,store_id):
        """
        Returns all available items at the store
        :param store_id: Store Number
        :type store_id: Int
        :return: Returns all Available items
        :rtype: Tuples (Sku,Price,Location)
        """
        cursor = self.mydb.cursor()
        query = "SELECT sku,Price,location FROM Walmart{} WHERE availability=1 and price!=-1".format(store_id)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def getMsrpPrice(self,sku):
        """
        Grabs the original price from Walmart.com
        :param sku: Item Sku
        :type sku: String
        :return: Price of the item
        :rtype: Float
        """
        cursor = self.mydb.cursor()
        query = "SELECT Price FROM SKU WHERE sku='{}'".format(sku)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result

    def getCategory(self,sku):
        """
        Gets the Category based off sku
        :param sku: Item Sku
        :type sku: String
        :return: Filter Name
        :rtype: String
        """
        cursor = self.mydb.cursor()
        query = "SELECT Filter FROM SKU WHERE sku='{}'".format(sku)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result

    def deleteSKU(self,sku,table_name):
        """
        Deletes SKU inside the table
        :param sku: Item Sku
        :type sku: String
        :param table_name: Name of the Table
        :type table_name: String
        :return: None
        :rtype: None
        """
        cursor = self.mydb.cursor()
        query = "DELETE FROM {} WHERE SKU='{}'".format(table_name,sku)
        cursor.execute(query)
        cursor.close()
        self.mydb.commit()

    def updateValue(self,table,sku,price,availability,location):
        """
        Changes the SKU,Price,Availability,Location of the given table
        :param table: Table Name
        :type table: String
        :param sku: Item Sku
        :type sku: String
        :param price: Price of Item
        :type price: Float
        :param availability: Availability of Item
        :type availability: Boolean (1 = Exists 0 = Not Exist)
        :param location: Where Item is located at store
        :type location: String
        :return:
        :rtype:
        """
        cursor = self.mydb.cursor()
        query = "UPDATE {} SET Price={},availability={},location='{}' WHERE sku='{}'".format(table,price,availability,location,sku)
        cursor.execute(query)
        cursor.close()
        print("Updated Prices/Location/Availability for SKU={}".format(sku))
        self.mydb.commit()

    def close(self):
        self.mydb.close()

