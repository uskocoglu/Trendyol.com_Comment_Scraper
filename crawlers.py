from bs4 import BeautifulSoup
import requests
from random import choice
import pandas as pd
import json
from datetime import date
from math import ceil
from time  import sleep
from config import *

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
