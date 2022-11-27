from ArsCommentScraperTrendyolFunctions import getLastCommentDate, writeLastCommentDate, getCommentCountInFile, writeTodayDateToFile, getMainPageJSON, returnRequestURLofComments, DataOfProduct, getContentOfComments, writeCommentsToFile
from configTrendyol import *

if __name__ == "__main__":

  lastCommentDate = getLastCommentDate('lastCommentDateTrendyol.txt')
  commentCountInFile = getCommentCountInFile('Trendyol')
  print(lastCommentDate)
  print("\n")
  print(commentCountInFile)


  for x in range (1, QueryPage):
    URL = f'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q=beyaz+e%C5%9Fya&qt=beyaz+e%C5%9Fya&st=beyaz+e%C5%9Fya&os=1&sst=MOST_RATED&pi={x}&culture=tr-TR&userGenderId=1&pId=0&scoringAlgorithmId=2&categoryRelevancyEnabled=false&isLegalRequirementConfirmed=false&searchStrategyType=DEFAULT&productStampType=TypeA&fixSlotProductAdsIncluded=true&initialSearchText=beyaz+e%C5%9Fya' #&pi=2,3,4... eklenecek

    jsonDataMain = getMainPageJSON(URL)

    for input in jsonDataMain['result']['products']:

      productURL = "https://www.trendyol.com" + input['url']
      requestURL = returnRequestURLofComments(productURL, 0)
      jsonData = DataOfProduct(requestURL)

      if (jsonData['statusCode'] == 200):
        totalPages = jsonData['result']['productReviews']['totalPages'] #147
      else:
        totalPages = 3

      if (jsonData['statusCode'] == 200):
        for js in jsonData['result']['productReviews']['content']:
          if (datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
            commentDic = getContentOfComments(js, productURL, input)
            everyItem.append(commentDic)
          else:
            break

      if totalPages > 100:
        for k in range (1, 100):
          requestURL2 = returnRequestURLofComments(productURL, k)
          jsonData2 = DataOfProduct(requestURL2)

          if (jsonData2['statusCode'] == 200):
            for js in jsonData2['result']['productReviews']['content']:
              if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                commentDic2 = getContentOfComments(js, productURL, input)
                everyItem.append(commentDic2)
              else:
                break
          else:
            continue

      else:
        for k in range (2, totalPages-1):
          requestURL2 = returnRequestURLofComments(productURL, k)
          jsonData2 = DataOfProduct(requestURL2)

          if (jsonData2['statusCode'] == 200):
            for js in jsonData2['result']['productReviews']['content']:
              if(datetime.fromisoformat(js['commentDateISOtype']) > datetime.fromisoformat(lastCommentDate)):
                commentDic2 = getContentOfComments(js, productURL, input)
                everyItem.append(commentDic2)
              else:
                break
          else:
            continue
  
  writeCommentsToFile('Trendyol', everyItem, commentCountInFile)
  writeTodayDateToFile("lastCommentDateTrendyol.txt")