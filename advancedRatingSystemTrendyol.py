#from ArsCommentScraperTrendyolFunctions import getLastCommentDate, writeLastCommentDate, getCommentCountInFile, writeTodayDateToFile, getMainPageJSON, returnRequestURLofComments, DataOfProduct, getContentOfComments, writeCommentsToFile
from configTrendyol import *
from crawlersTrendyol import *

if __name__ == "__main__":

  trendyol = Trendyol(everyItem, commentDataFileExist, today, QueryPage)
  trendyol.crawlData()