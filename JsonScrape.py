import requests
class jsonLocator():

    def __init__(self,url):
        self.r = requests.get(url)
        self.json_data = self.r.json()
        self.r.close()

    def doesExist(self):
        if self.r.status_code != 200:
            return False
        try:
            if self.json_data['items'] == []:
                return False
            else:
                return True
        except:
            return False

    def getTitle(self):
        title = self.json_data['items'][0]['title']
        title = title.replace('/','')
        if len(title) > 150:
            return title[0:150]
        else:
            return title

    def getAvailability(self):
        if self.json_data['items'][0]['storeFrontBuyingOptions']['available'] == False:
            return 0
        else:
            return 1

    def getIsleLocation(self):
        try:
            isle=self.json_data['items'][0]['storeFrontBuyingOptions']['aisleInfo']['aisle'][0]
            return isle
        except:
            return None

    def getStoreInventory(self):
        return self.json_data['items'][0]['storeFrontBuyingOptions']['availabiltyStatus']

    def getPrice(self):
        try:
            return self.json_data['items'][0]['storeFrontBuyingOptions']['primaryOfferPrice']['amount']
        except:
            return None

    def getUPC(self):
        return self.json_data['items'][0]['properties']['standard_upc']




#test = jsonLocator("https://www.walmart.com/store/electrode/api/search?query=614634449")
# test = jsonLocator("https://www.walmart.com/store/electrode/api/search?query=401199665&stores=869")
#print(len(test.getTitle()))
