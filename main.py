# import requests
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
class Walmart:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),options=self.chrome_options)
        #self.driver = webdriver.Chrome("/usr/bin/chromedriver",options = self.chrome_options) This is for Raspberry Pi

    # def createPage(self,url):
    #     html = self.driver.get(url)
    #     return html

    def scrapeProduct(self,url):
        self.driver.get(url)
        main_search_div = self.driver.find_element_by_id("mainSearchContent")
        search_product_result_id = main_search_div.find_element_by_id("searchProductResult")
        elements = search_product_result_id.find_elements_by_xpath("//li[contains(@data-tl-id,'ProductTileGridView')]")
        if elements != NoSuchElementException:
            count = 0
            for elem in elements:
                url =str(elem.find_element_by_css_selector("a[data-type='itemTitles']").get_attribute("href"))
                location = url.rfind("/")
                sku = url[location+1:len(url)]
                count+=1
                print(sku)
            print(count)
        else:
            print("No elements found on: ",url)



test = Walmart()
test.scrapeProduct("https://www.walmart.com/browse/electronics/3944?cat_id=3944&facet=pickup_and_delivery%3AFREE+Pickup+Today%7C%7Cretailer%3AWalmart.com&page=1&sort=best_seller")
# test.scrape(2)

