import sqlalchemy
from dotenv import load_dotenv,find_dotenv
import os
import psycopg2
import pandas as pd
load_dotenv()

HOST = os.getenv('ELEC_LCA_HOST')
DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
USER = os.getenv('ELEC_LCA_USER')
PASSWORD = os.getenv('ELEC_LCA_PASSWORD')

def connect_elec_lca_db():
    print(HOST,DB_NAME,USER,PASSWORD)
    conn = psycopg2.connect(host=HOST, dbname=DB_NAME, user=USER, password=PASSWORD)

    # engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL.create(
    #     drivername='postgresql',
    #     host=HOST,
    #     database=DB_NAME,
    #     username=USER,
    #     password=PASSWORD
    # ))

    conn = engine.connect()

    print(conn)

    conn.close()


if __name__ ==  '__main__':
    connect_elec_lca_db()