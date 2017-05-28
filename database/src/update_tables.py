import db_connection
from pymysql import MySQLError

# Creates a temporary WordMeta and Hyperlinks table. This is required due to
# linking words and links to outdated pages. We simply populate an new tables
# and when `finish_crawl_transaction` is called we truncate the production
# tables and add the new information stoed in the temporary tables This allows
# users to query our search engine while we crawl.
def start_crawl_transaction():
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''
            CREATE TEMPORARY TABLE WordMetaTemp (
               wordId   INT UNSIGNED REFERENCES Words(id),
               linkId   INT UNSIGNED REFERENCES Links(id),
               position INT UNSIGNED NOT NULL
            );

            CREATE TEMPORARY TABLE HyperlinksTemp (
               baselink  INT UNSIGNED REFERENCES Links(id),
               hyperlink INT UNSIGNED REFERENCES Links(id)
            );
         '''

         cur.execute(sql)
   except MySQLError as err:
      print(err)

# Finishes the entire crawl transaction moving newly found data into the
# WordMeta table and deleting the temporary WordMetaTemp table until next crawl.
def finish_crawl_transaction():
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''
            TRUNCATE TABLE WordMeta;
            INSERT INTO WordMeta SELECT * FROM WordMetaTemp;
            DROP TABLE WordMetaTemp;

            TRUNCATE TABLE Hyperlinks;
            INSERT INTO Hyperlinks SELECT * FROM HyperlinksTemp;
            DROP TABLE HyperlinksTemp;
         '''

         cur.execute(sql)

      # Commit all crawl transactions
      db_connection.connection.commit()
   except MySQLError as err:
      print(err)

# Adds the baselink if necessary
def _addBaseLink(baselink):
   try:
      with db_connection.connection.cursor() as cur:
         sql = '''
            INSERT INTO Links
               (link)
            VALUES
               (%s)
            ON DUPLICATE KEY UPDATE link=VALUES(link)
         '''

         cur.execute(sql, baselink)
   except MySQLError as err:
      print(err)

# Inserts words into the Words and WordMetaTemp table, allows for batching each
# page. This can be extended to take in a map if necessary for further batching.
#    baselink - link of the page currently visiting
#    words    - a list of tuples (word, position_in_text)
def addWords(baselink, words):
   try:
      _addBaseLink(baselink)

      # Insert the new words into the Words table
      with db_connection.connection.cursor() as cur:
         sql = '''
            INSERT INTO Words
               (word)
            VALUES
         '''

         for word in words:
            sql += '(%s),'

         # Remove trailing comma and update duplicates as appropriate
         if words:
            sql = sql[:-1] + ' ON DUPLICATE KEY UPDATE word=VALUES(word)'

         word_lst = [word[0] for word in words]
         cur.execute(sql, word_lst)

      # Insert the word information into the WordMetaTemp table
      # This will probably be slow I didn't know how to batch this
      with db_connection.connection.cursor() as cur:
         for word in words:
            sql = '''
               INSERT INTO WordMetaTemp
                  (wordId, linkId, position)
               SELECT * FROM
                  (SELECT id FROM Words WHERE word = %s) AS W
                  JOIN (SELECT id FROM Links WHERE link = %s) AS L
                  JOIN (SELECT %s) AS P
            '''

            cur.execute(sql, [word[0], baselink, word[1]])
   except MySQLError as err:
      print(err)

# Inserts links into the Links table, allows for batching each page. This can
# be extended to take in a map if necessary for further batching.
#    baselink - the link of the current page that links are being added from
#    links    - a list of links linked from baselink
def addLinks(baselink, links):
   try:
      _addBaseLink(baselink)

      with db_connection.connection.cursor() as cur:
         sql = '''
            INSERT INTO Links
               (link)
            VALUES
         '''

         for link in links:
            sql += '(%s),'

         # Remove trailing comma and update duplicates as appropriate
         if links:
            sql = sql[:-1] + ' ON DUPLICATE KEY UPDATE link=VALUES(link)'

         cur.execute(sql, links)

      with db_connection.connection.cursor() as cur:
         for link in links:
            sql = '''
               INSERT INTO HyperlinksTemp
                  (baselink, hyperlink)
               SELECT * FROM
                  (SELECT id FROM Links WHERE link = %s) AS B
                  JOIN (SELECT id FROM Links WHERE link = %s) AS H
            '''

            cur.execute(sql, [baselink, link])
   except MySQLError as err:
      print(err)
