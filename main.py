# import requests
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
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
    def scrapeProduct(self,url,db):
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

                        if price != None and not db.exist(sku):
                            data.append((sku,price))
                        elif db.exist(sku):
                            print("The product with sku of {} already exists".format(sku))
                    except NoSuchElementException:
                        print("{} has problem with finding a[data-type='itemTitles'] or span[class='search-result-productprice gridview enable-2price-2']".format(url))
                return data
            else:
                print("No elements found on: ",url)
        except NoSuchElementException:
            print("Error with {} either mainSearchContent or searchProductResult".format(url))


websites=[]

with open('websites.txt') as read:
    for line in read:
        if line[0] != '#':
            websites.append(line.rstrip('\n'))
test = Walmart()
database = sql()
for link in websites:
    for i in range(1,26):
        html_tag = "?page="+str(i)
        newurl=link+html_tag
        time0=time.time()
        data = test.scrapeProduct(newurl,database)
        database.add(data)
        time1=time.time()
        print(time1-time0)





