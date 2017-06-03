import searchengine.database.search_engine_db as db
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
   links = db.getLinks(words)
   return links if links else []

# Caculate the TF-IDF weight for a given link and given word
def tf_idf(words, link, numDBLinks):
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
         idf = math.log(numDBLinks / numLinksWithWord)

      # Return TF-IDF
      weights.append(tf * idf)
   return weights

# Calculate the TF-IDF for the search query
def tf_idf_query(words, numDBLinks):
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
         idf = math.log(numDBLinks / numLinksWithWord)

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
   queryMagnitude = magnitude(queryWeights)
   linkMagnitude = magnitude(linkWeights)
   if queryMagnitude == 0 or linkMagnitude == 0:
      return 0
   return dot(queryWeights, linkWeights) / (queryMagnitude * linkMagnitude)

# Find the top n relevant links for a given search query
def findRelevantLinks(query, n):
   words = wordsFromQuery(query.strip().lower())

   # Get the links with the search query terms and sort by cosine similarity
   links = linksForQuery(words)
   if links:
      numDBLinks = db.getNumLinks()
      queryWeights = tf_idf_query(words, numDBLinks)
      linkWeights = [(link, tf_idf(words, link, numDBLinks)) for link in links]
      linkSimilarities = [(link, cosineSimilarity(queryWeights, weights)) for (link, weights) in linkWeights]
      links = sorted(linkSimilarities, key=lambda entry: entry[1], reverse=True)

   return [link[0] for link in links[:n]]

def test():
   db.init_db()
   query1 = "This is a possible search query"
   query2 = "\"What about this query?\""

   # Verify necessary db methods don't crash
   db.getLinks(["test", "words"])
   numDBLinks = db.getNumLinks()
   db.getNumLinks("testing")
   db.getFreq("word", "link.com")
   db.getMaxFreq("link.com")

   print("Query 1: {0}".format(query1))
   words1 = wordsFromQuery(query1)
   print(words1)
   query1Weights = tf_idf_query(words1, numDBLinks)
   print("Query1 Weights: {0}".format(query1Weights))
   links1 = findRelevantLinks(query1, 10)
   print("Links 1: {0}".format(links1))

   print()
   print("Query 2: {0}".format(query2))
   words2 = wordsFromQuery(query2)
   print(words2)
   query2Weights = tf_idf_query(words2, numDBLinks)
   print("Query2 Weights: {0}".format(query2Weights))
   links2 = findRelevantLinks(query2, 10)
   print("Links 2: {0}".format(links2))   

if __name__ == "__main__":
   test()