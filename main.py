# import requests
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
from database import sql
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
    def scrapeProduct(self,url):
        self.driver.get(url)
        main_search_div = self.driver.find_element_by_id("mainSearchContent")
        search_product_result_id = main_search_div.find_element_by_id("searchProductResult")
        elements = search_product_result_id.find_elements_by_xpath("//li[contains(@data-tl-id,'ProductTileGridView')]")
        if elements != NoSuchElementException:
            count = 0
            db = sql()
            for elem in elements:
                url =str(elem.find_element_by_css_selector("a[data-type='itemTitles']").get_attribute("href"))
                location = url.rfind("/")
                sku = url[location+1:len(url)]
                price = self.filterPrice(elem.find_element_by_css_selector("span[class='search-result-productprice gridview enable-2price-2']").text)
                if price != None and not db.exist(sku):
                    db.add(sku,price)
                elif db.exist(sku):
                    print("The product with sku of {} already exists".format(sku))

            db.close()
        else:
            print("No elements found on: ",url)



test = Walmart()
test.scrapeProduct("https://www.walmart.com/browse/electronics/3944?cat_id=3944&facet=pickup_and_delivery%3AFREE+Pickup+Today%7C%7Cretailer%3AWalmart.com&page=1&sort=best_seller")
# test.scrape(2)

