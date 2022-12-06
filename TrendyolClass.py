import requests
from bs4 import BeautifulSoup
import time
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

    def getMainPageJSON(url):
        r = requests.get(url)
        html = BeautifulSoup(r.content, "lxml")
        pageContent = html.p.text
        jsonDataMain = json.loads(pageContent)
        
        return jsonDataMain

    def returnRequestURLofComments(productURL, pageNumber):
        index = productURL.find("?boutiqueId")
        firstNumber = productURL.rfind("-")
        secondNumber = productURL.rfind("=")
        requestURL = "https://public-mdc.trendyol.com/discovery-web-socialgw-service/api/review/" + productURL[firstNumber+1:index] + "?merchantId=" + productURL[secondNumber+1:] + "&storefrontId=1&culture=tr-TR&order=1&searchValue=&onlySellerReviews=false&page=" + str(pageNumber)

        return requestURL

    def DataOfProduct(requestURL):
        req = requests.get(requestURL)
        jsonData = json.loads(req.content)
        
        return jsonData

    def getContentOfComments(js, productURL, input):
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