import sys
sys.path.insert(0, '../database/src')
import search_engine_db as db
import re, math
from nltk.corpus import stopwords

# Strip the words out of a string using regex
def wordsFromString(string):
   return re.findall(r'\b(\w+)\b', string)

# Remove words that are too common
def removeStopWords(words):
   return [w for w in words if w not in stopwords.words('english')]

# from nltk.stem.porter import *
# stemmer = PorterStemmer()
# def stemWords(words):
#     stemmed = []
#     for word in words:
#         stemmed.append(stemmer.stem(word))
#     return stemmed

# Extract all important words from a search query
def wordsFromQuery(query):
   # Get words from query
   words = wordsFromString(query)
   # Remove stopwords
   words = removeStopWords(words)
   # Convert to stems
   # words = stemWords(words)
   return words

# Find all links that contain at least one of the given words
def linksForQuery(words):
   return db.getLinks(words)

# Caculate the TF-IDF weight for a given link and given word
def tf_idf(words, link):
   maxWordFreq = db.getMaxFreq(link)
   weights = []
   for word in words:
      # Calculate TF
      tf = 0
      if maxWordFreq != 0:
         wordFreq = db.getFreq(word, link)
         tf = 0.5 + 0.5 * wordFreq / maxWordFreq

      # Calculate IDF
      idf = 0
      numLinksWithWord = db.getNumLinks(word)
      if numLinksWithWord != 0:
         numLinks = db.getNumLinks()
         idf = math.log(numLinks / numLinksWithWord)

      # Return TF-IDF
      weights.append(tf * idf)
   return weights

# Calculate the TF-IDF for the search query
def tf_idf(words):
   maxWordFreq = max([words.count(w) for w in set(words)])
   weights = []
   for word in words:
      # Calculate TF
      wordFreq = words.count(word)
      tf = 0.5 + 0.5 * wordFreq / maxWordFreq

      # Calculate IDF
      idf = 0
      numLinksWithWord = db.getNumLinks(word)
      if numLinksWithWord != 0:
         numLinks = db.getNumLinks()
         idf = math.log(numLinks / numLinksWithWord)

      # Calculate TF-IDF
      weights.append(tf * idf)
   return weights

# Calculate the dot product between two vectors
def dot(list1, list2):
   if len(list1) != len(list2):
      return 0
   return sum([i*j for (i, j) in zip(list1, list2)])

# Calculate the magnitude of a vector
def magnitude(list1):
   squared = sum([x*x for x in list1])
   return math.sqrt(squared)

# Determine the similarity between two vectors using the angle between them
def cosineSimilarity(queryWeights, linkWeights):
   return dot(queryWeights, linkWeights) / (magnitude(queryWeights) * magnitude(linkWeights))

# Calculate the total weight for a link by combining the TF-IDF weights for each word
def weightForLink(link, words):
   totalWeight = 0
   for word in words:
      totalWeight += tf_idf(link, word)
   return totalWeight / len(words)

# Find the top n relevant links for a given search query
def findRelevantLinks(query, n):
   words = wordsFromQuery(query.strip().lower())

   # Get the links with the search query terms and sort by cosine similarity
   queryWeights = tf_idf(words)
   linkWeights = [(link, tf_idf(words, link)) for link in linksForQuery(words)]
   links = sorted(linkWeights, key=lambda link, linkWeights: cosineSimilarity(queryWeights, linkWeights), reverse=True)

   return links[:n]

def test():
   db.init_db()
   query1 = "This is a possible search query"
   query2 = "\"What about this query?\""

   print("Query 1: {0}".format(query1))
   words1 = wordsFromQuery(query1)
   print(words1)
   # query1Weights = tf_idf(words1)
   # print("Query1 Weights: {0}".format(query1Weights))

   print("Query 2: {0}".format(query2))
   words2 = wordsFromQuery(query2)
   print(words2)
   # query2Weights = tf_idf(words2)
   # print("Query2 Weights: {0}".format(query2Weights))

if __name__ == "__main__":
   test()
