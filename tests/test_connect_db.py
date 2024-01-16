from dotenv import load_dotenv
import psycopg2
import os

def test_can_connect_to_db():
    load_dotenv()

    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')

    conn = None
    try:
        conn = psycopg2.connect(host=HOST, dbname=DB_NAME, user=USER, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        print(f'Succesfully connected to database {DB_NAME} on host {HOST} with user {USER}')
        print(cursor.fetchone()) # Should print the version of the database
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as e:
        raise e
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    assert True