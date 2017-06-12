import searchengine.database.search_engine_db as db
import re, math, cProfile
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
# {link: (PageRank score, [words])}
def linksForQuery(words):
   links = {}
   for word in set(words):
      for link, PRWeight in db.getLinks([word]):
         if link in links:
            links[link] = (links[link][0], links[link][1] + [word])
         else:
            links[link] = (PRWeight, [word])
   return links

def calculateTFIDF(freq, maxFreq, numLinksWithTerm, numLinksTotal):
   # Calculate TF
   tf = 0
   if maxFreq != 0:
      tf = 0.5 + 0.5 * freq / maxFreq

   # Calculate IDF
   idf = 0
   if numLinksWithTerm != 0:
      idf = math.log(numLinksTotal / numLinksWithTerm)

   # Return TF-IDF
   return tf * idf

def tfidfLinkPhrase(words, thisLink, linkDict, numLinksTotal, wordFreqs, maxWordFreq):
   # Find the number of links that contain all the words in the phrase
   # TODO: this can be optimized by pulling it out of this method and calculating it fewer times
   numLinksWithPhrase = 0
   for link in linkDict:
      linkContainsPhrase = True
      for word in set(words):
         pageRankWeight, linkWords = linkDict[link]
         # If a phrase word is not in the link, break
         if not linkWords or word not in linkWords:
            linkContainsPhrase = False
            break
      # If the link contains all phrase words, then increment counter
      if linkContainsPhrase:
         numLinksWithPhrase += 1

   # Find the frequency of the phrase in this link (min freq of any word in the phrase)
   phraseFreq = None
   for word in words:
      pageRankWeight, linkWords = linkDict[thisLink]
      # If a phrase word is not in the link, break
      if word not in linkWords or word not in wordFreqs:
         phraseFreq = 0
         break
      # Otherwise check if the word frequency is less than the min so far
      else:
         if not phraseFreq:
            phraseFreq = wordFreqs[word]
         else:
            if wordFreqs[word] < phraseFreq:
               phraseFreq = wordFreqs[word]

   # Return TF-IDF
   return calculateTFIDF(phraseFreq, maxWordFreq, numLinksWithPhrase, numLinksTotal)

def tfidfQueryPhrase(queryWords, phraseWords, linkDict, numLinksTotal, maxWordFreq):
   # Find the number of links that contain all the words in the phrase
   numLinksWithPhrase = 0
   for link in linkDict:
      linkContainsPhrase = True
      for word in set(phraseWords):
         pageRankWeight, linkWords = linkDict[link]
         # If a phrase word is not in the link, break
         if not linkWords or word not in linkWords:
            linkContainsPhrase = False
            break
      # If the link contains all phrase words, then increment counter
      if linkContainsPhrase:
         numLinksWithPhrase += 1

   # Find the frequency of the phrase in this link (min freq of any word in the phrase)
   phraseFreq = min([queryWords.count(w) for w in set(phraseWords)])

   # Return TF-IDF
   return calculateTFIDF(phraseFreq, maxWordFreq, numLinksWithPhrase, numLinksTotal)

# Caculate the TF-IDF weight for a given link and given word
def tfidfLink(words, link, linkDict, numLinksPerWord, numLinksTotal, wordFreqs, maxWordFreq, usePhraseSearch):
   weights = []

   # Calculate the TF-IDF weight for each word in the search query
   for word in words:
      # Calculate TF
      tf = 0
      if maxWordFreq != 0:
         wordFreq = wordFreqs[word] if word in wordFreqs else 0
         tf = 0.5 + 0.5 * wordFreq / maxWordFreq

      # Calculate IDF
      idf = 0
      if word in numLinksPerWord and numLinksPerWord[word] != 0:
         idf = math.log(numLinksTotal / numLinksPerWord[word])

      # Return TF-IDF
      tfidf = tf * idf
      weights.append(tfidf)

   # If there were multiple words in the query and usePhraseSearch is enabled,
   # calculate an additional weight for each sequential phrase of 2+ words
   if usePhraseSearch and len(words) > 1:
      weights.append(tfidfLinkPhrase(words, link, linkDict, numLinksTotal, wordFreqs, maxWordFreq))
   
   return weights

# Calculate the TF-IDF for the search query
def tfidfQuery(words, linkDict, numLinksTotal, numLinksPerWord, usePhraseSearch):
   wordFreqs = {w:words.count(w) for w in set(words)}
   maxWordFreq = max(wordFreqs.values())
   weights = []

   # Calculate the TF-IDF weight for each word in the search query
   for word in words:
      # Calculate TF
      tf = 0.5 + 0.5 * wordFreqs[word] / maxWordFreq

      # Calculate IDF
      idf = 0
      if word in numLinksPerWord and numLinksPerWord[word] != 0:
         idf = math.log(numLinksTotal / numLinksPerWord[word])

      # Calculate TF-IDF
      weights.append(tf * idf)

   # If there were multiple words in the query and usePhraseSearch is enabled,
   # calculate an additional weight for each sequential phrase of 2+ words
   if usePhraseSearch and len(words) > 1:
      weights.append(tfidfQueryPhrase(words, words, linkDict, numLinksTotal, maxWordFreq))
   
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

# Determine the similarity between two vectors using the euclidean distance between them
def euclideanDistance(queryWeights, linkWeights):
   sumsquared = sum([pow(queryWeights[i] - linkWeights[i], 2) for i in range(len(queryWeights))])
   return math.sqrt(sumsquared)

def harmonicMean(cosSim, pageRank):
   return 2 * (cosSim * pageRank) / (cosSim + pageRank)

# Perform TF-IDF and return the link weights and the query weights
def tfidf(words, linkDict, usePhraseSearch):
   links = list(linkDict.keys())

   # Get the necessary values for TF-IDF from the DB
   numLinksTotal = db.getNumLinks()
   numLinksPerWord = db.getNumLinks(set(words))
   wordFreqPerLink = db.getFreq(list(set(words)), links)
   maxWordFreqPerLink = db.getMaxFreq(links) # TODO: This info should maybe be extracted from wordFreqPerLink

   # Perform TF-IDF to get the weights for each link
   queryWeights = tfidfQuery(words, linkDict, numLinksTotal, numLinksPerWord, usePhraseSearch)
   linkWeights = [(link, tfidfLink(words, link, linkDict, numLinksPerWord, numLinksTotal, wordFreqPerLink[link], maxWordFreqPerLink[link], usePhraseSearch), pageRankWeight) for (link, (pageRankWeight, _)) in linkDict.items()]
   return queryWeights, linkWeights

# Rank the links based on similarity to the search query
def rankLinks(queryWeights, linkWeightsList, usePageRank, useCosineSimilarity):
   # If PageRank is enabled, rank the links based on the harmonic mean between
   # the PageRank score and the cosine similarity of the tfidf score to the query
   if usePageRank == True:
      # If there is only one word, use the distance between the values instead of cosine similarity
      # because cosine similarity will always return 1.0 in this case
      if len(queryWeights) == 1:
         linkSimilarityScores = [(link, abs(queryWeights[0] - linkWeights[0]), float(pageRankWeight)) for (link, linkWeights, pageRankWeight) in linkWeightsList]
         maxScore = max([score[1] for score in linkSimilarityScores])
         linkSimilarityScores = [(link, harmonicMean(1 - score / maxScore, pow(pageRankWeight, 1/3))) for link, score, pageRankWeight in linkSimilarityScores]
      else:
         if useCosineSimilarity:
            linkSimilarityScores = [(link, cosineSimilarity(queryWeights, linkWeights), float(pageRankWeight)) for (link, linkWeights, pageRankWeight) in linkWeightsList]
            maxScore = max([score[1] for score in linkSimilarityScores])
            linkSimilarityScores = [(link, harmonicMean(score / maxScore, pow(pageRankWeight, 1/3))) for link, score, pageRankWeight in linkSimilarityScores]
         else:
            linkSimilarityScores = [(link, euclideanDistance(queryWeights, linkWeights), float(pageRankWeight)) for (link, linkWeights, pageRankWeight) in linkWeightsList]
            maxScore = max([score[1] for score in linkSimilarityScores])
            linkSimilarityScores = [(link, harmonicMean(1 - score / maxScore, pow(pageRankWeight, 1/3))) for link, score, pageRankWeight in linkSimilarityScores]

   # Otherwise, rank the links based on the cosine similarity of the tfidf score to the query
   else:
      # If there is only one word, use the distance between the values instead of cosine similarity
      # because cosine similarity will always return 1.0 in this case
      if len(queryWeights) == 1:
         linkSimilarityScores = [(link, abs(queryWeights[0] - linkWeights[0])) for (link, linkWeights, pageRankWeight) in linkWeightsList]
         maxScore = max([score[1] for score in linkSimilarityScores])
         linkSimilarityScores = [(link, 1 - score / maxScore) for link, score in linkSimilarityScores]
      else:
         if useCosineSimilarity:
            linkSimilarityScores = [(link, cosineSimilarity(queryWeights, linkWeights)) for (link, linkWeights, pageRankWeight) in linkWeightsList]
            maxScore = max([score[1] for score in linkSimilarityScores])
            linkSimilarityScores = [(link, score / maxScore) for link, score in linkSimilarityScores]
         else:
            linkSimilarityScores = [(link, euclideanDistance(queryWeights, linkWeights)) for (link, linkWeights, pageRankWeight) in linkWeightsList]
            maxScore = max([score[1] for score in linkSimilarityScores])
            linkSimilarityScores = [(link, 1 - score / maxScore) for link, score in linkSimilarityScores]

   # print("Similarity Scores:")
   # for score in linkSimilarityScores:
   #    print(score)

   # First sort the results by link length (shorter links tend to be better)
   sortedScores = sorted(linkSimilarityScores, key=lambda entry: len(entry[0]))
   
   # Return the links sorted by similarity score (best first)
   sortedScores = sorted(sortedScores, key=lambda entry: (int)(1000000*entry[1]), reverse=True)
   return sortedScores

# Find the top n relevant links for a given search query
def findRelevantLinks(query, n, usePageRank, usePhraseSearch = True, useCosineSimilarity = False):
   usePageRank = not (usePageRank == "false" or usePageRank == "False" or usePageRank == False)

   # Extract the words from the query string
   words = wordsFromQuery(query.strip().lower())

   # Get the links that contain at least one of the query terms
   linkDict = linksForQuery(words)
   links = []

   # print("Use PageRank:", usePageRank)
   # print("Link Dict:")
   # for link in linkDict.keys():
   #    print(link, linkDict[link])
   # print()

   # Check if any links exist
   if len(linkDict) > 0:
      # Perform TF-IDF to get the weights for each link
      queryWeights, linkWeightsList = tfidf(words, linkDict, usePhraseSearch)

      # print("QueryWeights:", queryWeights)
      # print("LinkWeights:")
      # for link in linkWeightsList:
      #    print(link)

      # Rank the links based on similarity to the search query
      links = rankLinks(queryWeights, linkWeightsList, usePageRank, useCosineSimilarity)

   # Return the top n links
   # print()
   # print("Finals Links:")
   # for link in links[:n]:
   #    print(link)
   return [link[0] for link in links[:n]]

def test():
   db.init_db()
   cProfile.run('findRelevantLinks("aaron keen", 10, True)')

   # db.init_db()
   # query1 = "This is a possible search query"
   # query2 = "\"What about this query?\""

   # # Verify necessary db methods don't crash
   # db.getLinks(["test", "words"])
   # numDBLinks = db.getNumLinks()
   # db.getNumLinks("testing")
   # db.getFreq("word", "link.com")
   # db.getMaxFreq("link.com")

   # print("Query 1: {0}".format(query1))
   # words1 = wordsFromQuery(query1)
   # print(words1)
   # numLinksPerWord1 = db.getNumLinks(words1)
   # query1Weights = tf_idf_query(words1, numDBLinks, numLinksPerWord1)
   # print("Query1 Weights: {0}".format(query1Weights))
   # links1 = findRelevantLinks(query1, 10)
   # print("Links 1: {0}".format(links1))

   # print()
   # print("Query 2: {0}".format(query2))
   # words2 = wordsFromQuery(query2)
   # print(words2)
   # numLinksPerWord2 = db.getNumLinks(words2)
   # query2Weights = tf_idf_query(words2, numDBLinks, numLinksPerWord1)
   # print("Query2 Weights: {0}".format(query2Weights))
   # links2 = findRelevantLinks(query2, 10)
   # print("Links 2: {0}".format(links2))   

if __name__ == "__main__":
   test()
