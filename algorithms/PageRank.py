import numpy
import math



class allPages:
   def __init__(self):
      self.inLinks = {}
      self.numberOfOutLinks = {}
      self.danglingPages = []
      
   def addPage(self, pageLink, inLinks, numberOfOutLinks):
      self.inLinks[pageLink] = inLinks
      self.numberOfOutLinks[pageLink] = numberOfOutLinks;
      if (numberOfOutLinks == 0):
         self.danglingPages.append(pageLink)
         
         

def pagerank(pages, dampening = .85, epsilon = .000001):

   links = pages.inLinks.keys()
   n = len(links)
   
   p = numpy.matrix(numpy.ones((n,1)))/n
   
   links = pages.inLinks.keys()
   
   converganceChange = 0
   
   while converganceChange > e:
      
      m = numpy.matrix(numpy.zeros((n,1)))
      danglingProduct = sum([p[i] for i in g.dangling_pages.keys()])
      for i, link in enumerate(links):
         linkSum = 0
         for j, inlink in enumerate(pages.inLinks[link]):
            linkSum += p[j]/g.number_out_links[inLink]
         sA = dampening * linkSum
         sD = (dampening * danglingProduct) / n
         tE = (1 - dampening) / n
         m[i] = sA + sD + tE
         
      oldP = p
      p = m / numpy.sum(m)
      absChange = numpy.abs(oldP-p)
      converganceChange = numpy.sum(absChange)
      
   return p
      
         
   
   

