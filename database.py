import mysql.connector
from mysql.connector import errorcode
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
        mycursor = self.mydb.cursor()

        sql = "INSERT INTO WALMART (name, address) VALUES (%s, %s)"
        val = (sku,price)
        mycursor.execute(sql, val)

        self.mydb.commit()

        print(mycursor.rowcount, "record inserted.")

test = sql()
test.add("18934583",93.5)