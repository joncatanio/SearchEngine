import numpy
import math
import searchengine.database.search_engine_db as db

class AllPages:
   def __init__(self, inLinks, numberOfOutLinks):
      self.inLinks = inLinks
      self.numberOfOutLinks = numberOfOutLinks


def pagerank(pages, dampening = .85, epsilon = .000001):

   links = pages.inLinks.keys()
   print('NUM IN:', len(pages.inLinks.keys()))
   print('NUM OUT:', len(pages.numberOfOutLinks.keys()))
   n = len(links)
   linkIndex = {}

   for i, link in enumerate(links):
      linkIndex[link] = i

   p = numpy.matrix(numpy.ones((n,1)))/n

   converganceChange = epsilon
   numIterations = 0


   while converganceChange >= epsilon:

      m = numpy.matrix(numpy.zeros((n,1)))

      danglingProduct = 0
      for i, link in enumerate(links):
         if link not in pages.numberOfOutLinks:
            danglingProduct += p[i]

      for i, link in enumerate(links):

         linkSum = 0
         for inLink in pages.inLinks[link]:
            if inLink in pages.numberOfOutLinks:
               linkSum += p[linkIndex[inLink]]/pages.numberOfOutLinks[inLink]

         sA = dampening * linkSum
         sD = (dampening * danglingProduct) / n
         tE = (1 - dampening) / n
         m[i] = sA + sD + tE

      oldP = p
      p = m / numpy.sum(m)
      absChange = numpy.abs(oldP-p)
      converganceChange = numpy.sum(absChange)
      numIterations += 1
      print (converganceChange)
      print (numIterations)

   print (p)
   rankDict = {}
   for i, link in enumerate(links):
      rankDict[link] = p[i][0,0]

   return rankDict

def main():

	# page rank
	in_links = db.getInlinks()
	out_links = db.getNumOutlinks()

	all_pages = AllPages(in_links, out_links)

	link_page_ranks = pagerank(all_pages)

	# insert page rank data into DB
	db.updatePageRank(link_page_ranks)

if __name__ == "__main__":
	db.init_db()
	main()
