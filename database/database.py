import pymysql

connection = pymysql.connect(host='localhost',
                             user='searchEngineUser',
                             password='search_engine_pw',
                             db='SearchEngine',
                             cursorclass=pymysql.cursors.DictCursor)
