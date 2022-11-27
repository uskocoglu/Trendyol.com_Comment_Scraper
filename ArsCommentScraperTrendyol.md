
#  Marketplace web scrapers included in the project
* Trendyol
    *  made by Utku Selim Koçoğlu



## 1. Trendyol Comment Scraper
This project collects user comments for Arçelik products that are present in trendyol.com.
___

## 2. Project Description
This program takes API response page of Arçelik products as input and iterates over all products to get the comment data which consists of product title, comment title, buyer name, date, comment, votes, rating, seller and product URL. After that, this comment data is saved and stored in an Excel file. When the program terminates, the date is stored in a text file and by doing so, next time we run the program, only the comments after that date are collected and appended to the already existing Excel file. 
___

Import the required libraries

```python
pip install requests
pip install beautifulsoup4
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json
from datetime import datetime
``` 
___

Script search for a txt file named **LastCommentDate_trendyol** which has the latest query date. Script stores the latest query date in this txt file when the program terminates and uses this date to retrieve only the most recent data for the next use cases. If the txt file does not exist, it creates the file and assigns a very old date to be able to retrieve the latest comments.

```python
try:
    with open('LastCommentDate_trendyol.txt') as f:
        LastCommentDate = f.read()
    if LastCommentDate == "":  
        f = open("LastCommentDate_trendyol.txt","w+")
        LastCommentDate = "1900-01-01"
        f.write(LastCommentDate)       
    f.close()
except IOError:
    f = open("LastCommentDate_trendyol.txt","w+")
    LastCommentDate = "1900-01-01"
    f.write(LastCommentDate)
    f.close()

``` 
Script also searches for an excel file named **CommentData_trendyol** which has the retrieved data up to the date specified in **LastCommentDate_trendyol.txt**. If the excel file does not exist, it creates an empty excel file.

```python
try:
    with open('CommentData_trendyol.xlsx') as f:
      commentDataFileExist = True
      reader = pd.read_excel(r'CommentData_trendyol.xlsx')
      commentCountinFile = len(reader)       
    f.close()
except IOError:
    commentCountinFile = 0
    pass

``` 


___

This loop generates a unique URL on each iteration that each of them is the API response page of Arçelik products. 

```python
for x in range (1, 21):
  URL = "https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?wb=626&os=1&sk=1&sst=MOST_RATED&pi=" + str(x) + "&culture=tr-TR&userGenderId=1&pId=0&scoringAlgorithmId=2&categoryRelevancyEnabled=false&isLegalRequirementConfirmed=false&searchStrategyType=DEFAULT&productStampType=TypeA" 
  r = requests.get(URL)


  html = BeautifulSoup(r.content, "lxml")
  pageContent = html.p.text
  jsonDataMain = json.loads(pageContent)

``` 

Inside the loop before, there is another for loop. This loop generates a  product URL using its ID and sends a request to the server. For each product that is iterated, the total number of API response pages are found and stored in a variable to be used later. 

```python
for input in jsonDataMain['result']['products']:

    productURL = "https://www.trendyol.com" + input['url']
    index = productURL.find("?boutiqueId")
    firstNumber = productURL.rfind("-")
    secondNumber = productURL.rfind("=")
    requestURL = "https://public-mdc.trendyol.com/discovery-web-socialgw-service/api/review/" + productURL[firstNumber+1:index] + "?merchantId=" + productURL[secondNumber+1:] + "&storefrontId=1&culture=tr-TR&order=1&searchValue=&onlySellerReviews=false&page=0"
    req = requests.get(requestURL)
    jsonData = json.loads(req.content)
    time.sleep(2)
    if (jsonData['statusCode'] == 200):
      totalPages = jsonData['result']['productReviews']['totalPages'] #147
    else:
      totalPages = 3

``` 

After the total pages are found, this script collects the product information data for the 0th API response page. 

```python
if (jsonData['statusCode'] == 200):
      for js in jsonData['result']['productReviews']['content']:
        dic = {}
        if (datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(LastCommentDate)):
          dic['productTitle'] = input['name']
          dic['commentTitle'] = js['commentTitle']
          dic['buyerName'] = js['userFullName']
          dic['date'] = js['commentDateISOtype']
          dic['comment'] = js['comment']
          dic['votesLike'] = js['reviewLikeCount']
          dic['votesDislike'] = "n/a"
          dic['rating'] = js['rate']
          dic['buyerAge'] = "n/a"
          dic['seller'] = js['sellerName']
          dic['verification'] = js['trusted']
          dic['color'] = "n/a"
          dic['buyerLocation'] = "n/a"
          dic['totalRating'] = "n/a"
          dic['productURL'] = productURL
          everyItem.append(dic)
          commentCountinFile=commentCountinFile+1
        else:
          break

``` 

According to the number of total pages, the script acts differently. Even though the total number of API pages is found greater than 100, the maximum amount of API response is 100 on Trendyol website. That is why the loop finishes at 100 if the total pages greater than 100. 

```python
if totalPages > 100:
    for k in range (1, 100):
    requestURL = "https://public-mdc.trendyol.com/discovery-web-socialgw-service/api/review/" + productURL[firstNumber+1:index] + "?merchantId=" + productURL[secondNumber+1:] + "&storefrontId=1&culture=tr-TR&order=1&searchValue=&onlySellerReviews=false&page=" + str(k)
    req2 = requests.get(requestURL)
    jsonData2 = json.loads(req2.content)

    if (jsonData2['statusCode'] == 200):
        for j in jsonData2['result']['productReviews']['content']:
        dic = {}
        if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(LastCommentDate)):
            dic['productTitle'] = input['name']
            dic['commentTitle'] = j['commentTitle']
            dic['buyerName'] = j['userFullName']
            dic['date'] = j['commentDateISOtype']
            dic['comment'] = j['comment']
            dic['votesLike'] = j['reviewLikeCount']
            dic['votesDislike'] = "n/a"
            dic['rating'] = j['rate']
            dic['buyerAge'] = "n/a"
            dic['seller'] = j['sellerName']
            dic['verification'] = j['trusted']
            dic['color'] = "n/a"
            dic['buyerLocation'] = "n/a"
            dic['totalRating'] = "n/a"
            dic['productURL'] = productURL
            everyItem.append(dic)
            commentCountinFile=commentCountinFile+1
        else:
            break
    else:
        continue

else:
    for k in range (2, totalPages-1):
    requestURL = "https://public-mdc.trendyol.com/discovery-web-socialgw-service/api/review/" + productURL[firstNumber+1:index] + "?merchantId=" + productURL[secondNumber+1:] + "&storefrontId=1&culture=tr-TR&order=1&searchValue=&onlySellerReviews=false&page=" + str(k)
    req2 = requests.get(requestURL)
    jsonData2 = json.loads(req2.content)
    #size = jsonData['result']['productReviews']['size'] #30

    if (jsonData2['statusCode'] == 200):
        for j in jsonData2['result']['productReviews']['content']:
        dic = {}
        if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(LastCommentDate)):
            dic['productTitle'] = input['name']
            dic['commentTitle'] = j['commentTitle']
            dic['buyerName'] = j['userFullName']
            dic['date'] = j['commentDateISOtype']
            dic['comment'] = j['comment']
            dic['votesLike'] = j['reviewLikeCount']
            dic['votesDislike'] = "n/a"
            dic['rating'] = j['rate']
            dic['buyerAge'] = "n/a"
            dic['seller'] = j['sellerName']
            dic['verification'] = j['trusted']
            dic['color'] = "n/a"
            dic['buyerLocation'] = "n/a"
            dic['totalRating'] = "n/a"
            dic['productURL'] = productURL
            everyItem.append(dic)
            commentCountinFile=commentCountinFile+1
        else:
            break
    else:
        continue

``` 

A new comment is appended to excel file before moving to next comment


```python
        df1 = pd.DataFrame(everyItem)
        if commentDataFileExist:
            writer = pd.ExcelWriter('CommentData_trendyol.xlsx', engine='openpyxl', mode ='a', if_sheet_exists='overlay')
            df1.to_excel(writer, sheet_name='trendyol', startrow=commentCountinFile, index = False, header= False)
            writer.save()
        else:
            df = pd.DataFrame([['productTitle', 'commentTitle', 'buyerName', 'date', 'comment', 'votesLike', 'votesDislike', 'rating', 'buyerAge', 'seller', 'verification', 'color', 'buyerLocation', 'totalRating', 'productURL']])
            writer = pd.ExcelWriter('CommentData_trendyol.xlsx', engine='openpyxl')
            df.to_excel(writer, sheet_name='trendyol', startrow=0, index = False, header= False)
            df1.to_excel(writer, sheet_name='trendyol', startrow=1, index = False, header= False)
            writer.save()
            commentDataFileExist = True
```
Before terminating, date of the day is written to **LastCommentDate_trendyol.txt**
```python
f = open("LastCommentDate_trendyol.txt","w+")
f.write(str(today))
f.close()
```