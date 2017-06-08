import searchengine.database.db_connection as db_connection
from pymysql import MySQLError

# Return a list of links that contain at least one word in the given
# list of words
def getLinks(words):
   try:
      with db_connection.connection.cursor() as cur:
         formatTuple = ','.join(['%s'] * len(words))
         sql = '''
            SELECT link, pageRank FROM Links WHERE id IN
               (SELECT DISTINCT linkId FROM WordMeta WHERE wordId IN
                  (SELECT id FROM Words WHERE word IN (%s)));
         ''' % formatTuple

         cur.execute(sql, tuple(words))

         # Return all the matching links
         return [(entry["link"], entry["pageRank"]) for entry in cur.fetchall()]

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
               FROM
                  Words AS W
                  INNER JOIN WordMeta AS WM ON W.id = WM.wordId
               WHERE
                  word IN (''' + param_string + ''')
               GROUP BY id, word
            '''

         if words:
            cur.execute(sql, tuple(words))
            results = cur.fetchall()

            numLinks = {}
            for result in results:
               numLinks[result['word']] = result['numLinks']

            # Ensure that all words will be in output dictionary
            [numLinks.update({w:0}) for w in words if w not in numLinks]
         else:
            cur.execute(sql)
            result = cur.fetchone()
            numLinks = int(result['numLinks']) if result else 0

         return numLinks
   except MySQLError as err:
      print(err)

# Return the frequency of a given word for a given link
# {link: {word: frequency}}
def getFreq(words, links):
   try:
      with db_connection.connection.cursor() as cur:
         link_params = ','.join(['%s'] * len(links))
         word_params = ','.join(['%s'] * len(words))

         sql = '''
            SELECT
               link,
               word,
               COUNT(*) AS freq
            FROM
               WordMeta AS WM
               INNER JOIN Words AS W ON WM.wordId = W.id
               INNER JOIN Links AS L ON WM.linkId = L.id
            WHERE
               link IN (''' + link_params + ''')
               AND word IN (''' + word_params + ''')
            GROUP BY
               link,
               word
         '''

         cur.execute(sql, links + words)

         records = cur.fetchall()
         freq_dict = {}
         for record in records:
            # record = {'link': str, 'word': str, 'frequency': num}
            if record['link'] in freq_dict:
               freq_dict[record['link']].update({record['word']:record['freq']})
            else:
               freq_dict[record['link']] = {record['word']:record['freq']}

         return freq_dict
   except MySQLError as err:
      print(err)

# Return the maximum frequency achieved by any word associated with
# a given link
def getMaxFreq(links):
   try:
      with db_connection.connection.cursor() as cur:
         formatTuple = ','.join(['%s'] * len(links))
         sql = '''
            SELECT link, linkId, MAX(FreqCount) as Freq FROM
               (SELECT wordId, linkId, COUNT(*) as FreqCount FROM WordMeta
               WHERE
                  linkId IN (SELECT id FROM Links WHERE link IN (%s))
               GROUP BY wordId, linkId) as newTable
               INNER JOIN Links as L ON L.id = newTable.linkId
            GROUP BY linkId;
         ''' % formatTuple

         cur.execute(sql, links)

         results = cur.fetchall()
         if results:
            return {result["link"]:result["Freq"] for result in results}
         return None#{link:0 for link in links}

   except MySQLError as err:
      print(err)

# Returns a dictionary for links and their inlinks.
# If the links parameter is empty is will fetch all links
def getInlinks(links=None):
   try:
      with db_connection.connection.cursor() as cur:
         if links:
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
         else:
            sql = '''
               SELECT
                  BASE.link AS baselink,
                  INLINK.link AS inlink
               FROM
                  Hyperlinks AS H
                  INNER JOIN Links AS INLINK ON H.baselink = INLINK.id
                  RIGHT JOIN Links AS BASE ON H.hyperlink = BASE.id
            '''

            cur.execute(sql)

         records = cur.fetchall()
         inlinks = {}
         for record in records:
            if record['baselink'] in inlinks:
               inlinks[record['baselink']].append(record['inlink'])
            else:
               inlinks[record['baselink']] = [record['inlink']]

         if links:
            # Ensure that all links given will be in output dictionary
            [inlinks.update({l:[]}) for l in links if l not in inlinks]

         return inlinks

   except MySQLError as err:
      print(err)

# Returns a dictionary of links and the number of outlinks they contain.
# If the links parameter is empty is will fetch all links
def getNumOutlinks(links=None):
   try:
      with db_connection.connection.cursor() as cur:
         if links:
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
         else:
            sql = '''
               SELECT
                  L.link as baselink,
                  IFNULL(B.numOutlinks, 0) AS numOutlinks
               FROM
                  Links AS L
                  LEFT JOIN (
                     SELECT
                        id AS linkId,
                        link AS baselink,
                        COUNT(*) AS numOutlinks
                     FROM
                        Links AS L
                        INNER JOIN Hyperlinks AS H ON L.id = H.baselink
                     GROUP BY
                        L.id,
                        L.link
                  ) AS B ON L.id = B.linkId
            '''

            cur.execute(sql)

         records = cur.fetchall()
         numOutlinks = {}
         for record in records:
            numOutlinks[record['baselink']] = int(record['numOutlinks'])

         if links:
            # Ensure that all links will be in output dictionary
            [numOutlinks.update({l:0}) for l in links if l not in numOutlinks]

         return numOutlinks

   except MySQLError as err:
      print(err)
