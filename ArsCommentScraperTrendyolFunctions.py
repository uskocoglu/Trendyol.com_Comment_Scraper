import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json
from datetime import date
from configTrendyol import *

def getLastCommentDate(file): 
    lastCommentDate = "1900-01-01"
    try:
        with open(file) as f:
            lastCommentDate = f.read()    
    except IOError:
        writeLastCommentDate(file, lastCommentDate)
    else:
        f.close()
        if lastCommentDate == "":  
            lastCommentDate = "1900-01-01"
            writeLastCommentDate(file, lastCommentDate)
    finally:
        return lastCommentDate

def writeLastCommentDate(file, lastCommentDate): 
    f = open(file,"w+")
    f.write(lastCommentDate)
    f.close()

def getCommentCountInFile(companyName):
    file = f"commentData{companyName}.xlsx"
    try:
        with open(file) as f:
            reader = pd.read_excel(file)
            commentCountInFile = len(reader)       
    except IOError:
        commentCountInFile = 1
        df = pd.DataFrame([['productTitle', 'commentTitle', 'buyerName', 'date', 'comment', 'votesLike', 'votesDislike'
                            , 'rating', 'buyerAge', 'seller', 'verification', 'color', 'buyerLocation', 'totalRating', 'productURL']]                                            )
        writer = pd.ExcelWriter(file, engine='openpyxl')
        df.to_excel(writer, sheet_name=companyName, startrow=0, index = False, header= False)
        writer.save()
    return commentCountInFile

def writeTodayDateToFile(file):
    f = open(file,"w+")
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

    
def writeCommentsToFile(companyName, commentList, commentCountInFile):

    df = pd.DataFrame(commentList)

    with pd.ExcelWriter(f"commentData{companyName}.xlsx", engine='openpyxl', mode ='a', if_sheet_exists='overlay') as writer:
        df.to_excel(writer, sheet_name=companyName, startrow=commentCountInFile, index = False, header= False)
        writer.save()