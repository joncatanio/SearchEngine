import pymysql

def init_connection():
   global connection
   connection = pymysql.connect(host='localhost',
                                user='searchEngineUser',
                                password='search_engine_pw',
                                db='SearchEngineDB',
                                cursorclass=pymysql.cursors.DictCursor,
                                charset='utf8')
