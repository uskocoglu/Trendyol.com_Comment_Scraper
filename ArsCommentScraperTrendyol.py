#from ArsCommentScraperTrendyolFunctions import getLastCommentDate, writeLastCommentDate, getCommentCountInFile, writeTodayDateToFile, getMainPageJSON, returnRequestURLofComments, DataOfProduct, getContentOfComments, writeCommentsToFile
from configTrendyol import *
from TrendyolClass import *

if __name__ == "__main__":

  trendyol = Trendyol(everyItem, commentDataFileExist, today, QueryPage)

  lastCommentDate = trendyol.getLastCommentDate()
  commentCountInFile = trendyol.getCommentCountInFile()

  for x in range (1, trendyol.QueryPage):
    URL = f'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q=beyaz+e%C5%9Fya&qt=beyaz+e%C5%9Fya&st=beyaz+e%C5%9Fya&os=1&sst=MOST_RATED&pi={x}&culture=tr-TR&userGenderId=1&pId=0&scoringAlgorithmId=2&categoryRelevancyEnabled=false&isLegalRequirementConfirmed=false&searchStrategyType=DEFAULT&productStampType=TypeA&fixSlotProductAdsIncluded=true&initialSearchText=beyaz+e%C5%9Fya' #&pi=2,3,4... eklenecek

    jsonDataMain = trendyol.getMainPageJSON(URL)

    for input in jsonDataMain['result']['products']:

      productURL = "https://www.trendyol.com" + input['url']
      requestURL = trendyol.returnRequestURLofComments(productURL, 0)
      jsonData = trendyol.DataOfProduct(requestURL)

      if (jsonData['statusCode'] == 200):
        totalPages = jsonData['result']['productReviews']['totalPages'] #147
      else:
        totalPages = 3

      if (jsonData['statusCode'] == 200):
        for js in jsonData['result']['productReviews']['content']:
          if (datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
            commentDic = trendyol.getContentOfComments(js, productURL, input)
            trendyol.everyItem.append(commentDic)
          else:
            break

      if totalPages > 100:
        for k in range (1, 100):
          requestURL2 = trendyol.returnRequestURLofComments(productURL, k)
          jsonData2 = trendyol.DataOfProduct(requestURL2)

          if (jsonData2['statusCode'] == 200):
            for js in jsonData2['result']['productReviews']['content']:
              if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                commentDic2 = trendyol.getContentOfComments(js, productURL, input)
                trendyol.everyItem.append(commentDic2)
              else:
                break
          else:
            continue

      else:
        for k in range (2, totalPages-1):
          requestURL2 = trendyol.returnRequestURLofComments(productURL, k)
          jsonData2 = trendyol.DataOfProduct(requestURL2)

          if (jsonData2['statusCode'] == 200):
            for js in jsonData2['result']['productReviews']['content']:
              if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                commentDic2 = trendyol.getContentOfComments(js, productURL, input)
                trendyol.everyItem.append(commentDic2)
              else:
                break
          else:
            continue
  
  trendyol.writeCommentsToFile(everyItem, commentCountInFile)
  trendyol.writeTodayDateToFile()