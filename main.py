from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from database import sql
from joblib import Parallel, delayed
import time
from JsonScrape import jsonLocator

class Walmart:
    def __init__(self):
        self.storeID = []
        self.filters = ['TV', 'Audio', 'Phone Case', 'Screen Protector', 'Cell Phone Accessories', 'Power Banks',
                        'Security Camera', 'Streaming Device', 'Smart Device', 'iPad/Tablet', 'Desktop/Laptop',
                        'Router', 'PC Parts', 'GPS', 'Camera', 'Drone', 'Camera Accessories', 'Headphones',
                        'Bluetooth Speakers', 'Garden']

    def getFilters(self):
        return self.filters

    def initChromeDriver(self):
        """
        Initializes Chrome Driver - self.driver
        :return: None
        :rtype:
        """
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=self.chrome_options)
        # self.driver = webdriver.Chrome("/usr/bin/chromedriver",options = self.chrome_options) #This is for Raspberry Pi
        print("Chrome Driver Initialized")

    def closeChromeDriver(self):
        self.driver.quit()
        print("Chrome Driver Quit")

    def filterPrice(self, text):
        """
        Helper function to filter out the price and random unecessary text.

        :param text: Current Text returned by css selector which includes a lot of mumbo jumbo
        :return:
        Float-  The actual price which can be added into the database
        """
        regex = "(\d+.\d+)"
        matches = re.findall(regex, text)
        if len(
                matches) == 4:  # Lists current price twice and non-sale price twice which accounts for 4. Matching the max
            return float(matches[2])
        elif len(
                matches) == 2:  # If there is no sale, then there will be two matches as current price will be listed twice
            return float(matches[0])
        else:
            return None

    def scrapeProduct(self, url, db, desc):
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
            elements = search_product_result_id.find_elements_by_xpath(
                "//li[contains(@data-tl-id,'ProductTileGridView')]")
            data = []
            if elements != NoSuchElementException:
                for elem in elements:
                    try:
                        url = str(elem.find_element_by_css_selector("a[data-type='itemTitles']").get_attribute("href"))
                        location = url.rfind("/")
                        sku = url[location + 1:len(url)]
                        price = self.filterPrice(elem.find_element_by_css_selector(
                            "span[class='search-result-productprice gridview enable-2price-2']").text)

                        if price != None and not db.exist(sku, 'SKU') and len(sku) < 16:
                            data.append((sku, price, desc))
                        elif db.exist(sku, 'SKU'):
                            print("The product with sku of {} already exists".format(sku))
                    except NoSuchElementException:
                        print(
                            "{} has problem with finding a[data-type='itemTitles'] or span["
                            "class='search-result-productprice gridview enable-2price-2']".format(
                                url))
                return data
            else:
                print("No elements found on: ", url)
        except NoSuchElementException:
            print("Error with {} either mainSearchContent or searchProductResult".format(url))

    def loadDatabase(self, database):
        """
        Loads the main Walmart Database from Walmart.com based off the known websites inside the websites.txt file

        :param database: Database instance
        :type database: Sql()
        :return: N/A
        :rtype: N/A
        """
        websites = []
        locations = []  # Keeps a track of locations for each filter in the notepad
        with open('websites.txt') as read:
            count = 0
            for line in read:
                if line[0] != '#':
                    websites.append(line.rstrip('\n'))
                    count += 1
                else:
                    if count != 0:
                        locations.append(count)
        id = 0
        for position in range(len(websites)):
            if position == (locations[id]):
                id += 1
            description = self.filters[id]
            for i in range(1, 26):
                link = websites[position]
                html_tag = "?page=" + str(i)
                newurl = link + html_tag
                print(newurl)
                time0 = time.time()
                data = test.scrapeProduct(newurl, database, description)
                database.add(data)
                time1 = time.time()
                print(time1 - time0)

    def addCookies(self, zipcode):
        """
        Adds Cookie to BrickSeek Website
        :param zipcode: Zipcode of current location
        :type zipcode: int
        :return: N/A
        :rtype: N/A
        """
        cookie = {"name": "bs_zip", "value": str(zipcode)}
        self.driver.get("https://brickseek.com")
        self.driver.add_cookie(cookie)

    def pricePageSourceBrickSeek(self, sku):
        """
        Returns the page source from BrickSeek's website
        :param sku: Item SKU number to look up on BrickSeek
        :type sku: string
        :return: Page Source (HTML Text)
        :rtype:  String
        """
        url = "https://brickseek.com/walmart-inventory-checker/?sku=" + sku
        self.driver.get(url)

        print("Click")
        self.driver.find_element_by_xpath("//div[@class='grid__item-content']//button[@type='submit']").send_keys("\n")
        try:

            page = WebDriverWait(self.driver, 10).until(

                EC.presence_of_element_located((By.CLASS_NAME, 'table__body'))
            )
            page_source = self.driver.page_source
            # self.driver.close()
            return page_source
        except:
            print("Product not available at current location")
            return False

    def isDiscounted(self, currPrice, originalPrice):
        """
        Checks if price is over 50% off
        :param currPrice: Current Price of the Local Store
        :type currPrice: Integer or Float
        :param originalPrice: Original Price of the main Database
        :type originalPrice: Integer or Float
        :return: True - Over 50% off
                 False - Less than 50% off
        :rtype: Boolean
        """
        discount = 1 - (currPrice / originalPrice)
        if discount > 0.5:
            return True
        return False

    def brickseekSale(self, db):  # Do NOT USE unless with VPN
        """
        Checks sales from Brickseek
        :param db:
        :type db:
        :return:
        :rtype:
        """
        elements = db.filterByCategory(self.filters[0])
        page_source = self.pricePageSourceBrickSeek("547940259")
        # Test code
        # if page_source != False:
        #     soup = BeautifulSoup(page_source,'lxml')
        #     locations = []
        #     location_price = soup.find_all('div', class_='table__row')
        #     for loc in location_price:
        #         print("195775096",len(location_price))
        #         #print(loc)
        #         price = loc.find(class_="price-formatted__dollars")
        #         if price != None:
        #             price = float(price.get_text())
        #             if self.isDiscounted(price,398):
        #
        #                 place = loc.find(class_="address")
        #                 locations.append(place)
        #                 print("Found discount")
        # #             else:
        #                 print("no discount")
        # Works for websites
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
        :return: None
        :rtype: None
        """
        self.driver.get("https://www.allstays.com/c/walmart-colorado-locations.htm")
        stores = self.driver.find_elements_by_xpath("//a[@class='full-width button']")
        id = []
        for x in stores:
            value = x.text[len(x.text) - 4:len(x.text)]
            id.append(value)
        print(len(id))

        self.driver.close()

    def loadWalmartId(self):
        """
        Reads the textfile WalmartID and stores into self.storeID
        :return: None
        :rtype: None
        """
        with open('WalmartID.txt') as read:
            for line in read:
                if line[0] != '#':
                    self.storeID.append(line.rstrip('\n'))

    def getProductPageSource(self, url):
        """
        Returns any page source given a url. Uses Selenium to load the Javascript to grab full HTML
        :param url: Link of the website
        :type url: String
        :return: HTML of the website
        :rtype: String
        """
        self.driver.get(url)
        page_source = self.driver.page_source
        self.driver.quit()
        return page_source

    def searchWalmart(self, url):
        """
        Returns the product name, price, and location
        :param url: Link of website
        :type url: String
        :return: Product Name, Price, and Location
        :rtype: String, String, String
        """
        # OOS 476550098
        # Not available 791149058
        walmart_json = jsonLocator(url)
        if walmart_json.doesExist():
            item_name = walmart_json.getTitle()
            item_price = None
            if walmart_json.getAvailability() == 1:
                item_price = walmart_json.getPrice()
            item_location = walmart_json.getStoreInventory()
            if walmart_json.getIsleLocation() is not None:
                item_location += "| " + walmart_json.getIsleLocation()
            return item_name, item_price, item_location

        return None, None, None

    def runParallelInsert(self, sku, id):
        """
        Inserts into local Walmart Database based off availability
        :param sku: SKU of Item
        :type sku: String
        :param id: Local Walmart ID
        :type id: String
        :return: None
        :rtype: None
        """
        try:
            db = sql()

            link = "https://www.walmart.com/store/electrode/api/search?query={}&stores={}".format(sku, id)
            print(link)
            if db.exist(sku, "Walmart{}".format(id)):
                print("{} already exists in the database with store id {}".format(sku, id))
            else:
                print(link)
                item_name, item_price, item_location = self.searchWalmart(link)
                #If Item Exists
                if item_name is not None:
                    #If Price is not found
                    if item_price is None:
                        db.insertStoreEntry(id, sku, -1, True, item_location)
                    #If Price is found
                    else:
                        db.insertStoreEntry(id, sku, int(float(item_price)), True, item_location)
                else:
                    db.insertStoreEntry(id, sku, -1, False, "None")
            db.close()
        except:
            print("Error with Connection to database")

    def checkWalmart(self, db, category):
        """
        Runs Parallel Processes To Insert Unknown Sku's into Local Walmarts
        :param db: Database
        :type db: Sql()
        :param category: Filter Category (Should be from self.filters)
        :type category: String
        :return: None
        :rtype: None
        """
        filterQueries = db.filterByCategory(category)
        # self.searchWalmart("https://www.walmart.com/store/1045/lafayette-co/search?query=791149058")
        for id in self.storeID:
            print("Current Category is: {}".format(category))
            test = Parallel(n_jobs=20)(delayed(self.runParallelInsert)(query[0], id) for query in filterQueries)

    def productOnSale(self,db):
        """
        Writes to file called deals.txt a list of all the deals that are over 50% off
        :param db: Database Instance
        :type db: Sql()
        :return: None
        :rtype: None
        """
        for store_id in self.storeID:
            for sku,price,location in db.getAvailableKnownInStoreItems(store_id):
                link = 'https://www.walmart.com/store/{}/search?query={}'.format(store_id,sku)
                try:
                    result = self.isDiscounted(price,db.getMsrpPrice(sku)[0])
                    if result <= 1:
                        line = "Discount Found at store {} with sku {} with category {} and link at {}\n".format(store_id,sku,db.getCategory(sku),link)
                        deals_file = open('deals.txt','a+')
                        deals_file.write(line)
                        deals_file.close()
                except:
                    print("Item does not exist in main database with SKU={}".format(sku))

    def removeSku(self,sku,db):
        """
        Deletes Sku from all Local Walmarts
        :param sku: Sku of the item
        :type sku: String
        :param db: Database Instance
        :type db: Sql()
        :return: None
        :rtype: None
        """
        for store_id in self.storeID:
            try:
                db.deleteSKU(sku,"Walmart{}".format(store_id))
            except:
                print("Does not exist in table")

    def updateTableParallel(self, sku, id):
        """
        Updates all the available item prices / locations/ and availability

        :param sku: Sku of item
        :type sku: String
        :param id: Walmart store ID
        :type id: String
        :return: None
        :rtype: None
        """
        try:
            db = sql()
            store_id = "Walmart{}".format(id)
            link = "https://www.walmart.com/store/electrode/api/search?query={}&stores={}".format(sku, id)
            print(link)
            item_name, item_price, item_location = self.searchWalmart(link)
            if item_name is not None:

                if item_price is None:
                    db.updateValue(store_id, sku, -1, True, item_location)
                else:
                    db.updateValue(store_id, sku, int(float(item_price)), True, item_location)
            else:
                db.updateValue(store_id, sku, -1, False, "None")
            db.close()
        except:
            print("Error with Connection to database")

    def updateTablePrices(self,db):
        """
        Runs Parallel Processes for updating table of known processes
        :param db: Database Instance
        :type db: Sql()
        :return: None
        :rtype: None
        """
        for store_id in self.storeID:
            Parallel(n_jobs=20)(delayed(self.updateTableParallel)(query[0], store_id) for query in db.getAvailableKnownInStoreItems(store_id))



if __name__ == "__main__":
    database = sql()
    test = Walmart()
    test.loadWalmartId()
    print("Enter the following:\n "
          "1) Load Database\n"
          "2) Load Local Walmarts\n"
          "3) Check for Discounts\n"
          "4) Delete SKU \n"
          "5) Update Table")
    response = input("Your Choice: ")
    if response == "1":
        test.initChromeDriver()
        test.loadDatabase(database)
        test.closeChromeDriver()
    elif response == "2":
        print("How many filters do you want to run?\n"
              "Choose the following:\n"
              "1,2,3,max")
        response = input()
        print(test.getFilters())
        if response == "1":
            print("Enter the filter name")
            filter1 = input()
            test.checkWalmart(database, filter1)
        elif response == "2":
            print("Enter the filter name")
            filter1 = input()
            print("Enter the filter name")
            filter2 = input()
            test.checkWalmart(database, filter1)
            test.checkWalmart(database, filter2)
        elif response == "3":
            print("Enter the filter name")
            filter1 = input()
            print("Enter the filter name")
            filter2 = input()
            print("Enter the filter name")
            filter3 = input()
            test.checkWalmart(database, filter1)
            test.checkWalmart(database, filter2)
            test.checkWalmart(database, filter3)
        elif response == "max":
            for filter_name in test.getFilters():
                test.checkWalmart(database, filter_name)
    elif response=="3":
        test.productOnSale(database)
    elif response=="4":
        print("Enter SKU")
        response = input('SKU: ')
        test.removeSku(response,database)
    elif response=="5":
        print("Updating table now...")
        test.updateTablePrices(database)
    database.close()
# test.checkSale(database)
# test.checkWalmart(database,"TV")
# database.close()
