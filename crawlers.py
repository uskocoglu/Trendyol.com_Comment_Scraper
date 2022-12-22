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

class Base():   
    def __init__(self):   
        Base.getCommentCountInFile(self.companyName)
        Base.getProxies(self)
        self.session = requests.Session()

    def getCommentCountInFile(companyName):
        file = f"commentData{companyName}.xlsx"
        try:
            with open(file) as f:
                reader = pd.read_excel(file)
                commentCountInFile = len(reader)      
        except IOError:
            df = pd.DataFrame([['productTitle', 'commentTitle', 'buyerName', 'date', 'comment', 'votesLike', 'votesDislike'
                                , 'rating', 'buyerAge', 'seller', 'verification', 'color', 'buyerLocation', 'totalRating', 'productURL']]                                            )
            with pd.ExcelWriter(file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=companyName, startrow=0, index = False, header= False)
                commentCountInFile = 0
        return commentCountInFile

    def getProxies(self):     
        proxyURL = "https://github.com/clarketm/proxy-list/blob/master/proxy-list-raw.txt"
        response = requests.get(proxyURL) 
        soup = BeautifulSoup(response.content, "html.parser").find_all("td",{"class":"blob-code blob-code-inner js-file-line"})
        self.proxies = [proxy.text for proxy in soup]

    def getRandomProxy(self):
        randomProxy = choice(self.proxies)
        return {
            "http" : randomProxy,
            "https" : randomProxy,
        }

    def getWorkingProxy(self, URL):
        for i in range(len(self.proxies)):
            proxy = Base.getRandomProxy(self)
            print(f"Candidate Proxy {proxy}")
            try:
                response = self.session.get(URL, proxies=proxy, headers=headers, timeout=3) 
            except:
                pass
            else:
                if response.status_code == 200: 
                    self.session.proxies.update(proxy)
                    print(f"Proxy {self.session.proxies} used")       
                    return response 

    def getURL(self, URL): 
        try:
            response = self.session.get(URL, headers=headers, timeout=8)
        except:
            print(URL)
            response = Base.getWorkingProxy(self, URL)
        else:
            if response.status_code != 200:  
                print(URL)
                print(response.status_code)
                response = Base.getWorkingProxy(self, URL)
        finally:
            return response

    def getSoup(self, link):
        page = Base.getURL(self, link)
        return BeautifulSoup(page.content, "html.parser")

    def writeCommentsToFile(self, df):
        with st.empty():
            st.write(df) 
        with pd.ExcelWriter(f"commentData{self.companyName}.xlsx", engine='openpyxl', mode ='a', if_sheet_exists='overlay') as writer:  
            df.to_excel(writer, sheet_name=self.companyName, startrow=Base.getCommentCountInFile(self.companyName)+1, index = False, header= False)
  
    def getLastCommentDate(self): 
        file = f"lastCommentDate{self.companyName}.txt"
        lastCommentDate = "1900-01-01"
        try:
            with open(file) as f:
                lastCommentDate = f.read()    
        except IOError:
            Base.writeLastCommentDate(file, lastCommentDate)
        else:
            # f.close()
            if lastCommentDate == "":  
                lastCommentDate = "1900-01-01"
                Base.writeLastCommentDate(file, lastCommentDate)
        finally:
            return lastCommentDate

    def writeLastCommentDate(file, lastCommentDate): 
        f = open(file,"w+")
        f.write(lastCommentDate)
        f.close()

    def writeTodayDateToFile(self):
        file = f"lastCommentDate{self.companyName}.txt"
        f = open(file,"w+")
        today = date.today()
        f.write(str(today))
        f.close()

class HepsiBurada(Base):   
    def __init__(self):
        self.companyName = "HepsiBurada"
        Base.__init__(self)

    def getJson(self, link):
        return json.loads(Base.getSoup(self, link).text)

    def crawlData(self):
        commentList = []
        count = 0   
        lastCommentDate = Base.getLastCommentDate(self)

        products = HepsiBurada.getJson(self, f"{hepsiBuradaURL1}&page=1")  
        pageSize = products.get('pageSize')
        totalProductCount = products.get('totalProductCount')
        productCountInPage = pageSize if totalProductCount > pageSize else totalProductCount
        totalPageCount =  ceil(totalProductCount / productCountInPage)

        for i in range(totalPageCount):
            page = i + 2

            for product in range(productCountInPage):
                productInProducts = products.get('products')[product]
                totalCommentCount =  productInProducts.get('customerReviewCount')
                totalRating = productInProducts.get('customerReviewRating')
                variantList = productInProducts.get('variantList')

                for i in range(len(variantList)):
                    variantListX = variantList[i]
                    productSKU = variantListX.get('sku')

                    variantListProperties = variantListX.get('properties')
                    color = variantListProperties.get('Renk', NE)
                    if color != NE:
                        color = color.get('displayValue')
        
                    for commentCount in range(ceil(totalCommentCount/10)):
                        productPage = HepsiBurada.getJson(self, f"{hepsiBuradaURL2}{productSKU}&from={str(commentCount*10)}&size=10&sortField=createdAt")

                        currentItemCount = productPage.get('currentItemCount')
                        if currentItemCount != 0:
                            for i in range(currentItemCount):
                                productData = productPage.get('data').get('approvedUserContent').get('approvedUserContentList')[i]
                                
                                commentDate = productData.get('createdAt')[0:10]
                                print("CommentDate = ", commentDate)
                                print("LastCommentDate = ", lastCommentDate) 
                                if (lastCommentDate >= commentDate):
                                    print("No New Comment\n")
                                    break
                                print("New Comment Taken")
                                            
                                commentList.append(HepsiBurada.getProductProperties(productData, commentDate, color, totalRating))
                                if count == 500:                      
                                    Base.writeCommentsToFile(self, pd.DataFrame(commentList))
                                    count = 0
                                    commentList = []
                                else:
                                    count += 1

            products = HepsiBurada.getJson(self, f"{hepsiBuradaURL1}&page={str(page)}")
            totalProductCount -= productCountInPage
            pageSize = products.get('pageSize')
            productCountInPage = pageSize if totalProductCount > pageSize else totalProductCount

        Base.writeCommentsToFile(self, pd.DataFrame(commentList))
        Base.writeTodayDateToFile(self)

    def getProductProperties(productData, commentDate, color, totalRating):
        today = date.today()

        dic = {}
        product = productData.get('product')
        customer = productData.get('customer')

        dic['productTitle'] = product.get('name')
        dic['commentTitle'] = NA
        dic['buyerName'] = f"{customer.get('name')} {customer.get('surname')}"
        dic['date'] = commentDate
        dic['comment'] = productData.get('review').get('content') if productData.get('contentType') == 1 else NE

        reactions = productData.get('reactions')
        if reactions == None:
            dic['votesLike'] = NE
            dic['votesDislike'] = NE
        else:
            dic['votesLike'] = reactions.get('clap', 0)
            dic['votesDislike'] = reactions.get('thumbsdown', 0)
        
        dic['rating'] = productData.get('star')
        dic['buyerAge'] = NE if customer.get('birthDate') == None else today.year-int(customer.get('birthDate')[0:4])

        order = productData.get('order')
        dic['seller'] = NE if order == None else order.get('merchantName')
        dic['verification'] = productData.get('isPurchaseVerified')
        dic['color'] = color
        dic['buyerLocation'] = NE if order == None else order.get('shippingAddressCity')
        dic['totalRating'] = totalRating
        dic['productURL'] = product.get('url') 

        print("\n",dic,"\n")
        return dic
    
class Amazon(Base):   
    def __init__(self):
        self.companyName = "Amazon"
        Base.__init__(self)

    def crawlData(self):
        commentList = []
        count = 0 

        lastCommentDate = Base.getLastCommentDate(self)
        mainNextPageExist = True
        mainPageCount = 1

        while (mainNextPageExist):
            page = Base.getSoup(self, f"{amazonURL1}&page={str(mainPageCount)}")
            products = Amazon.findAllSoup(page, "a", "class", "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")

            for link in products:
                initialProductPage = Base.getSoup(self, f"https://www.amazon.com.tr/{link['href']}")
                viewAllCommentsProductLink = Amazon.getAttributeNoText(initialProductPage, "a", "class", "a-link-emphasis a-text-bold")
            
                if (viewAllCommentsProductLink) != NE:
                    allCommentsLink = f"https://www.amazon.com.tr/{viewAllCommentsProductLink['href']}&sortBy=recent"
                    isNextButtonNotAppeared = True
                    pageId = 1

                    while(isNextButtonNotAppeared):                   
                        nextPageLink = f"{allCommentsLink}&pageNumber={str(pageId)}"
                        singleProductPage = Base.getSoup(self, nextPageLink)
                    
                        totalRating = Amazon.findSoupText(singleProductPage, "span", "class", "a-size-medium a-color-base")
                        productTitle = Amazon.findSoupText(singleProductPage, "a", "data-hook", "product-link")
                        comments = Amazon.findAllSoup(singleProductPage, "div", "class", "a-section celwidget")

                        for comment in comments:                      
                            commentDate = Amazon.findCommentDate(Amazon.getAttribute(comment, "span", "data-hook", "review-date"))
                            print("CommentDate = ", commentDate)
                            print("LastCommentDate = ", lastCommentDate)                 
                            if (lastCommentDate >= commentDate):
                                print("No New Comment\n")
                                break
                            print("New Comment Taken")

                            commentList.append(Amazon.getProductProperties(productTitle, comment, totalRating, nextPageLink))
                            if count == 500:                         
                                Base.writeCommentsToFile(self, pd.DataFrame(commentList))
                                count = 0
                                commentList = []
                            else:
                                count += 1
        
                        if(Amazon.findSoup(singleProductPage, "div", "id","cm_cr-pagination_bar")):
                            if(Amazon.findSoup(singleProductPage, "li", "class", "a-disabled a-last")):
                                isNextButtonNotAppeared = False           
                            else:
                                pageId = pageId + 1
                        else:
                            isNextButtonNotAppeared = False 
                else:
                    print("No Comment\n")

            if (Amazon.findSoup(page, "span", "class", "s-pagination-item s-pagination-next s-pagination-disabled")):
                mainNextPageExist = False
            else:
                mainPageCount = mainPageCount + 1

        Base.writeCommentsToFile(self, pd.DataFrame(commentList))
        Base.writeTodayDateToFile(self)

    def getProductProperties(productTitle, comment, totalRating, nextPageLink):
        dic = {}
        dic['productTitle'] = productTitle
        dic['commentTitle'] = Amazon.getAttributeWithSecondFind(comment, "a", "class", "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold")
        dic['buyerName'] = Amazon.getAttribute(comment, "span", "class", "a-profile-name")
        dic['date'] = Amazon.getAttribute(comment, "span", "data-hook", "review-date")
        dic['comment'] = Amazon.getAttributeWithSecondFind(comment, "span", "class", "a-size-base review-text review-text-content")
        dic['votesLike'] = Amazon.getAttribute(comment, "span", "class", "a-size-base a-color-tertiary cr-vote-text")
        dic['votesDislike'] = NA
        dic['rating'] = Amazon.getAttribute(comment, "span", "class", "a-icon-alt")
        dic['buyerAge'] = NA
        dic['seller'] = NA
        dic['verfication'] = Amazon.getAttribute(comment, "span", "class", "a-size-mini a-color-state a-text-bold")
        dic['color'] = Amazon.getAttributeWithText(comment, "a", "class", "a-size-mini a-link-normal a-color-secondary")
        dic['buyerLocation'] = NA
        dic['totalRating'] = totalRating
        dic['productURL'] = nextPageLink 

        print("\n",dic,"\n")
        return dic

    def getAttribute(comment, tag, id, attr):
        commentFound = comment.find(tag, attrs={id:attr})
        if (commentFound):
            return commentFound.text
        else:
            return NE

    def getAttributeWithSecondFind(comment, tag, id, attr):
        commentFound = comment.find(tag, attrs={id:attr})
        if (commentFound):
            commentFound = commentFound.find("span")
            if (commentFound):
                return commentFound.text
            else:
                return NE
        else:
            return NE

    def getAttributeWithText(comment, tag, id, attr):
        commentFound = comment.find(tag, attrs={id:attr})
        if (commentFound):
            return commentFound.text[6:]
        else:
            return NE

    def getAttributeNoText(comment, tag, id, attr):
        commentFound = comment.find(tag, attrs={id:attr})
        if (commentFound):
            return commentFound
        else:
            return NE

    def findAllSoup(soup, tag, id, attr):
        return soup.find_all(tag, attrs={id:attr})

    def findSoup(soup, tag, id, attr):
        return soup.find(tag, attrs={id:attr})

    def findSoupText(soup, tag, id, attr):
        soup = soup.find(tag, attrs={id:attr})
        if (soup.text):
            return soup.text
        else:
            return NE

    def findCommentDate(date):
        print(date)
        if date != NE:
            dateList = date.split()
            if (dateList[0].isnumeric()):
                i = 0
            else:
                i = 1
            day = dateList[i]
            if (len(day) == 1):
                day = f"0{day}"
            return f"{dateList[i+2]}-{months.get(dateList[i+1], '00')}-{day}"
        else:
            return "1900-01-01"

class N11(Base):
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
                allComments = self.getEveryComments(yorumLinkleri, urunAdi, urunLink)
                df = pd.DataFrame(allComments)
                print(df)
                Base.writeCommentsToFile(self, df)
            else:
                continue

        Base.writeTodayDateToFile(self)

    def returnProducts(self):
        soup = Base.getSoup(self, n11URL)
        urunler = soup.find_all("li", attrs={"class": "column"})
        return urunler

    def returnProductName(self, product):
        productName = product.a.get("title")
        return productName

    def returnProductLink(self, product):
        productLink = product.a.get("href")
        return productLink

    def getProductID(self, productLink):
        product_soup = Base.getSoup(self, productLink)
        product_id = product_soup.find("input", attrs={"id": "productId"}).get("value")
        return product_id

    def getFirstCommentPage(self, product_id):
        firstCommentLink = "https://www.n11.com/component/render/productReviews?page=1&" + "productId=" + product_id   #ürünün ilk yorum sayfası
        firstCommentPage_soup =Base.getSoup(self, firstCommentLink)
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

    def getEveryComments(self, yorumLinkleri, urunAdi, urunLink):
        everyItem = []
        for yorumlink in yorumLinkleri:
            yorumlar_soup = Base.getSoup(self, yorumlink)
            yorumlar = yorumlar_soup.find_all("li", attrs={"class": "comment"})
            for yorum in yorumlar:
                dic = {}
                dic['productTitle'] = urunAdi
                title = yorum.find("h5", attrs={"class": "commentTitle"})
                if title is not None:
                    dic['commentTitle'] = yorum.find("h5", attrs={"class": "commentTitle"}).text
                else:
                    dic['commentTitle'] = NE
                dic['buyerName'] = yorum.find("span", attrs={"class": "userName"}).text
                date = yorum.find("span", attrs={"class": "commentDate"})
                if date is not None:
                    dic['date'] = yorum.find("span", attrs={"class": "commentDate"}).text
                else:
                    dic['date'] = NE
                comment = yorum.find("p")
                if comment is not None:
                    dic['comment'] = yorum.find("p").text
                else:
                    dic['comment'] = NE
                votesLike = yorum.find("em")
                if votesLike is not None:
                    dic['votesLike'] = yorum.find("em").text
                else:
                    dic['votesLike'] = NE
                dic['votesDislike'] = NA
                dic['rating'] = yorum.find("div", attrs={"class": "ratingCont"}).span.get("class")
                dic['buyerAge'] = NA
                dic['seller'] = NA
                dic['verification'] = NA
                dic['color'] = NA
                dic['buyerLocation'] = NA
                dic['totalRating'] = NA
                dic['productURL'] = urunLink 
                everyItem.append(dic)

        return everyItem

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

    def getMainPageJSON(self, url):
        html = Base.getSoup(self, url)
        # pageContent = html.p.text
        pageContent = html.text
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
        dic['votesDislike'] = NA
        dic['rating'] = js['rate']
        dic['buyerAge'] = NA
        dic['seller'] = js['sellerName']
        dic['verification'] = js['trusted']
        dic['color'] = NA
        dic['buyerLocation'] = NA
        dic['totalRating'] = NA
        dic['productURL'] = productURL

        return dic