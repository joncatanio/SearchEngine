import searchengine.database.db_connection as db_connection
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

# Return the total number of links in the database or the number of links
# which contain the given words
def getNumLinks(words = None):
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''SELECT COUNT(*) AS numLinks FROM Links;'''
         if words:
            param_string = ','.join(['%s'] * len(words))

            sql = '''
               SELECT
                  id,
                  word,
                  COUNT(DISTINCT linkId) AS numLinks
               FROM (
                     SELECT id, word
                     FROM Words
                     WHERE
                        word IN (''' + param_string + ''')
                  ) AS W
                  INNER JOIN WordMeta AS WM ON W.id = WM.wordId
               GROUP BY id
            '''

         cur.execute(sql, words)
         if words:
            results = cur.fetchall()

            numLinks = {}
            for result in results:
               numLinks[result['word']] = result['numLinks']

            # Ensure that all words will be in output dictionary
            [numLinks.update({w:0}) for w in words if w not in numLinks]
         else:
            result = cur.fetchone()
            numLinks = int(result['numLinks']) if result else 0

         return numLinks
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

         cur.execute(sql, [link])

         results = cur.fetchall()
         if results and results:
            return results[0]["FreqCount"]
         return 0

   except MySQLError as err:
      print(err)

# Returns a list of links that link the parameter `link`
def getInlinks(links):
   try:
      if not links:
         return {}

      with db_connection.connection.cursor() as cur:
         param_string = ','.join(['%s'] * len(links))

         sql = '''
            SELECT
               BASE.link AS baselink,
               INLINK.link AS inlink
            FROM
               Hyperlinks AS H
               INNER JOIN Links AS BASE ON H.hyperlink = BASE.id
               INNER JOIN Links AS INLINK ON H.baselink = INLINK.id
            WHERE
               BASE.link IN (''' + param_string + ''')'''

         cur.execute(sql, links)
         records = cur.fetchall()

         inlinks = {}
         for record in records:
            if record['baselink'] in inlinks:
               inlinks[record['baselink']].append(record['inlink'])
            else:
               inlinks[record['baselink']] = [record['inlink']]

         # Ensure that all links will be in output dictionary
         [inlinks.update({l:[]}) for l in links if l not in inlinks]
         return inlinks

   except MySQLError as err:
      print(err)

# Returns the number of outlinks linked from `link`
def getNumOutlinks(links):
   try:
      if not links:
         return {}

      with db_connection.connection.cursor() as cur:
         param_string = ','.join(['%s'] * len(links))

         sql = '''
            SELECT
               link AS baselink,
               COUNT(*) AS numOutlinks
            FROM
               Links AS L
               INNER JOIN Hyperlinks AS H ON L.id = H.baselink
            WHERE
               L.link IN (''' + param_string + ''')
            GROUP BY
               L.link
         '''

         cur.execute(sql, links)
         records = cur.fetchall()
         numOutlinks = {}
         for record in records:
            numOutlinks[record['baselink']] = int(record['numOutlinks'])

         # Ensure that all links will be in output dictionary
         [numOutlinks.update({l:0}) for l in links if l not in numOutlinks]
         return numOutlinks

   except MySQLError as err:
      print(err)