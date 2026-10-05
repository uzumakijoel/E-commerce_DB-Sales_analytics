import mysql.connector
import sys
from mysql.connector import Error
from contextlib import contextmanager

@contextmanager
def db_connection(host,user,password,database):
    conn = None

    try:
        conn= mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Database connection established.")
        yield conn
    except Error as e:
        print(f"Database connexion error : {e}")
        sys.exit(1)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print("Database connection closed.")