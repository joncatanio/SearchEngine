import pymysql

from database.src.db_connection import * # Database connection
from database.src.update_tables import * # Updating functions
from database.src.query_tables import *  # Querying functions

def init_db():
   init_connection()
