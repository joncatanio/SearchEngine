import db_connection
from pymysql import MySQLError

# Return a list of links that contain at least one word in the given 
# list of words
def getLinks(words):
   try:
      with db_connection.connection.cursor() as cur:
         formatTuple = ','.join(['%s'] * len(words))
         sql = '''
            SELECT link FROM Links WHERE id IN 
               (SELECT DISTINCT linkId FROM WordMeta WHERE wordId IN 
                  (SELECT id FROM Words WHERE word IN (%s)));
         ''' % formatTuple
         
         cur.execute(sql, tuple(words))

         # Return all the matching links
         return [entry["link"] for entry in cur.fetchall()]

   except MySQLError as err:
      print(err)

# Return the total number of links in the database
def getNumLinks(word):
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''SELECT COUNT(*) FROM Links;'''
         if word:
            sql = '''
               SELECT COUNT(DISTINCT linkId) FROM WordMeta 
               WHERE 
                  wordId=(SELECT id FROM Words WHERE word=%s);
            '''

         cur.execute(sql, word)

         results = cur.fetchall()
         if results and results:
            return results[0]["COUNT(DISTINCT linkId)"]
         return 0

   except MySQLError as err:
      print(err)

# Return the frequency of a given word for a given link
def getFreq(word, link):
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''
            SELECT COUNT(*) FROM WordMeta WHERE 
               wordId=(SELECT id FROM Words WHERE word=%s) AND 
               linkId=(SELECT id FROM Links WHERE link=%s);
         '''

         cur.execute(sql, (word, link))

         results = cur.fetchall()
         if results and results:
            return results[0]["COUNT(*)"]
         return 0

   except MySQLError as err:
      print(err)

# Return the maximum frequency achieved by any word associated with
# a given link
def getMaxFreq(link):
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''
            SELECT wordId, COUNT(*) AS FreqCount FROM WordMeta 
            WHERE 
               linkId=(SELECT id FROM Links WHERE link=%s) 
            GROUP BY wordId 
            ORDER BY FreqCount DESC;
         '''

         cur.execute(sql, link)

         results = cur.fetchall()
         if results and results:
            return results[0]["COUNT(*)"]
         return 0

   except MySQLError as err:
      print(err)
