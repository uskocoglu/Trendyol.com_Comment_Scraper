
#  Marketplace web scrapers included in the project
* Trendyol
* N11
    *  made by Utku Selim Koçoğlu
* Amazon
* Hepsiburada
    * made by Ahmet Ali Sancaktaroğlu





## 1. Websites Comment Scraper
This project collects user comments for Arçelik products that are present in trendyol.com, n11.com, amazon.com, and hepsiburada.com.
___

## 2. Project Description

### 2.1 The Base Class
The base class includes all the common and necessary functions that the subclasses need. 
___

Import the required libraries

```python
from bs4 import BeautifulSoup
import requests
from random import choice
import pandas as pd
import json
from datetime import date
from datetime import datetime
from math import ceil
from time  import sleep
from config import *
import streamlit as st
``` 
___


In the constructor, firstly the method **getCommentCountInFile** is called. This method counts the total number of lines that are already filled with data in the given company's excel file. Since the program is designed to scrap data and save them in a dataframe, this total number is significant in terms of appending new comments to the existing dataframe. Following this, **getProxies** method is called in order not to be banned from the websites using proxies. And lastly, the requests library is used to initiate a session to send HTTP requests to websites. 

```python
class Base():   
    def __init__(self):   
        Base.getCommentCountInFile(self.companyName)
        Base.getProxies(self)
        self.session = requests.Session()

``` 



___

### 2.2 N11 Class
This class is a child class of the Base class. It basically collects user comments from the products that are displayed in n11.com. 

```python
def __init__(self):
        self.companyName = "N11"
        Base.__init__(self)

    def crawlData(self):
        urunler = self.returnProducts()
        lastCommentDate = Base.getLastCommentDate(self)
           
        for urun in urunler:
            urunAdi = self.returnProductName(urun)
            urunLink = self.returnProductLink(urun)
            urun_id = self.getProductID(urunLink)
            ilkYorumSayfasi = self.getFirstCommentPage(urun_id)
            pageCount = self.getPageCount(ilkYorumSayfasi)

            if pageCount is not None:
                yorumLinkleri = self.getCommentLinks(ilkYorumSayfasi, urun_id)
                allComments = self.getEveryComments(yorumLinkleri, urunAdi, urunLink, lastCommentDate)
                df = pd.DataFrame(allComments)
                print(df)
                Base.writeCommentsToFile(self, df)
            else:
                continue

        Base.writeTodayDateToFile(self)

``` 
### 2.3 Trendyol Class
Trendyol class is a subclass of the Base class. It includes functions to get user comments from the products that are displayed in trendyol.com 

```python
class Trendyol(Base):
    def __init__(self):
        self.companyName = "Trendyol"
        self.QueryPage = QueryPage
        Base.__init__(self)

    def crawlData(self):
            lastCommentDate = Base.getLastCommentDate(self)

            for x in range (1, self.QueryPage):
                URL = f'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q=beyaz+e%C5%9Fya&qt=beyaz+e%C5%9Fya&st=beyaz+e%C5%9Fya&os=1&sst=MOST_RATED&pi={x}&culture=tr-TR&userGenderId=1&pId=0&scoringAlgorithmId=2&categoryRelevancyEnabled=false&isLegalRequirementConfirmed=false&searchStrategyType=DEFAULT&productStampType=TypeA&fixSlotProductAdsIncluded=true&initialSearchText=beyaz+e%C5%9Fya'

                jsonDataMain = self.getMainPageJSON(URL)
                
                for input in jsonDataMain['result']['products']:
                    self.everyItem = []

                    productURL = "https://www.trendyol.com" + input['url']
                    requestURL = self.returnRequestURLofComments(productURL, 0)
                    jsonData = self.DataOfProduct(requestURL)

                    if (jsonData['statusCode'] == 200):
                        totalPages = jsonData['result']['productReviews']['totalPages'] #147
                    else:
                        totalPages = 3

                    if (jsonData['statusCode'] == 200):
                        for js in jsonData['result']['productReviews']['content']:
                            if (datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                                commentDic = self.getContentOfComments(js, productURL, input)
                                self.everyItem.append(commentDic)
                            else:
                                break

                    if totalPages > 100:
                        for k in range (1, 100):
                            requestURL2 = self.returnRequestURLofComments(productURL, k)
                            jsonData2 = self.DataOfProduct(requestURL2)

                            if (jsonData2['statusCode'] == 200):
                                for js in jsonData2['result']['productReviews']['content']:
                                    if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                                        commentDic2 = self.getContentOfComments(js, productURL, input)
                                        self.everyItem.append(commentDic2)
                                    else:
                                        break
                            else:
                                continue
                    else:
                        for k in range (2, totalPages-1):
                            requestURL2 = self.returnRequestURLofComments(productURL, k)
                            jsonData2 = self.DataOfProduct(requestURL2)

                            if (jsonData2['statusCode'] == 200):
                                for js in jsonData2['result']['productReviews']['content']:
                                    if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                                        commentDic2 = self.getContentOfComments(js, productURL, input)
                                        self.everyItem.append(commentDic2)
                                    else:
                                        break
                            else:
                                continue        
                    
                    df = pd.DataFrame(self.everyItem)
                    print(df)
                    Base.writeCommentsToFile(self, df)
            Base.writeTodayDateToFile(self)

``` 





