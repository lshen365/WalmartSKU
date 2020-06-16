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
        cursor = self.mydb.cursor()

        sql = "INSERT INTO SKU (SKU, Price,Filter) VALUES (%s, %s, %s)"
        cursor.executemany(sql, data)

        self.mydb.commit()

        print(cursor.rowcount, "record inserted")

    def exist(self,sku,table):
        """

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
        cursor = self.mydb.cursor()
        query = "SELECT SKU,Price FROM SKU WHERE Filter='{}'".format(category)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def createStoreTable(self,id):
        cursor = self.mydb.cursor()
        query = "CREATE TABLE Walmart{} (sku VARCHAR(16),price int(11),availability BOOLEAN,location VARCHAR(60))".format(id)
        print("Successfully created a database")
        cursor.execute(query)
        cursor.close()

    def insertStoreEntry(self,store_id,sku,price,exist,location):
        cursor = self.mydb.cursor()
        query = "INSERT INTO Walmart{} (sku, Price, availability, location) VALUES ('{}',{},{},'{}')".format(store_id,sku,price,exist,location)
        print("Successfully inserted Walmart{} with SKU={} entry".format(store_id,sku))
        cursor.execute(query)
        cursor.close()
        self.mydb.commit()

    def close(self):
        self.mydb.close()
