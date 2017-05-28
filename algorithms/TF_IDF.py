import re, math
# import database as db

# db.getLinks(word)        - The list of all links that contain the given word
# db.getMaxFreq(link)      - The maximum frequency of any word in the given link
# db.getFreq(link, word)   - The freqency of a word in a link
# db.getNumLinks()         - The total number of links
# db.getNumLinks(word)     - The total number of links that contain the given word

# Strip the words out of a string using regex
def wordsFromString(string):
   return re.findall(r'\b(\w+)\b', string)

# Remove words that are too common
def removeStopWords(words):
   return [w for w in words if w not in stopwords.words('english')]

# from nltk.corpus import stopwords
# from nltk.stem.porter import *
# stemmer = PorterStemmer()
# stopwords = ["a", "about", "an", "are", "as", "at", "be", "by", "for", "from", "how", "in", "is", "of", "on", "or", "that", "the", "these", "this", "to", "was", "what", "when", "where", "who", "will", "with"]
# nltk english stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn']
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
   links = set()
   for word in words:
      links = links.union(db.getLinks(word))
   return links

# Caculate the TF-IDF weight for a given link and given word
def tf_idf(words, link):
   maxWordFreq = db.getMaxFreq(link)
   weights = []
   for word in words:
      # Calculate TF
      tf = 0
      if maxWordFreq != 0:
         wordFreq = db.getFreq(link, word)
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
   links = sorted(linkWeights, key=lambda (link, linkWeights): cosineSimilarity(queryWeights, linkWeights), reverse=True)

   return links[:n]

def test():
   query1 = "This is a possible search query"
   query2 = "\"What about this query?\""

   print("Query 1: {0}".format(query1))
   words1 = wordsFromQuery(query1)
   print(words1)

   print("Query 2: {0}".format(query2))
   words2 = wordsFromQuery(query2)
   print(words2)

if __name__ == "__main__":
   test()
