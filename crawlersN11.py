import requests
from bs4 import BeautifulSoup
from datetime import date
import pandas as pd
from config_n11 import *


class N11:

    companyName = "n11"
    file = "lastCommentDateN11.txt"
    
    def __init__(self, URL):
        self.URL = URL
    
    def returnProducts(self):
        r = requests.get(self.URL)
        soup = BeautifulSoup(r.content, "lxml")
        urunler = soup.find_all("li", attrs={"class": "column"})
        return urunler

    def returnProductName(self, product):
        productName = product.a.get("title")
        return productName

    def returnProductLink(self, product):
        productLink = product.a.get("href")
        return productLink

    def getProductID(self, productLink):
        product_r = requests.get(productLink)
        product_soup = BeautifulSoup(product_r.content)
        product_id = product_soup.find("input", attrs={"id": "productId"}).get("value")
        return product_id

    def getFirstCommentPage(self, product_id):
        firstCommentLink = "https://www.n11.com/component/render/productReviews?page=1&" + "productId=" + product_id   #ürünün ilk yorum sayfası
        firstCommentPage = requests.get(firstCommentLink)
        firstCommentPage_soup = BeautifulSoup(firstCommentPage.content)
        return firstCommentPage_soup

    def getPageCount(self, firstCommentPage_soup):
        pageCount = firstCommentPage_soup.find("span", attrs={"class": "pageCount"})
        return pageCount

    def getCommentLinks(self, firstCommentPage_soup, product_id):
        pageCount = firstCommentPage_soup.find("span", attrs={"class": "pageCount"}).text
        yorumLinkleri = []
        for i in range(1, int(pageCount)+1):
            stri = str(i)
            yorumsayfasi = "https://www.n11.com/component/render/productReviews?page=" + stri + "&productId=" + product_id
            yorumLinkleri.append(yorumsayfasi)
        return yorumLinkleri

    def getEveryComments(self, yorumLinkleri, urunAdi):
        everyItem = []
        for yorumlink in yorumLinkleri:
            html = requests.get(yorumlink, )
            yorumlar_soup = BeautifulSoup(html.content)
            yorumlar = yorumlar_soup.find_all("li", attrs={"class": "comment"})
            for yorum in yorumlar:
                dic = {}
                dic['productTitle'] = urunAdi
                title = yorum.find("h5", attrs={"class": "commentTitle"})
                if title is not None:
                    dic['commentTitle'] = yorum.find("h5", attrs={"class": "commentTitle"}).text
                else:
                    dic['commentTitle'] = "n/a"
                dic['buyerName'] = yorum.find("span", attrs={"class": "userName"}).text
                date = yorum.find("span", attrs={"class": "commentDate"})
                if date is not None:
                    dic['date'] = yorum.find("span", attrs={"class": "commentDate"}).text
                else:
                    dic['date'] = "n/a"
                comment = yorum.find("p")
                if comment is not None:
                    dic['comment'] = yorum.find("p").text
                else:
                    dic['comment'] = "n/a"
                votesLike = yorum.find("em")
                if votesLike is not None:
                    dic['votesLike'] = yorum.find("em").text
                else:
                    dic['votesLike'] = "n/a"
                dic['votesDislike'] = "n/a"
                dic['rating'] = yorum.find("div", attrs={"class": "ratingCont"}).span.get("class")
                dic['buyerAge'] = "n/a"
                dic['seller'] = "n/a"
                dic['verification'] = "n/a"
                dic['color'] = "n/a"
                dic['buyerLocation'] = "n/a"
                dic['totalRating'] = "n/a"
                everyItem.append(dic)

        return everyItem


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

    def writeCommentsToFile(self, commentList, commentCountInFile):

        df = pd.DataFrame(commentList)

        with pd.ExcelWriter(f"commentData{self.companyName}.xlsx", engine='openpyxl', mode ='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name=self.companyName, startrow=commentCountInFile, index = False, header= False)
            writer.save()

    def crawlData(self):
        urunler = self.returnProducts()

        lastCommentDate = self.getLastCommentDate()
        commentCountInFile = self.getCommentCountInFile()

        for urun in urunler:
            urunAdi = self.returnProductName(urun)
            urunLink = self.returnproductLink(urun)
            urun_id = self.getProductID(urunLink)
            ilkYorumSayfasi = self.getFirstCommentPage(urun_id)
            pageCount = self.getPageCount(ilkYorumSayfasi)
            if pageCount is not None:
                yorumLinkleri = self.getCommentLinks(ilkYorumSayfasi, urun_id)
                allComments = self.getEveryComments(yorumLinkleri, urunAdi)
            else:
                continue

        self.writeCommentsToFile(allComments, commentCountInFile)
        self.writeTodayDateToFile()