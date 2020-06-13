import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
from database import sql
import time
class Walmart:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),options=self.chrome_options)
        #self.driver = webdriver.Chrome("/usr/bin/chromedriver",options = self.chrome_options) This is for Raspberry Pi
        self.filters = ['TV','Tablet/Accessories','Laptop/Desktop','Router','PC Parts','GPS','Camera','Drone','Camera','Headhones']

    # def createPage(self,url):
    #     html = self.driver.get(url)
    #     return html

    def filterPrice(self,text):
        """
        Helper function to filter out the price and random unecessary text.

        :param text: Current Text returned by css selector which includes a lot of mumbo jumbo
        :return:
        Float-  The actual price which can be added into the database
        """
        regex = "(\d+.\d+)"
        matches = re.findall(regex,text)
        if len(matches) == 4: #Lists current price twice and non-sale price twice which accounts for 4. Matching the max
            return float(matches[2])
        elif len(matches) == 2: #If there is no sale, then there will be two matches as current price will be listed twice
            return float(matches[0])
        else:
            return None
    def scrapeProduct(self,url,db,desc):
        """
        Scrapes all the products on the page with the SKU/Price

        :param url: Link to the Walmart Page
        :type url: String
        :param db: Database instance
        :type db: SQL Object
        :param desc: Category of filter
        :type desc: String
        :return: Data = an array of tuples which contains the (SKU,Price) of each item on the page
        :rtype: Array of Tuples
        """
        self.driver.get(url)
        try:
            main_search_div = self.driver.find_element_by_id("mainSearchContent")
            search_product_result_id = main_search_div.find_element_by_id("searchProductResult")
            elements = search_product_result_id.find_elements_by_xpath("//li[contains(@data-tl-id,'ProductTileGridView')]")
            data = []
            if elements != NoSuchElementException:
                count = 0
                for elem in elements:
                    try:
                        url =str(elem.find_element_by_css_selector("a[data-type='itemTitles']").get_attribute("href"))
                        location = url.rfind("/")
                        sku = url[location+1:len(url)]
                        price = self.filterPrice(elem.find_element_by_css_selector("span[class='search-result-productprice gridview enable-2price-2']").text)

                        if price != None and not db.exist(sku) and len(sku) < 16:
                            data.append((sku,price,desc))
                        elif db.exist(sku):
                            print("The product with sku of {} already exists".format(sku))
                    except NoSuchElementException:
                        print("{} has problem with finding a[data-type='itemTitles'] or span[class='search-result-productprice gridview enable-2price-2']".format(url))
                return data
            else:
                print("No elements found on: ",url)
        except NoSuchElementException:
            print("Error with {} either mainSearchContent or searchProductResult".format(url))

    def loadDatabase(self,database):
        """

        :param database: Database instance
        :type database: Sql()
        :return: N/A
        :rtype: N/A
        """
        websites=[]
        locations = [] #Keeps a track of locations for each filter in the notepad
        with open('websites.txt') as read:
            count = 0;
            for line in read:
                if line[0] != '#':
                    websites.append(line.rstrip('\n'))
                    count+=1
                else:
                    if count != 0:
                        locations.append(count)
        id = 0
        for position in range(len(websites)):
            if position == (locations[id]):
                id+=1
            description = self.filters[id]
            for i in range(1,26):
                link = websites[position]
                html_tag = "?page="+str(i)
                newurl=link+html_tag
                print(newurl)
                time0=time.time()
                data = test.scrapeProduct(newurl,database,description)
                database.add(data)
                time1=time.time()
                print(time1-time0)

    def addCookies(self,zipcode):
        """

        :param zipcode: Zipcode of current location
        :type zipcode: int
        :return: N/A
        :rtype: N/A
        """
        cookie = {"name": "bs_zip", "value" : str(zipcode)}
        self.driver.get("https://brickseek.com")
        self.driver.add_cookie(cookie)

    def pricePageSource(self,sku):
        url = "https://brickseek.com/walmart-inventory-checker/?sku="+sku
        self.driver.get(url)

        print("Click")
        self.driver.find_element_by_xpath("//div[@class='grid__item-content']//button[@type='submit']").send_keys("\n")
        try:

            page = WebDriverWait(self.driver,10).until(

                EC.presence_of_element_located((By.CLASS_NAME,'table__body'))
            )
            page_source = self.driver.page_source
            #self.driver.close()
            return page_source
        except:
            print("Product not available at current location")
            return False

    def isDiscounted(self,currPrice,originalPrice):
        discount = 1-(currPrice/originalPrice)
        if(discount > 0.5):
            return True
        return False

    def checkSale(self, db): #Do NOT USE unless with VPN
        """
        Checks sales from Brickseek
        :param db:
        :type db:
        :return:
        :rtype:
        """
        elements = db.filterByCategory(self.filters[0])
        page_source = self.pricePageSource("547940259")
        if page_source != False:
            soup = BeautifulSoup(page_source,'lxml')
            locations = []
            location_price = soup.find_all('div', class_='table__row')
            for loc in location_price:
                print("195775096",len(location_price))
                #print(loc)
                price = loc.find(class_="price-formatted__dollars")
                if price != None:
                    price = float(price.get_text())
                    if self.isDiscounted(price,398):

                        place = loc.find(class_="address")
                        locations.append(place)
                        print("Found discount")
        #             else:
        #                 print("no discount")
        # for query in elements:
        #     page_source = self.pricePageSource(query[0])
        #     if page_source != False:
        #         soup = BeautifulSoup(page_source,'lxml')
        #         locations = []
        #         location_price = soup.find_all('div', class_='table__row')
        #         for loc in location_price:
        #             price = loc.find(class_="price-formatted__dollars")
        #             if price != None:
        #                 price = float(price.get_text())
        #                 if self.isDiscounted(price,query[1]):
        #                     place = loc.find(class_="address")
        #                     locations.append(place)
        #                     print("Found discount",query[0],place)
        #                 # else:
        #                 #     print("no discount")

    def walmartID(self):
        """
        Grabs all of Walmart's location ID's
        :return:
        :rtype:
        """
        self.driver.get("https://www.allstays.com/c/walmart-colorado-locations.htm")
        stores = self.driver.find_elements_by_xpath("//a[@class='full-width button']")
        id = []
        for x in stores:
            value = x.text[len(x.text)-4:len(x.text)]
            id.append(value)
        print(len(id))

        self.driver.close()

    def checkWalmart(self):
        #https://www.walmart.com/store/1045/search?query=247544454




database = sql()
test = Walmart()
test.walmartID()
# test.loadDatabase(database)
# test.addCookies(80016)
# test.checkSale(database)
database.close()






