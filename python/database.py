import mysql.connector
from contextlib import contextmanager

@contextmanager
def db_connection(host,user,password,database):
    conn= mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    try:
        print("Database connection established.")
        yield conn
    finally:
        conn.close()
        print("Database connection closed.")