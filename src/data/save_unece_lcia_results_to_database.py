import sqlalchemy
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

import logging
import sys

from src.extract.unece_to_df import load_unece_lcia_data

logger = logging.getLogger('data_loader')
logger.addHandler(logging.FileHandler('data_loader.log'))

def my_handler(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))

sys.excepthook = my_handler

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
    #
    # conn = engine.connect()
    version_as_df = pd.read_sql('SELECT version();',conn)
    print(conn)

    conn.close()


def load_and_save_impact_data():
    logger = logging.Logger('unece_loader.log')

    # Load LCIA result data from table from UNECE report
    # Note you must have the cleaned data table in the data/processed folder
    unece_data = load_unece_lcia_data()

    # Connect to postgres database
    engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL.create(
        drivername='postgresql',
        host=HOST,
        database=DB_NAME,
        username=USER,
        password=PASSWORD
    ))

    # Tranform data for loading into ElectricityGenerationTypes table
    elec_generation_types = unece_data[['Type']].drop_duplicates()
    elec_generation_types = elec_generation_types.rename({'Type': 'Name'}, axis=1)
    elec_generation_subtypes = unece_data[['Subtype']].drop_duplicates()
    elec_generation_subtypes = elec_generation_subtypes.rename({'Subtype': 'Name'}, axis=1)

    logger.info(f'There are {len(elec_generation_types)+len(elec_generation_subtypes)} electricity generation types to store')
    # Clear any existing ElectricityGenerationTypes from ElectricityGenerationTypes table
    # with engine.connect() as connection:
        # deletion_result = connection.execute(
        #     sqlalchemy.text(f'DELETE FROM public."ElectricityGenerationTypes"')
        # )
        # connection.commit()
        # print(f'{deletion_result.rowcount} rows deleted')

    elec_generation_types.to_sql(name='ElectricityGenerationTypes',con=engine,if_exists='append',index=False)
    elec_generation_subtypes.to_sql(name='ElectricityGenerationTypes', con=engine, if_exists='append', index=False)

    # Transform data for loading into the ImpactCategories table
    impact_categories = unece_data.columns.drop(['Type','Subtype']).drop_duplicates()
    impact_categories = pd.DataFrame(impact_categories,columns=['Name'])
    impact_categories['Unit'] = impact_categories['Name'].str.extract(r'\[([0-9a-zA-Z .?]{1,10})\]')
    logger.info(f'There are {len(impact_categories)} impact categories to store')

    # Clear any existing impact categories from ImpactCategories table
    with engine.connect() as connection:
        deletion_result = connection.execute(
            sqlalchemy.text(f'DELETE FROM public."ImpactCategories"')
        )
        connection.commit()
        print(f'{deletion_result.rowcount} rows deleted')

    impact_categories.to_sql(name='ImpactCategories',con=engine,if_exists='append',index=False)

    # get impact category table (so that have keys to use)
    actual_impact_categories_df = pd.read_sql('SELECT * FROM public."ImpactCategories"', con=engine)
    # Create a fact table for StoredLCIAResults
    # TODO
    impact_categories.join(actual_impact_categories_df, left_on='ImpactCategoryName')

if __name__ ==  '__main__':
    load_and_save_impact_data()