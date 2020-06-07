import mysql.connector
from mysql.connector import errorcode

#Finding how much memory it takes https://stackoverflow.com/questions/6474591/how-can-you-determine-how-much-disk-space-a-particular-mysql-table-is-taking-up
class sql:

    def __init__(self):
        try:
            self.mydb = mysql.connector.connect(user='sql3346026', password='9NjuSrd8Sv',
                                      host='sql3.freemysqlhosting.net',
                                      database='sql3346026')
            print("success")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def add(self,sku,price):
        cursor = self.mydb.cursor()

        sql = "INSERT INTO SKU (SKU, Price) VALUES (%s, %s)"
        val = (sku,price)
        cursor.execute(sql, val)

        self.mydb.commit()

        print(cursor.rowcount, "record inserted. with SKU value of ",sku,"and price of ",price)

    def exist(self,sku):
        """

        :param sku: SKU of Walmart's item
        :return:

        If Exist: Cost of item
        If Not Exist: False
        """
        cursor = self.mydb.cursor()
        exist_statement = "SELECT Price FROM SKU WHERE SKU='{}'".format(sku)
        cursor.execute(exist_statement)
        result = cursor.fetchone()

        if result == None:
            return False
        else:
            return True

    def close(self):
        self.mydb.close()
