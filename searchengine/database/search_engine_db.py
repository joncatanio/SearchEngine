import pymysql

from searchengine.database.db_connection import * # Database connection
from searchengine.database.update_tables import * # Updating functions
from searchengine.database.query_tables import *  # Querying functions

def init_db():
   init_connection()
