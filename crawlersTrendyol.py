import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import date
from configTrendyol import *

class Trendyol:

    companyName = "Trendyol"
    file = "lastCommentDateTrendyol.txt"

    def __init__(self, everyItem, commentDataFileExist, today, QueryPage):
        self.everyItem = everyItem
        self.commentDataFileExist = commentDataFileExist
        self.today = today
        self.QueryPage = QueryPage

    def writeLastCommentDate(self, lastCommentDate): 
        f = open(self.file,"w+")
        f.write(lastCommentDate)
        f.close()
        
    def getLastCommentDate(self): 
        lastCommentDate = "1900-01-01"
        try:
            with open(self.file) as f:
                lastCommentDate = f.read()    
        except IOError:
            self.writeLastCommentDate(lastCommentDate)
        else:
            f.close()
            if lastCommentDate == "":  
                lastCommentDate = "1900-01-01"
                self.writeLastCommentDate(lastCommentDate)
        finally:
            return lastCommentDate
    
    def getCommentCountInFile(self):
        file = f"commentData{self.companyName}.xlsx"
        try:
            with open(file) as f:
                reader = pd.read_excel(file)
                commentCountInFile = len(reader)       
        except IOError:
            commentCountInFile = 1
            df = pd.DataFrame([['productTitle', 'commentTitle', 'buyerName', 'date', 'comment', 'votesLike', 'votesDislike'
                                , 'rating', 'buyerAge', 'seller', 'verification', 'color', 'buyerLocation', 'totalRating', 'productURL']])
            writer = pd.ExcelWriter(file, engine='openpyxl')
            df.to_excel(writer, sheet_name=self.companyName, startrow=0, index = False, header= False)
            writer.save()
        return commentCountInFile

    def writeTodayDateToFile(self):
        f = open(self.file,"w+")
        today = date.today()
        f.write(str(today))
        f.close()

    def getMainPageJSON(self, url):
        r = requests.get(url)
        html = BeautifulSoup(r.content, "lxml")
        pageContent = html.p.text
        jsonDataMain = json.loads(pageContent)
        
        return jsonDataMain

    def returnRequestURLofComments(self, productURL, pageNumber):
        index = productURL.find("?boutiqueId")
        firstNumber = productURL.rfind("-")
        secondNumber = productURL.rfind("=")
        requestURL = "https://public-mdc.trendyol.com/discovery-web-socialgw-service/api/review/" + productURL[firstNumber+1:index] + "?merchantId=" + productURL[secondNumber+1:] + "&storefrontId=1&culture=tr-TR&order=1&searchValue=&onlySellerReviews=false&page=" + str(pageNumber)

        return requestURL

    def DataOfProduct(self, requestURL):
        req = requests.get(requestURL)
        jsonData = json.loads(req.content)
        
        return jsonData

    def getContentOfComments(self, js, productURL, input):
        dic = {}
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

        return dic
    

    def writeCommentsToFile(self, commentList, commentCountInFile):

        df = pd.DataFrame(commentList)

        with pd.ExcelWriter(f"commentData{self.companyName}.xlsx", engine='openpyxl', mode ='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name=self.companyName, startrow=commentCountInFile, index = False, header= False)
            writer.save()

    def crawlData(self):
        lastCommentDate = self.getLastCommentDate()
        commentCountInFile = self.getCommentCountInFile()

        for x in range (1, self.QueryPage):
            URL = f'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q=beyaz+e%C5%9Fya&qt=beyaz+e%C5%9Fya&st=beyaz+e%C5%9Fya&os=1&sst=MOST_RATED&pi={x}&culture=tr-TR&userGenderId=1&pId=0&scoringAlgorithmId=2&categoryRelevancyEnabled=false&isLegalRequirementConfirmed=false&searchStrategyType=DEFAULT&productStampType=TypeA&fixSlotProductAdsIncluded=true&initialSearchText=beyaz+e%C5%9Fya'

            jsonDataMain = self.getMainPageJSON(URL)

            for input in jsonDataMain['result']['products']:

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
        self.writeCommentsToFile(everyItem, commentCountInFile)
        self.writeTodayDateToFile()