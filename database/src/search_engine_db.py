import pymysql

from db_connection import * # Database connection
from update_tables import * # Updating functions
from query_tables import *  # Querying functions

def init_db():
   init_connection()
